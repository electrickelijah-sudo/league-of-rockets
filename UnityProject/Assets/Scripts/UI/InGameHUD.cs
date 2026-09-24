using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    /// <summary>
    /// Broadcast tournament in-game HUD overlay:
    /// - Top central scoreboard: BLUE SCORE | TIME / OVERTIME | ORANGE SCORE
    /// - Boost meter dial & percentage
    /// - Speedometer in KM/H
    /// - Off-screen directional ball indicator
    /// - Dynamic pop-up stat notification badges
    /// </summary>
    public class InGameHUD : MonoBehaviour
    {
        [Header("=== SCOREBOARD & CLOCK ===")]
        public Text blueScoreText;
        public Text orangeScoreText;
        public Text matchTimerText;
        public GameObject overtimeIndicator;

        [Header("=== BOOST GAUGE ===")]
        public Image boostFillImage;
        public Text boostValueText;
        public GameObject supersonicIcon;

        [Header("=== SPEEDOMETER ===")]
        public Text speedKmhText;

        [Header("=== OFF-SCREEN BALL INDICATOR ===")]
        public RectTransform ballPointerArrow;
        public Text ballDistanceText;

        [Header("=== NOTIFICATIONS & BANNERS ===")]
        public GameObject kickoffCountdownBanner;
        public Text countdownNumberText;
        public GameObject goalScoredBanner;
        public Text goalTitleText;
        public GameObject statNotificationBadge;
        public Text statBadgeText;

        [Header("=== REFERENCES ===")]
        public CarController playerCar;
        public BallController ball;
        public Camera mainCam;

        private float _statBadgeTimer = 0f;

        private void Start()
        {
            if (mainCam == null) mainCam = Camera.main;

            if (playerCar == null)
            {
                CarController[] cars = FindObjectsByType<CarController>(FindObjectsSortMode.None);
                foreach (var c in cars)
                {
                    if (!c.isAI)
                    {
                        playerCar = c;
                        break;
                    }
                }
                if (playerCar == null && cars.Length > 0) playerCar = cars[0];
            }

            if (ball == null)
            {
                ball = FindFirstObjectByType<BallController>();
            }

            if (statNotificationBadge != null) statNotificationBadge.SetActive(false);
        }

        private void Update()
        {
            UpdateBoostGauge();
            UpdateSpeedometer();
            UpdateBallIndicator();

            if (_statBadgeTimer > 0f)
            {
                _statBadgeTimer -= Time.deltaTime;
                if (_statBadgeTimer <= 0f && statNotificationBadge != null)
                {
                    statNotificationBadge.SetActive(false);
                }
            }
        }

        private void UpdateBoostGauge()
        {
            if (playerCar == null) return;

            float boost = playerCar.CurrentBoost;
            if (boostFillImage != null) boostFillImage.fillAmount = boost / 100f;
            if (boostValueText != null) boostValueText.text = Mathf.RoundToInt(boost).ToString();

            if (supersonicIcon != null)
            {
                supersonicIcon.SetActive(playerCar.IsSupersonic);
            }
        }

        private void UpdateSpeedometer()
        {
            if (playerCar == null || playerCar.Rb == null || speedKmhText == null) return;

            float speedKmh = playerCar.Rb.linearVelocity.magnitude * 3.6f;
            speedKmhText.text = $"{Mathf.RoundToInt(speedKmh)} KM/H";
        }

        private void UpdateBallIndicator()
        {
            if (ball == null || mainCam == null || ballPointerArrow == null) return;

            Vector3 screenPos = mainCam.WorldToViewportPoint(ball.transform.position);
            bool isOffScreen = screenPos.z < 0 || screenPos.x < 0.05f || screenPos.x > 0.95f || screenPos.y < 0.05f || screenPos.y > 0.95f;

            ballPointerArrow.gameObject.SetActive(isOffScreen);

            if (isOffScreen)
            {
                if (screenPos.z < 0)
                {
                    screenPos.x = 1f - screenPos.x;
                    screenPos.y = 1f - screenPos.y;
                }

                Vector2 onScreen = new Vector2(
                    Mathf.Clamp(screenPos.x, 0.08f, 0.92f) * Screen.width,
                    Mathf.Clamp(screenPos.y, 0.08f, 0.92f) * Screen.height
                );

                ballPointerArrow.position = onScreen;

                Vector2 dir = (onScreen - new Vector2(Screen.width * 0.5f, Screen.height * 0.5f)).normalized;
                float angle = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg;
                ballPointerArrow.rotation = Quaternion.Euler(0, 0, angle - 90f);

                if (ballDistanceText != null)
                {
                    float dist = Vector3.Distance(playerCar != null ? playerCar.transform.position : Vector3.zero, ball.transform.position);
                    ballDistanceText.text = $"{Mathf.RoundToInt(dist)}m";
                }
            }
        }

        public void DisplayStatBadge(string statTitle, int points)
        {
            if (statNotificationBadge != null && statBadgeText != null)
            {
                statBadgeText.text = $"{statTitle}\n+{points}";
                statNotificationBadge.SetActive(true);
                _statBadgeTimer = 2.2f;
            }
        }
    }
}
