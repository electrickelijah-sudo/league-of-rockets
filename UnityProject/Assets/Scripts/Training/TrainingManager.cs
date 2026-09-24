using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    public enum TrainingDrillType
    {
        FreePlay,
        ShootingDrill,
        GoalieSaveDrill,
        AerialDrill
    }

    /// <summary>
    /// Training mode manager supporting Free Play (unlimited boost, instant reset, ball launch)
    /// and structured skill drills (Shooting target rings, Goalie saves, Aerial hits).
    /// </summary>
    public class TrainingManager : MonoBehaviour
    {
        public static TrainingManager Instance { get; private set; }

        [Header("=== DRILL CONFIGURATION ===")]
        public TrainingDrillType currentDrill = TrainingDrillType.FreePlay;

        [Header("=== REFERENCES ===")]
        public CarController playerCar;
        public BallController ball;
        public Transform orangeGoalTarget;

        [Header("=== HUD & INSTRUCTIONS ===")]
        public Text instructionText;
        public Text scoreCounterText;

        private int _successfulDrills = 0;
        private Vector3 _carStartPos = new Vector3(0f, 0.8f, -35f);

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);
        }

        private void Start()
        {
            if (playerCar != null)
            {
                _carStartPos = playerCar.transform.position;
            }
            StartDrill(currentDrill);
        }

        private void Update()
        {
            // Free play hotkeys
            if (Input.GetKeyDown(KeyCode.R))
            {
                ResetCarAndBall();
            }

            if (Input.GetKeyDown(KeyCode.F))
            {
                ResetBallToCenter();
            }

            if (Input.GetKeyDown(KeyCode.B))
            {
                LaunchBallAtCar();
            }

            if (currentDrill == TrainingDrillType.FreePlay && playerCar != null)
            {
                // Infinite boost for training
                playerCar.AddBoost(100f);
            }
        }

        public void StartDrill(TrainingDrillType drill)
        {
            currentDrill = drill;
            _successfulDrills = 0;
            ResetCarAndBall();

            switch (drill)
            {
                case TrainingDrillType.FreePlay:
                    if (instructionText != null)
                        instructionText.text = "FREE PLAY\n[R] Reset Car & Ball | [F] Center Ball | [B] Launch Ball | Infinite Boost";
                    break;

                case TrainingDrillType.ShootingDrill:
                    if (instructionText != null)
                        instructionText.text = "SHOOTING DRILL: Strike the ball cleanly into the orange net!";
                    SetupShootingDrill();
                    break;

                case TrainingDrillType.GoalieSaveDrill:
                    if (instructionText != null)
                        instructionText.text = "GOALIE SAVE: Guard the net and clear incoming shots!";
                    SetupGoalieDrill();
                    break;

                case TrainingDrillType.AerialDrill:
                    if (instructionText != null)
                        instructionText.text = "AERIAL DRILL: Double-jump and boost up to strike high-altitude balls!";
                    SetupAerialDrill();
                    break;
            }

            UpdateScoreUI();
        }

        private void SetupShootingDrill()
        {
            if (ball != null)
            {
                ball.transform.position = new Vector3(Random.Range(-12f, 12f), 1.25f, Random.Range(-5f, 15f));
                ball.Rb.linearVelocity = Vector3.zero;
            }
        }

        private void SetupGoalieDrill()
        {
            if (playerCar != null)
            {
                playerCar.transform.position = new Vector3(0f, 0.8f, -44f);
                playerCar.transform.rotation = Quaternion.identity;
                playerCar.Rb.linearVelocity = Vector3.zero;
            }

            if (ball != null)
            {
                ball.transform.position = new Vector3(Random.Range(-15f, 15f), 1.25f, Random.Range(10f, 25f));
                Vector3 toGoal = (new Vector3(Random.Range(-7f, 7f), Random.Range(1f, 5f), -50f) - ball.transform.position).normalized;
                ball.Rb.linearVelocity = toGoal * Random.Range(18f, 28f);
            }
        }

        private void SetupAerialDrill()
        {
            if (ball != null)
            {
                ball.transform.position = new Vector3(Random.Range(-8f, 8f), Random.Range(7f, 12f), Random.Range(-10f, 10f));
                ball.Rb.linearVelocity = Vector3.up * 4f;
            }
        }

        public void ResetCarAndBall()
        {
            if (playerCar != null)
            {
                playerCar.transform.position = _carStartPos;
                playerCar.transform.rotation = Quaternion.identity;
                if (playerCar.Rb != null)
                {
                    playerCar.Rb.linearVelocity = Vector3.zero;
                    playerCar.Rb.angularVelocity = Vector3.zero;
                }
            }

            ResetBallToCenter();
        }

        public void ResetBallToCenter()
        {
            if (ball != null)
            {
                ball.ResetKickoff();
            }
        }

        public void LaunchBallAtCar()
        {
            if (ball == null || playerCar == null) return;

            ball.transform.position = playerCar.transform.position + playerCar.transform.forward * 22f + Vector3.up * 3f;
            Vector3 dir = (playerCar.transform.position - ball.transform.position).normalized;
            ball.Rb.linearVelocity = dir * 20f + Vector3.up * 6f;
        }

        public void RecordSuccess()
        {
            _successfulDrills++;
            UpdateScoreUI();
            if (currentDrill != TrainingDrillType.FreePlay)
            {
                StartCoroutine(NextRepRoutine());
            }
        }

        private IEnumerator NextRepRoutine()
        {
            yield return new WaitForSeconds(1.5f);
            StartDrill(currentDrill);
        }

        private void UpdateScoreUI()
        {
            if (scoreCounterText != null)
            {
                scoreCounterText.text = $"COMPLETED: {_successfulDrills}";
            }
        }
    }
}
