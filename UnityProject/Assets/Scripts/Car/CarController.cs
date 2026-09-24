using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League Authentic Vehicle Physics Controller (1 Unit = 1 Meter scale).
    /// Configured with exact base physics dimensions:
    /// - Rigidbody Mass: 1500 kg
    /// - Center of Mass: 0.3 m above ground
    /// - Suspension Travel: 0.3 m
    /// - Wheel Radius: 0.4 m (0.8m diameter)
    /// - Ground Clearance: 0.25 m
    /// - Max Ground Speed: 22 m/s
    /// - Max Boost Speed: 35 m/s
    /// - Boost Acceleration: ~25 m/s²
    /// - Jump Force: ~7 m/s upward impulse
    /// - Double Jump: Additional upward impulse
    /// - Configurable Air Control (Pitch, Yaw, Roll)
    /// - Wall driving adhesion downforce
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class CarController : MonoBehaviour
    {
        [Header("=== RIGIDBODY & CENTER OF MASS ===")]
        public float vehicleMass = 1500f;
        public Vector3 centerOfMassOffset = new Vector3(0f, -0.25f, 0f); // 0.3m above ground

        [Header("=== SPEED & ACCELERATION (m/s) ===")]
        [Tooltip("Maximum regular driving speed (22 m/s)")]
        public float maxGroundSpeed = 22f;

        [Tooltip("Maximum boost speed (35 m/s)")]
        public float maxBoostSpeed = 35f;

        [Tooltip("Regular forward driving acceleration")]
        public float driveAcceleration = 14f;

        [Tooltip("Boost acceleration (~25 m/s²)")]
        public float boostAcceleration = 25f;

        [Tooltip("Reverse driving acceleration")]
        public float reverseAcceleration = 11f;

        [Tooltip("Braking deceleration")]
        public float brakeDeceleration = 28f;

        [Tooltip("Steering turn speed on ground")]
        public float steerSpeed = 2.4f;

        [Tooltip("Handbrake turn multiplier for drifting")]
        public float handbrakeTurnMultiplier = 1.8f;

        [Header("=== JUMP & AERIAL ACROBATICS ===")]
        [Tooltip("Jump force (~7 m/s upward)")]
        public float jumpForce = 7f;

        [Tooltip("Double jump additional upward impulse")]
        public float doubleJumpForce = 7f;

        [Tooltip("Dodge/flip forward impulse")]
        public float dodgeImpulse = 12f;

        [Tooltip("Dodge flip duration in seconds")]
        public float dodgeDuration = 0.65f;

        [Tooltip("Configurable air pitch speed")]
        public float airPitchSpeed = 3.5f;

        [Tooltip("Configurable air yaw speed")]
        public float airYawSpeed = 3.0f;

        [Tooltip("Configurable air roll speed")]
        public float airRollSpeed = 4.8f;

        [Header("=== WHEEL CONTACT RAYCASTS ===")]
        public LayerMask groundLayer;
        public float suspensionRestLength = 0.55f;
        public float suspensionTravel = 0.3f;
        public float groundClearance = 0.25f;
        public float springStrength = 45000f;
        public float damperStrength = 3500f;
        public float wheelRadius = 0.4f;

        [Header("=== AI INPUT OVERRIDE ===")]
        public bool isAI = false;
        [Range(-1f, 1f)] public float aiThrottle = 0f;
        [Range(-1f, 1f)] public float aiSteer = 0f;
        public bool aiBoost = false;
        public bool aiJump = false;
        public bool aiHandbrake = false;
        [Range(-1f, 1f)] public float aiPitch = 0f;
        [Range(-1f, 1f)] public float aiYaw = 0f;
        [Range(-1f, 1f)] public float aiRoll = 0f;

        [Tooltip("Wheel anchor transforms (FL, FR, RL, RR)")]
        public Transform[] wheelAnchors = new Transform[4];
        public Transform[] wheelMeshRenderers = new Transform[4];

        [Header("=== BOOST SYSTEM ===")]
        public float currentBoost = 33.3f;
        public float maxBoost = 100f;
        public float boostConsumeRate = 33.3f; // ~3 sec continuous burn
        public ParticleSystem boostParticles;
        public TrailRenderer[] supersonicTrails;

        [Header("=== WALL DRIVING ADHESION ===")]
        public float wallGripForce = 35f;
        public float downforceScale = 14f;

        // Internal physics state
        private Rigidbody _rb;
        private bool _isGrounded;
        private int _wheelsGroundedCount;
        private bool _canDoubleJump;
        private bool _isDodgeFlipping;
        private float _dodgeTimer;
        private Vector3 _dodgeDir;
        private Vector3 _groundNormal = Vector3.up;
        private bool _controlsLocked = false;
        private float _steerAngleVisual;

        public Rigidbody Rb => _rb;
        public bool IsGrounded => _isGrounded;
        public bool IsBoosting { get; private set; }
        public bool IsSupersonic => _rb != null && _rb.linearVelocity.magnitude >= (maxBoostSpeed - 1.5f);
        public float CurrentBoost => currentBoost;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.mass = vehicleMass;
            _rb.linearDamping = 0.06f;
            _rb.angularDamping = 2.4f;
            _rb.centerOfMass = centerOfMassOffset;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

            if (groundLayer.value == 0)
            {
                groundLayer = LayerMask.GetMask("Default", "Ground", "Arena");
            }
        }

        private void Update()
        {
            if (_controlsLocked) return;

            HandleAirDodgeInputs();
            UpdateWheelVisuals();
            UpdateFX();
        }

        private void FixedUpdate()
        {
            if (_controlsLocked) return;

            UpdateSuspension();

            if (_isGrounded)
            {
                ApplyGroundForces();
            }
            else
            {
                ApplyAerialForces();
            }

            ApplyWallAdhesion();
            ApplyBoostPhysics();
        }

        private void UpdateSuspension()
        {
            _wheelsGroundedCount = 0;
            Vector3 accumulatedNormal = Vector3.zero;
            float restDist = groundClearance + wheelRadius;
            float maxRayDist = restDist + suspensionTravel;

            for (int i = 0; i < wheelAnchors.Length; i++)
            {
                if (wheelAnchors[i] == null) continue;

                Ray ray = new Ray(wheelAnchors[i].position, -transform.up);
                RaycastHit[] hits = Physics.RaycastAll(ray, maxRayDist, groundLayer, QueryTriggerInteraction.Ignore);
                RaycastHit validHit = default;
                bool hasHit = false;
                float closestDist = float.MaxValue;

                foreach (var h in hits)
                {
                    if (h.collider != null && h.collider.transform.root != transform.root)
                    {
                        if (h.distance < closestDist)
                        {
                            closestDist = h.distance;
                            validHit = h;
                            hasHit = true;
                        }
                    }
                }

                if (hasHit)
                {
                    RaycastHit hit = validHit;
                    _wheelsGroundedCount++;
                    accumulatedNormal += hit.normal;

                    // Spring compression
                    float currentDist = hit.distance - wheelRadius;
                    float compression = restDist - currentDist;

                    // Spring force: F = k * x
                    float springForce = compression * springStrength;

                    // Damper force: F = -c * v
                    float wheelRelVel = Vector3.Dot(_rb.GetPointVelocity(wheelAnchors[i].position), transform.up);
                    float damperForce = -wheelRelVel * damperStrength;

                    float totalSuspension = Mathf.Max(0f, springForce + damperForce);
                    _rb.AddForceAtPosition(transform.up * totalSuspension, wheelAnchors[i].position);

                    // Lateral tire friction
                    Vector3 lateralDir = wheelAnchors[i].right;
                    float lateralVel = Vector3.Dot(_rb.GetPointVelocity(wheelAnchors[i].position), lateralDir);
                    float gripSlip = (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.Space)) ? 0.72f : 0.94f;
                    _rb.AddForceAtPosition(-lateralDir * lateralVel * vehicleMass * gripSlip * 0.25f, wheelAnchors[i].position);
                }
            }

            _isGrounded = (_wheelsGroundedCount >= 2);
            if (_isGrounded)
            {
                _groundNormal = accumulatedNormal.normalized;
                _canDoubleJump = true;
            }
        }

        private void ApplyGroundForces()
        {
            float throttle = isAI ? aiThrottle : Input.GetAxis("Vertical"); // W / S or Left Stick Y
            
            // Explicit A/D steering: D = turn RIGHT (+1), A = turn LEFT (-1)
            float steer = 0f;
            if (!isAI)
            {
                if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) steer += 1f;
                if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) steer -= 1f;
                if (Mathf.Approximately(steer, 0f)) steer = Input.GetAxis("Horizontal");
            }
            else
            {
                steer = aiSteer;
            }

            bool handbrake = isAI ? aiHandbrake : (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.Space) || Input.GetKey(KeyCode.JoystickButton2) || Input.GetKey(KeyCode.JoystickButton4));

            Vector3 fwd = transform.forward;
            float currentSpeed = Vector3.Dot(_rb.linearVelocity, fwd);

            // Forward Drive
            if (throttle > 0.05f)
            {
                if (currentSpeed < maxGroundSpeed)
                {
                    _rb.AddForce(fwd * (throttle * driveAcceleration * vehicleMass), ForceMode.Force);
                }
            }
            // Reverse / Brake
            else if (throttle < -0.05f)
            {
                if (currentSpeed > 0.5f)
                {
                    // Braking
                    _rb.AddForce(-fwd * (brakeDeceleration * vehicleMass), ForceMode.Force);
                }
                else if (currentSpeed > -maxGroundSpeed * 0.5f)
                {
                    // Reverse
                    _rb.AddForce(fwd * (throttle * reverseAcceleration * vehicleMass), ForceMode.Force);
                }
            }

            // Steering Torque:
            // In Unity PhysX, clockwise rotation around transform.up (turn RIGHT) is -transform.up
            // When steer > 0 (D pressed), apply torque to turn RIGHT.
            // When steer < 0 (A pressed), apply torque to turn LEFT.
            float turnMult = handbrake ? handbrakeTurnMultiplier : 1.0f;
            float speedFactor = Mathf.Clamp(_rb.linearVelocity.magnitude / 6f, 0.45f, 1.25f);
            float reverseMult = (currentSpeed < -0.5f && throttle < -0.05f) ? -1f : 1f;
            float steerTorque = steer * steerSpeed * turnMult * speedFactor * reverseMult;
            _rb.AddTorque(-transform.up * (steerTorque * vehicleMass * 0.85f), ForceMode.Force);

            // Ground Jump
            bool doJump = isAI ? aiJump : (Input.GetKeyDown(KeyCode.Mouse1) || Input.GetKeyDown(KeyCode.J) || Input.GetButtonDown("Jump") || Input.GetKeyDown(KeyCode.JoystickButton0));
            if (doJump)
            {
                _rb.AddForce(transform.up * (jumpForce * vehicleMass), ForceMode.Impulse);
                _isGrounded = false;
            }
        }

        private void ApplyAerialForces()
        {
            // Air Pitch / Yaw / Roll
            float pitch = isAI ? aiPitch : Input.GetAxis("Vertical");
            
            float yaw = 0f;
            if (!isAI)
            {
                if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) yaw += 1f;
                if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) yaw -= 1f;
                if (Mathf.Approximately(yaw, 0f)) yaw = Input.GetAxis("Horizontal");
            }
            else
            {
                yaw = aiYaw;
            }

            float roll = isAI ? aiRoll : 0f;
            if (!isAI)
            {
                if (Input.GetKey(KeyCode.Q) || Input.GetKey(KeyCode.JoystickButton4)) roll -= 1f;
                if (Input.GetKey(KeyCode.E) || Input.GetKey(KeyCode.JoystickButton5)) roll += 1f;
            }

            // In air: D (yaw > 0) yaws RIGHT, A (yaw < 0) yaws LEFT
            Vector3 airTorque = (transform.right * (pitch * airPitchSpeed) +
                                 -transform.up * (yaw * airYawSpeed) +
                                 transform.forward * (-roll * airRollSpeed)) * vehicleMass * 0.35f;

            _rb.AddTorque(airTorque, ForceMode.Force);

            // Double Jump / Dodge
            bool doAirJump = isAI ? aiJump : (Input.GetKeyDown(KeyCode.Mouse1) || Input.GetKeyDown(KeyCode.J) || Input.GetButtonDown("Jump") || Input.GetKeyDown(KeyCode.JoystickButton0));
            if (_canDoubleJump && doAirJump)
            {
                _canDoubleJump = false;

                Vector2 inputDir = isAI ? new Vector2(aiSteer, aiThrottle) : new Vector2(yaw, Input.GetAxisRaw("Vertical"));
                if (inputDir.sqrMagnitude > 0.1f)
                {
                    // Directional Flip/Dodge (D dodges RIGHT, A dodges LEFT)
                    StartCoroutine(PerformDodge(inputDir.normalized));
                }
                else
                {
                    // Straight Upward Double Jump
                    _rb.AddForce(transform.up * (jumpForce * vehicleMass * 0.95f), ForceMode.Impulse);
                }
            }
        }

        public void ExecuteDodge(Vector2 dir)
        {
            if (_canDoubleJump)
            {
                _canDoubleJump = false;
                StartCoroutine(PerformDodge(dir.normalized));
            }
        }

        private IEnumerator PerformDodge(Vector2 dir)
        {
            _isDodgeFlipping = true;
            Vector3 worldDodge = (transform.forward * dir.y + transform.right * dir.x).normalized;

            // Instant impulse in dodge direction
            _rb.AddForce(worldDodge * (dodgeImpulse * vehicleMass), ForceMode.Impulse);

            float elapsed = 0f;
            Vector3 flipAxis = (transform.right * dir.x - transform.forward * dir.y).normalized;

            while (elapsed < dodgeDuration)
            {
                elapsed += Time.fixedDeltaTime;
                _rb.AddTorque(flipAxis * (30f * vehicleMass), ForceMode.Force);
                yield return new WaitForFixedUpdate();
            }

            _isDodgeFlipping = false;
        }

        private void ApplyWallAdhesion()
        {
            if (!_isGrounded) return;

            // Apply sticky downforce towards surface normal when on walls or slopes
            float slopeAngle = Vector3.Angle(_groundNormal, Vector3.up);
            if (slopeAngle > 15f)
            {
                _rb.AddForce(-_groundNormal * (wallGripForce * vehicleMass * Mathf.Clamp01(slopeAngle / 90f)), ForceMode.Force);
            }
            else
            {
                // Standard downforce based on forward speed
                _rb.AddForce(-transform.up * (_rb.linearVelocity.magnitude * downforceScale), ForceMode.Force);
            }
        }

        private void ApplyBoostPhysics()
        {
            bool wantBoost = isAI ? aiBoost : (Input.GetKey(KeyCode.Mouse0) || Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.JoystickButton1) || Input.GetKey(KeyCode.JoystickButton5));
            IsBoosting = wantBoost && (currentBoost > 0f);

            if (IsBoosting)
            {
                currentBoost = Mathf.Max(0f, currentBoost - boostConsumeRate * Time.fixedDeltaTime);

                Vector3 fwd = transform.forward;
                float currentSpeed = Vector3.Dot(_rb.linearVelocity, fwd);

                if (currentSpeed < maxBoostSpeed)
                {
                    _rb.AddForce(fwd * (boostAcceleration * vehicleMass), ForceMode.Force);
                }
            }
        }

        private void HandleAirDodgeInputs()
        {
            // Update steering angle for visual wheel models (D = right, A = left)
            float steer = 0f;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) steer += 1f;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) steer -= 1f;
            if (Mathf.Approximately(steer, 0f)) steer = Input.GetAxis("Horizontal");
            _steerAngleVisual = Mathf.Lerp(_steerAngleVisual, steer * 28f, 15f * Time.deltaTime);
        }

        private void UpdateWheelVisuals()
        {
            for (int i = 0; i < wheelMeshRenderers.Length; i++)
            {
                if (wheelMeshRenderers[i] == null) continue;

                // Turn front wheels visually with steering
                if (i < 2)
                {
                    wheelMeshRenderers[i].localRotation = Quaternion.Euler(0, _steerAngleVisual, 90f);
                }
            }
        }

        private void UpdateFX()
        {
            if (boostParticles != null)
            {
                if (IsBoosting && !boostParticles.isPlaying) boostParticles.Play();
                else if (!IsBoosting && boostParticles.isPlaying) boostParticles.Stop();
            }

            if (supersonicTrails != null)
            {
                bool supersonic = IsSupersonic;
                foreach (var trail in supersonicTrails)
                {
                    if (trail != null) trail.emitting = supersonic;
                }
            }
        }

        public void AddBoost(float amount)
        {
            currentBoost = Mathf.Clamp(currentBoost + amount, 0f, maxBoost);
        }

        public void SetControlsLocked(bool locked)
        {
            _controlsLocked = locked;
            if (locked && _rb != null && !_rb.isKinematic)
            {
                _rb.linearVelocity = Vector3.zero;
                _rb.angularVelocity = Vector3.zero;
            }
        }

        public void ResetVehicle(Vector3 spawnPosition, Quaternion spawnRotation)
        {
            transform.position = spawnPosition;
            transform.rotation = spawnRotation;
            if (_rb != null && !_rb.isKinematic)
            {
                _rb.linearVelocity = Vector3.zero;
                _rb.angularVelocity = Vector3.zero;
            }
            currentBoost = 33.3f;
            _isGrounded = true;
            _canDoubleJump = true;
        }
    }
}
