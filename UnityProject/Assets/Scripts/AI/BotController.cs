using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League Autonomous AI Bot Controller (1 Unit = 1 Meter scale).
    /// Implements authentic competitive arcade car-soccer behavior:
    /// - Multi-state machine: KickoffRush, AttackShot, DefendGoal, ReturnToDefense, ClearCorner, SupportMidfield, CollectBoost
    /// - Dynamic team rotation (Striker vs Goalie/Defender vs Back-post Rotation)
    /// - 3 Difficulty Tiers: Easy, Medium, Hard (with backward-compatible Rookie, Pro, AllStar aliases)
    /// - Predictive ball interception and timed directional dodge/flip power strikes
    /// - Boost pad searching, prioritization, and feathering
    /// - Mid-air pitch and roll orientation recovery to land wheels-down
    /// - Upside-down turtle self-righting recovery
    /// - 100% physical driving through CarController inputs (no teleportation, no cheating)
    /// </summary>
    [RequireComponent(typeof(CarController))]
    public class BotController : MonoBehaviour
    {
        public enum BotDifficulty
        {
            Easy = 0,
            Medium = 1,
            Hard = 2,
            Rookie = 0,
            Pro = 1,
            AllStar = 2
        }

        public enum BotState
        {
            KickoffRush,
            AttackShot,
            DefendGoal,
            ReturnToDefense,
            ClearCorner,
            SupportMidfield,
            CollectBoost
        }

        [Header("=== BOT IDENTITY & TEAM ===")]
        public string botName = "Amber Bot";
        public bool isBlueTeam = false;
        public BotDifficulty difficulty = BotDifficulty.Medium;

        [Header("=== STATE MACHINE (READ-ONLY) ===")]
        [SerializeField] private BotState _currentState = BotState.KickoffRush;
        [SerializeField] private bool _isPrimaryAttacker = true;
        [SerializeField] private Vector3 _currentTargetPoint;

        [Header("=== TARGETS & REFERENCES ===")]
        public BallController targetBall;
        public Transform opponentGoalTransform;
        public Transform ownGoalTransform;
        public List<BoostPad> availableBoostPads = new List<BoostPad>();

        [Header("=== REACTION DELAYS & TIMERS ===")]
        public float kickoffReactionDelay = 0.25f;

        private CarController _car;
        private Rigidbody _rb;
        private float _delayTimer = 0f;
        private float _flipCooldown = 0f;
        private float _turtleTimer = 0f;

        public BotState CurrentState => _currentState;
        public bool IsPrimaryAttacker => _isPrimaryAttacker;
        public Vector3 CurrentTargetPoint => _currentTargetPoint;

        private void Awake()
        {
            _car = GetComponent<CarController>();
            _car.isAI = true;
            _rb = GetComponent<Rigidbody>();
        }

        private void Start()
        {
            FindBall();

            if (availableBoostPads.Count == 0)
            {
                availableBoostPads.AddRange(FindObjectsByType<BoostPad>(FindObjectsSortMode.None));
            }

            ResetKickoffTimer();
        }

        public void FindBall()
        {
            if (targetBall == null)
            {
                targetBall = FindFirstObjectByType<BallController>();
            }
        }

        public void ResetKickoffTimer()
        {
            switch (difficulty)
            {
                case BotDifficulty.Easy:   _delayTimer = 0.55f; break;
                case BotDifficulty.Medium: _delayTimer = 0.25f; break;
                case BotDifficulty.Hard:   _delayTimer = 0.08f; break;
            }
            _currentState = BotState.KickoffRush;
        }

        private void FixedUpdate()
        {
            if (targetBall == null)
            {
                FindBall();
                if (targetBall == null) return;
            }
            if (_car == null) return;

            if (_flipCooldown > 0f) _flipCooldown -= Time.fixedDeltaTime;

            // Handle kickoff countdown or reaction delay
            if (_delayTimer > 0f)
            {
                _delayTimer -= Time.fixedDeltaTime;
                _car.aiThrottle = 0f;
                _car.aiSteer = 0f;
                _car.aiBoost = false;
                _car.aiJump = false;
                _car.aiHandbrake = false;
                _car.aiPitch = 0f;
                _car.aiRoll = 0f;
                _car.aiYaw = 0f;
                return;
            }

            // Check if car is upside-down on the ground (Turtle Recovery)
            if (CheckTurtleRecovery())
            {
                return;
            }

            // If airborne, execute mid-air orientation recovery so wheels face ground
            if (!_car.IsGrounded)
            {
                HandleAerialRecovery();
            }
            else
            {
                _car.aiPitch = 0f;
                _car.aiRoll = 0f;
                _car.aiYaw = 0f;
            }

            DetermineTeamRole();
            UpdateStateMachine();
            ExecuteDrivingControls();
        }

        /// <summary>
        /// Self-righting recovery when the car lands on its roof or side.
        /// </summary>
        private bool CheckTurtleRecovery()
        {
            // If car is near ground and roof is pointing downward or sideways
            if (transform.position.y < 1.4f && Vector3.Dot(transform.up, Vector3.up) < 0.25f)
            {
                _turtleTimer += Time.fixedDeltaTime;
                if (_turtleTimer > 0.25f)
                {
                    // Physically jump and roll to flip back onto wheels
                    _car.aiJump = true;
                    _car.aiRoll = 1.0f;
                    _car.aiPitch = -0.5f;
                    _car.aiThrottle = 0.5f;
                    _car.aiSteer = 0f;
                    _car.aiBoost = false;
                    _car.aiHandbrake = false;
                    return true;
                }
            }
            else
            {
                _turtleTimer = 0f;
            }
            return false;
        }

        /// <summary>
        /// Proportional air roll and pitch stabilization to align wheels with the ground normal before touchdown.
        /// </summary>
        private void HandleAerialRecovery()
        {
            // Calculate orientation difference between car's current up and desired landing up (world up or surface normal)
            Vector3 targetUp = Vector3.up;
            if (Physics.Raycast(transform.position, -Vector3.up, out RaycastHit hit, 6f, _car.groundLayer))
            {
                targetUp = hit.normal;
            }

            Vector3 localTargetUp = transform.InverseTransformDirection(targetUp);

            // Pitch error: localTargetUp.z > 0 means nose is down, < 0 means nose is up
            float pitchErr = -localTargetUp.z;
            // Roll error: localTargetUp.x > 0 means tilted right, < 0 means tilted left
            float rollErr = localTargetUp.x;

            float recoveryGain = (difficulty == BotDifficulty.Hard) ? 3.5f : ((difficulty == BotDifficulty.Medium) ? 2.5f : 1.2f);

            _car.aiPitch = Mathf.Clamp(pitchErr * recoveryGain, -1f, 1f);
            _car.aiRoll = Mathf.Clamp(rollErr * recoveryGain, -1f, 1f);
            _car.aiYaw = 0f;
        }

        private void DetermineTeamRole()
        {
            BotController[] allBots = FindObjectsByType<BotController>(FindObjectsSortMode.None);
            float myDist = Vector3.Distance(transform.position, targetBall.transform.position);

            _isPrimaryAttacker = true;
            foreach (var b in allBots)
            {
                if (b != this && b.isBlueTeam == isBlueTeam)
                {
                    float otherDist = Vector3.Distance(b.transform.position, targetBall.transform.position);
                    if (otherDist < myDist - 1.2f)
                    {
                        _isPrimaryAttacker = false;
                        break;
                    }
                }
            }
        }

        private void UpdateStateMachine()
        {
            Vector3 ballPos = targetBall.transform.position;
            Vector3 ballVel = targetBall.Rb != null ? targetBall.Rb.linearVelocity : Vector3.zero;

            float fwdSign = isBlueTeam ? 1f : -1f;
            Vector3 ownGoalPos = ownGoalTransform != null ? ownGoalTransform.position : new Vector3(isBlueTeam ? -50f : 50f, 2.5f, 0f);
            Vector3 oppGoalPos = opponentGoalTransform != null ? opponentGoalTransform.position : new Vector3(isBlueTeam ? 50f : -50f, 2.5f, 0f);

            // Lead prediction based on difficulty
            float leadTime = 0f;
            if (difficulty == BotDifficulty.Hard) leadTime = 0.42f;
            else if (difficulty == BotDifficulty.Medium) leadTime = 0.22f;

            Vector3 predBall = ballPos + ballVel * leadTime;
            if (difficulty == BotDifficulty.Hard && Mathf.Abs(ballVel.y) > 1.5f)
            {
                // Ballistic vertical gravity lead
                predBall.y += 0.5f * Physics.gravity.y * (leadTime * leadTime);
            }
            predBall.x = Mathf.Clamp(predBall.x, -46f, 46f);
            predBall.z = Mathf.Clamp(predBall.z, -36f, 36f);
            predBall.y = Mathf.Max(predBall.y, 0.8f);

            bool isKickoffBall = Mathf.Abs(ballPos.x) < 2.5f && Mathf.Abs(ballPos.z) < 2.5f && ballVel.magnitude < 3f;
            bool isCorner = Mathf.Abs(ballPos.x) > 33f && Mathf.Abs(ballPos.z) > 24f;

            // Distance along the field from bot to ball (positive = ball is ahead in front of bot)
            float toBallDistAlongField = (ballPos.x - transform.position.x) * fwdSign;
            bool isBehindBall = toBallDistAlongField < -2.5f;

            // STATE TRANSITION LOGIC
            if (isKickoffBall)
            {
                _currentState = _isPrimaryAttacker ? BotState.KickoffRush : BotState.DefendGoal;
            }
            else if (isBehindBall && Vector3.Distance(ballPos, ownGoalPos) < 35f && difficulty != BotDifficulty.Easy)
            {
                // Ball has passed bot towards own net: Rotate back along flank
                _currentState = BotState.ReturnToDefense;
            }
            else if (isCorner && _isPrimaryAttacker)
            {
                _currentState = BotState.ClearCorner;
            }
            else if (Vector3.Dot(ballPos - ownGoalPos, Vector3.forward * fwdSign) < 20f)
            {
                // Ball deep in own defensive half
                _currentState = _isPrimaryAttacker ? BotState.AttackShot : BotState.DefendGoal;
            }
            else
            {
                // Ball in midfield or opponent half
                if (_isPrimaryAttacker)
                {
                    _currentState = BotState.AttackShot;
                }
                else if (_car.CurrentBoost < (difficulty == BotDifficulty.Hard ? 25f : 35f))
                {
                    _currentState = BotState.CollectBoost;
                }
                else
                {
                    _currentState = BotState.SupportMidfield;
                }
            }

            // TARGET POINT COMPUTATION
            switch (_currentState)
            {
                case BotState.KickoffRush:
                    _currentTargetPoint = new Vector3(0f, 0.8f, 0f);
                    break;

                case BotState.ClearCorner:
                    float signX = Mathf.Sign(ballPos.x);
                    float signZ = Mathf.Sign(ballPos.z);
                    _currentTargetPoint = new Vector3(ballPos.x - signX * 1.8f, 0.8f, ballPos.z - signZ * 1.8f);
                    break;

                case BotState.AttackShot:
                    // Choose shot aim spot on opponent goal (aim for corners on Hard)
                    Vector3 aimTarget = oppGoalPos;
                    if (difficulty == BotDifficulty.Hard)
                    {
                        // Aim for the post furthest from player or goalie
                        float cornerOffsetZ = (transform.position.z > 0f) ? -5.5f : 5.5f;
                        aimTarget.z += cornerOffsetZ;
                    }

                    Vector3 shotDir = (predBall - aimTarget).normalized;
                    Vector3 strikeSpot = predBall + shotDir * 2.1f;

                    // If caught ahead of ball, swing wide to flank behind it
                    if (toBallDistAlongField < -1.5f)
                    {
                        float flankZ = transform.position.z > predBall.z ? 8.5f : -8.5f;
                        _currentTargetPoint = new Vector3(predBall.x - fwdSign * 7.5f, 0.8f, predBall.z + flankZ);
                    }
                    else
                    {
                        _currentTargetPoint = strikeSpot;
                    }
                    break;

                case BotState.ReturnToDefense:
                    // Retreat down the outer flank and enter goal through back post
                    float backPostZ = (ballPos.z > 0f) ? -6.5f : 6.5f;
                    float flankRetreatZ = (ballPos.z > 0f) ? -22f : 22f;

                    // If still far upfield, path along defensive flank through boost pads
                    if (Mathf.Abs(transform.position.x - ownGoalPos.x) > 20f)
                    {
                        _currentTargetPoint = new Vector3(ownGoalPos.x + fwdSign * 18f, 0.8f, flankRetreatZ);
                    }
                    else
                    {
                        // Enter goal through back post
                        _currentTargetPoint = new Vector3(ownGoalPos.x + fwdSign * 5.0f, 0.8f, backPostZ);
                    }
                    break;

                case BotState.DefendGoal:
                    float mouthZ = Mathf.Clamp(ballPos.z * 0.5f, -6.5f, 6.5f);
                    _currentTargetPoint = new Vector3(ownGoalPos.x + fwdSign * 6.0f, 0.8f, mouthZ);

                    // Emergency save charge if ball is on target for own goal
                    float dGoal = Vector3.Distance(ballPos, ownGoalPos);
                    if (dGoal < 22f && (Vector3.Distance(transform.position, ballPos) < 16f || ballVel.x * fwdSign < -1.5f))
                    {
                        _currentTargetPoint = predBall;
                    }
                    break;

                case BotState.SupportMidfield:
                    float midZ = Mathf.Clamp(ballPos.z * 0.5f, -18f, 18f);
                    _currentTargetPoint = new Vector3(fwdSign * -8f, 0.8f, midZ);
                    break;

                case BotState.CollectBoost:
                    BoostPad bestPad = null;
                    float bestScore = float.MaxValue;
                    foreach (var pad in availableBoostPads)
                    {
                        if (pad != null && pad.IsActive)
                        {
                            float d = Vector3.Distance(transform.position, pad.transform.position);
                            // Prioritize large 100-orbs on Hard or when far
                            float weight = (pad.isFullBoost && difficulty != BotDifficulty.Easy) ? d * 0.55f : d;
                            if (weight < bestScore)
                            {
                                bestScore = weight;
                                bestPad = pad;
                            }
                        }
                    }
                    if (bestPad != null) _currentTargetPoint = bestPad.transform.position;
                    else _currentTargetPoint = new Vector3(fwdSign * -8f, 0.8f, 0f);
                    break;
            }
        }

        private void ExecuteDrivingControls()
        {
            Vector3 toTarget = _currentTargetPoint - transform.position;
            toTarget.y = 0f;
            float dist = toTarget.magnitude;

            Vector3 localTarget = transform.InverseTransformPoint(_currentTargetPoint);
            float angleToTarget = Mathf.Atan2(localTarget.x, localTarget.z) * Mathf.Rad2Deg;

            // Steering multiplier based on difficulty
            float steerMult = 1.2f;
            if (difficulty == BotDifficulty.Hard) steerMult = 2.6f;
            else if (difficulty == BotDifficulty.Medium) steerMult = 1.8f;

            _car.aiSteer = Mathf.Clamp(angleToTarget / 45f * steerMult, -1f, 1f);

            // Throttle & Reverse
            if (Mathf.Abs(angleToTarget) > 135f && dist < 8f)
            {
                _car.aiThrottle = -0.8f; // Reverse if target is directly behind at close range
            }
            else
            {
                float turnSpeedReduction = (Mathf.Abs(angleToTarget) > 90f) ? 0.35f : 1.0f;
                // Cap speed on Easy difficulty
                if (difficulty == BotDifficulty.Easy && _rb.linearVelocity.magnitude > 18f)
                {
                    _car.aiThrottle = 0.2f;
                }
                else
                {
                    _car.aiThrottle = turnSpeedReduction;
                }
            }

            // Handbrake for sharp drift turns
            if (difficulty != BotDifficulty.Easy)
            {
                float handbrakeThreshold = (difficulty == BotDifficulty.Hard) ? 75f : 85f;
                _car.aiHandbrake = Mathf.Abs(angleToTarget) > handbrakeThreshold && dist > 6f;
            }
            else
            {
                _car.aiHandbrake = false;
            }

            // Boost usage
            bool aligned = Mathf.Abs(angleToTarget) < (difficulty == BotDifficulty.Hard ? 32f : 24f);
            bool needSpeed = dist > 8f || _currentState == BotState.KickoffRush;

            if (difficulty == BotDifficulty.Easy)
            {
                // Easy bot boosts rarely, only when straight on kickoff with high boost
                _car.aiBoost = (_currentState == BotState.KickoffRush && aligned && _car.CurrentBoost > 50f);
            }
            else if (difficulty == BotDifficulty.Medium)
            {
                _car.aiBoost = aligned && needSpeed && _car.CurrentBoost > 10f;
            }
            else // Hard
            {
                // Aggressive boost feathering; maintain supersonic, boost through challenges
                bool isSupersonic = _rb.linearVelocity.magnitude >= 30f;
                _car.aiBoost = aligned && needSpeed && (!isSupersonic || dist > 14f) && _car.CurrentBoost > 2f;
            }

            // Dodge Flip Attack Strike & Jump Contesting
            if (difficulty != BotDifficulty.Easy && _car.IsGrounded && _flipCooldown <= 0f)
            {
                float ballDist = Vector3.Distance(transform.position, targetBall.transform.position);
                Vector3 toBall = transform.InverseTransformPoint(targetBall.transform.position);
                float ballAngle = Mathf.Atan2(toBall.x, toBall.z) * Mathf.Rad2Deg;

                bool isShooting = _currentState == BotState.AttackShot || _currentState == BotState.KickoffRush;
                bool isEmergencySave = _currentState == BotState.DefendGoal && ballDist < 6.5f;

                if ((isShooting && ballDist < 5.2f && Mathf.Abs(ballAngle) < 24f) || isEmergencySave)
                {
                    _car.aiJump = true;
                    _flipCooldown = (difficulty == BotDifficulty.Hard) ? 1.8f : 2.5f;
                    StartCoroutine(ExecuteTimedDodge(ballAngle));
                }
                else
                {
                    _car.aiJump = false;
                }
            }
            else
            {
                _car.aiJump = false;
            }
        }

        private IEnumerator ExecuteTimedDodge(float ballAngle)
        {
            yield return new WaitForSeconds(0.12f);
            Vector2 dodgeDir = Vector2.up;
            if (difficulty == BotDifficulty.Hard && Mathf.Abs(ballAngle) > 10f)
            {
                // Directional diagonal flip toward ball
                dodgeDir = new Vector2(Mathf.Sign(ballAngle) * 0.4f, 0.9f).normalized;
            }
            _car.ExecuteDodge(dodgeDir);
        }
    }
}
