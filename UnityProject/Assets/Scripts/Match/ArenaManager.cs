using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League Match Manager (1 Unit = 1 Meter scale).
    /// Exact spawn positions:
    /// BLUE TEAM:
    ///   - Player: (-35, 0.8, 0) facing center (+X)
    ///   - Teammate 1: (-30, 0.8, -20) facing center
    ///   - Teammate 2: (-30, 0.8, 20) facing center
    /// ORANGE TEAM:
    ///   - Player: (35, 0.8, 0) facing center (-X)
    ///   - Teammate 1: (30, 0.8, -20) facing center
    ///   - Teammate 2: (30, 0.8, 20) facing center
    /// </summary>
    public class ArenaManager : MonoBehaviour
    {
        public enum MatchState
        {
            Warmup,
            Countdown,
            InPlay,
            GoalCelebration,
            Overtime,
            MatchOver
        }

        [Header("=== MATCH TIMING ===")]
        public float matchDuration = 300f; // 5:00
        public float countdownDuration = 3f;
        public float goalCelebrationDuration = 3.5f;

        [Header("=== GAME OBJECTS ===")]
        public BallController ball;
        public CameraController mainCamera;
        public List<CarController> blueCars = new List<CarController>();
        public List<CarController> orangeCars = new List<CarController>();
        public List<BoostPad> boostPads = new List<BoostPad>();

        [Header("=== SPAWN POSITIONS (1 Unit = 1 Meter) ===")]
        public Vector3 blueSpawnPlayer = new Vector3(-35f, 0.8f, 0f);
        public Vector3 blueSpawnTeammate1 = new Vector3(-30f, 0.8f, -20f);
        public Vector3 blueSpawnTeammate2 = new Vector3(-30f, 0.8f, 20f);

        public Vector3 orangeSpawnPlayer = new Vector3(35f, 0.8f, 0f);
        public Vector3 orangeSpawnTeammate1 = new Vector3(30f, 0.8f, -20f);
        public Vector3 orangeSpawnTeammate2 = new Vector3(30f, 0.8f, 20f);

        [Header("=== GOALS & EXPLOSIONS ===")]
        public Vector3 blueGoalExplosionPos = new Vector3(-50f, 4f, 0f);
        public Vector3 orangeGoalExplosionPos = new Vector3(50f, 4f, 0f);
        public ParticleSystem blueGoalExplosionFx;
        public ParticleSystem orangeGoalExplosionFx;
        public float explosionForce = 75f;
        public float explosionRadius = 55f;

        [Header("=== UI REFERENCES ===")]
        public InGameHUD inGameHUD;
        public Text scoreText;
        public Text timerText;
        public Text announcementText;

        [Header("=== AUDIO ===")]
        public AudioSource audioSource;
        public AudioClip countdownBeep;
        public AudioClip goWhistle;
        public AudioClip goalHorn;
        public AudioClip matchOverBuzzer;

        private MatchState _state = MatchState.Warmup;
        private float _timeRemaining;
        private float _overtimeElapsed = 0f;
        private int _blueScore = 0;
        private int _orangeScore = 0;

        public MatchState CurrentState => _state;
        public int BlueScore => _blueScore;
        public int OrangeScore => _orangeScore;

        private void OnEnable()
        {
            BallController.OnGoalScored += HandleGoalScored;
        }

        private void OnDisable()
        {
            BallController.OnGoalScored -= HandleGoalScored;
        }

        private void Start()
        {
            _timeRemaining = matchDuration;

            if (ball == null)
            {
                ball = FindFirstObjectByType<BallController>();
            }

            if (blueCars.Count == 0 && orangeCars.Count == 0)
            {
                CarController[] cars = FindObjectsByType<CarController>(FindObjectsSortMode.None);
                foreach (var car in cars)
                {
                    BotController bot = car.GetComponent<BotController>();
                    if (bot != null && !bot.isBlueTeam)
                        orangeCars.Add(car);
                    else
                        blueCars.Add(car);
                }
            }

            if (mainCamera == null)
            {
                mainCamera = FindFirstObjectByType<CameraController>();
            }

            if (audioSource == null)
            {
                audioSource = GetComponent<AudioSource>();
                if (audioSource == null) audioSource = gameObject.AddComponent<AudioSource>();
            }

            if (countdownBeep == null) countdownBeep = ProceduralAudioSynthesizer.CreateCountdownBeepClip(false);
            if (goWhistle == null) goWhistle = ProceduralAudioSynthesizer.CreateCountdownBeepClip(true);
            if (goalHorn == null) goalHorn = ProceduralAudioSynthesizer.CreateGoalHornClip();
            if (matchOverBuzzer == null) matchOverBuzzer = ProceduralAudioSynthesizer.CreateWhistleClip();

            FindBoostPadsInScene();
            StartCoroutine(KickoffSequence());
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.R) || Input.GetKeyDown(KeyCode.JoystickButton8))
            {
                StopAllCoroutines();
                StartCoroutine(KickoffSequence());
            }
            UpdateClock();
            UpdateUI();
        }

        private void UpdateClock()
        {
            if (_state == MatchState.InPlay)
            {
                _timeRemaining -= Time.deltaTime;
                if (_timeRemaining <= 0f)
                {
                    _timeRemaining = 0f;
                    // Zero-second rule: match concludes once ball touches turf
                    if (ball != null && ball.Position.y <= (ball.radius + 0.15f))
                    {
                        EndZeroSecondsPlay();
                    }
                }
            }
            else if (_state == MatchState.Overtime)
            {
                _overtimeElapsed += Time.deltaTime;
            }
        }

        private void EndZeroSecondsPlay()
        {
            if (_blueScore == _orangeScore)
            {
                StartOvertime();
            }
            else
            {
                EndMatch();
            }
        }

        private void StartOvertime()
        {
            _state = MatchState.Overtime;
            _overtimeElapsed = 0f;
            if (announcementText != null) announcementText.text = "OVERTIME!";
            StartCoroutine(KickoffSequence());
        }

        private void EndMatch()
        {
            _state = MatchState.MatchOver;
            if (audioSource != null && matchOverBuzzer != null) audioSource.PlayOneShot(matchOverBuzzer);

            bool blueWon = _blueScore > _orangeScore;
            string winner = blueWon ? "BLUE WINS!" : "ORANGE WINS!";
            if (announcementText != null) announcementText.text = winner;

            if (ball != null) ball.SetFrozen(true);
            FreezeAllCars(true);

            // Show post-match results UI with XP & Coins
            MatchResultUI resultUI = FindFirstObjectByType<MatchResultUI>();
            if (resultUI != null)
            {
                int earnedXP = blueWon ? 350 : 150;
                int earnedCoins = blueWon ? 100 : 35;
                if (PlayerProgression.Instance != null)
                {
                    PlayerProgression.Instance.AddMatchRewards(blueWon, earnedXP, earnedCoins);
                }
                resultUI.ShowResults(blueWon, _blueScore, _orangeScore, earnedXP, earnedCoins);
            }
        }

        private IEnumerator KickoffSequence()
        {
            _state = MatchState.Countdown;

            if (ball != null)
            {
                ball.ResetKickoff();
                ball.SetFrozen(true);
            }

            PositionCarsForKickoff();
            FreezeAllCars(true);

            foreach (var pad in boostPads)
            {
                if (pad != null) pad.ResetPad();
            }

            for (int i = 3; i >= 1; i--)
            {
                if (announcementText != null) announcementText.text = i.ToString();
                if (audioSource != null && countdownBeep != null) audioSource.PlayOneShot(countdownBeep);
                yield return new WaitForSeconds(1.0f);
            }

            if (announcementText != null) announcementText.text = "GO!";
            if (audioSource != null && goWhistle != null) audioSource.PlayOneShot(goWhistle);

            FreezeAllCars(false);
            if (ball != null) ball.SetFrozen(false);

            _state = (_timeRemaining <= 0f && _blueScore == _orangeScore) ? MatchState.Overtime : MatchState.InPlay;

            yield return new WaitForSeconds(1.0f);
            if (announcementText != null) announcementText.text = "";
        }

        private void PositionCarsForKickoff()
        {
            // Blue Team facing center (+X direction -> Y rotation 90 degrees)
            Quaternion blueRot = Quaternion.Euler(0, 90, 0);

            if (blueCars.Count > 0 && blueCars[0] != null)
                blueCars[0].ResetVehicle(blueSpawnPlayer, blueRot);
            if (blueCars.Count > 1 && blueCars[1] != null)
                blueCars[1].ResetVehicle(blueSpawnTeammate1, blueRot);
            if (blueCars.Count > 2 && blueCars[2] != null)
                blueCars[2].ResetVehicle(blueSpawnTeammate2, blueRot);

            // Orange Team facing center (-X direction -> Y rotation -90 degrees)
            Quaternion orangeRot = Quaternion.Euler(0, -90, 0);

            if (orangeCars.Count > 0 && orangeCars[0] != null)
                orangeCars[0].ResetVehicle(orangeSpawnPlayer, orangeRot);
            if (orangeCars.Count > 1 && orangeCars[1] != null)
                orangeCars[1].ResetVehicle(orangeSpawnTeammate1, orangeRot);
            if (orangeCars.Count > 2 && orangeCars[2] != null)
                orangeCars[2].ResetVehicle(orangeSpawnTeammate2, orangeRot);
        }

        private void FreezeAllCars(bool freeze)
        {
            foreach (var car in blueCars) if (car != null) car.SetControlsLocked(freeze);
            foreach (var car in orangeCars) if (car != null) car.SetControlsLocked(freeze);
        }

        private void HandleGoalScored(int scoringTeam)
        {
            if (_state != MatchState.InPlay && _state != MatchState.Overtime) return;

            // Immediately freeze the ball inside the net
            if (ball != null) ball.SetFrozen(true);

            if (scoringTeam == 0) _blueScore++;
            else _orangeScore++;

            if (ScoreboardManager.Instance != null)
            {
                string scorer = scoringTeam == 0 ? "Apex Striker" : "Amber Bot";
                ScoreboardManager.Instance.RegisterStat(scorer, "GOAL");
            }

            StartCoroutine(GoalExplosionRoutine(scoringTeam));
        }

        private IEnumerator GoalExplosionRoutine(int scoringTeam)
        {
            _state = MatchState.GoalCelebration;
            Vector3 blastOrigin = (scoringTeam == 0) ? orangeGoalExplosionPos : blueGoalExplosionPos;

            // Trigger Replay-style Camera focusing and orbiting the goal mouth
            if (GoalReplayCamera.Instance != null)
            {
                Transform targetFocus = (ball != null) ? ball.transform : transform;
                GoalReplayCamera.Instance.PlayCelebrationReplay(targetFocus, goalCelebrationDuration);
            }

            if (scoringTeam == 0 && orangeGoalExplosionFx != null) orangeGoalExplosionFx.Play();
            else if (scoringTeam == 1 && blueGoalExplosionFx != null) blueGoalExplosionFx.Play();

            if (audioSource != null && goalHorn != null) audioSource.PlayOneShot(goalHorn);
            if (mainCamera != null) mainCamera.AddShake(1.0f);

            if (announcementText != null)
            {
                announcementText.text = scoringTeam == 0 ? "BLUE SCORED!" : "ORANGE SCORED!";
            }

            ApplyShockwave(blastOrigin);

            yield return new WaitForSeconds(goalCelebrationDuration);

            // In overtime, sudden death (Golden Goal) concludes the match immediately
            if (_state == MatchState.Overtime || (_timeRemaining <= 0f && _blueScore != _orangeScore))
            {
                EndMatch();
            }
            else
            {
                StartCoroutine(KickoffSequence());
            }
        }

        private void ApplyShockwave(Vector3 origin)
        {
            List<CarController> allCars = new List<CarController>();
            allCars.AddRange(blueCars);
            allCars.AddRange(orangeCars);

            foreach (var car in allCars)
            {
                if (car == null || car.Rb == null) continue;

                Vector3 diff = car.transform.position - origin;
                float dist = diff.magnitude;
                if (dist < explosionRadius)
                {
                    Vector3 blastDir = (diff.normalized + Vector3.up * 0.5f).normalized;
                    float falloff = 1f - Mathf.Clamp01(dist / explosionRadius);
                    car.Rb.AddForce(blastDir * explosionForce * falloff, ForceMode.Impulse);
                }
            }
        }

        private void UpdateUI()
        {
            if (inGameHUD != null)
            {
                if (inGameHUD.blueScoreText != null) inGameHUD.blueScoreText.text = _blueScore.ToString();
                if (inGameHUD.orangeScoreText != null) inGameHUD.orangeScoreText.text = _orangeScore.ToString();
                if (inGameHUD.matchTimerText != null)
                {
                    if (_state == MatchState.Overtime)
                    {
                        int otMin = Mathf.FloorToInt(_overtimeElapsed / 60f);
                        int otSec = Mathf.FloorToInt(_overtimeElapsed % 60f);
                        inGameHUD.matchTimerText.text = $"+{otMin}:{otSec:D2}";
                        if (inGameHUD.overtimeIndicator != null) inGameHUD.overtimeIndicator.SetActive(true);
                    }
                    else
                    {
                        int min = Mathf.FloorToInt(_timeRemaining / 60f);
                        int sec = Mathf.FloorToInt(_timeRemaining % 60f);
                        inGameHUD.matchTimerText.text = $"{min:D2}:{sec:D2}";
                        if (inGameHUD.overtimeIndicator != null) inGameHUD.overtimeIndicator.SetActive(false);
                    }
                }
                return;
            }

            if (scoreText != null)
            {
                scoreText.text = $"BLUE {_blueScore}   |   {_orangeScore} ORANGE";
            }

            if (timerText != null)
            {
                if (_state == MatchState.Overtime)
                {
                    int otMin = Mathf.FloorToInt(_overtimeElapsed / 60f);
                    int otSec = Mathf.FloorToInt(_overtimeElapsed % 60f);
                    timerText.text = $"+{otMin}:{otSec:D2}";
                }
                else
                {
                    int min = Mathf.FloorToInt(_timeRemaining / 60f);
                    int sec = Mathf.FloorToInt(_timeRemaining % 60f);
                    timerText.text = $"{min}:{sec:D2}";
                }
            }
        }

        private void FindBoostPadsInScene()
        {
            boostPads.Clear();
            boostPads.AddRange(FindObjectsByType<BoostPad>(FindObjectsSortMode.None));
        }
    }
}
