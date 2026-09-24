using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League style dynamic follow camera controller (1 Unit = 1 Meter scale).
    /// Features authentic Ball Cam toggle, customizable RL camera settings (Distance, Height, Angle, FOV, Stiffness),
    /// supersonic FOV warp, and trauma-based camera shake.
    /// </summary>
    public class CameraController : MonoBehaviour
    {
        [Header("=== TARGETS ===")]
        public Transform carTarget;
        public Transform ballTarget;

        [Header("=== ROCKET LEAGUE CAMERA SETTINGS ===")]
        [Tooltip("Field of view in degrees")]
        [Range(60f, 120f)]
        public float fieldOfView = 110f;

        [Tooltip("Distance from car in world units (meters)")]
        public float distance = 7.5f;

        [Tooltip("Height above car pivot in world units (meters)")]
        public float height = 2.8f;

        [Tooltip("Pitch angle offset in degrees")]
        [Range(-20f, 10f)]
        public float pitchAngle = -4f;

        [Tooltip("Camera tracking stiffness (0 = loose lazy follow, 1 = locked rigid)")]
        [Range(0f, 1f)]
        public float stiffness = 0.55f;

        [Tooltip("Transition speed when toggling Ball Cam on/off")]
        public float swivelSpeed = 12f;

        [Header("=== SUPERSONIC EFFECTS ===")]
        public float supersonicFovBoost = 8f;

        [Header("=== MODE & CONTROLS ===")]
        public bool isBallCam = false;
        public KeyCode toggleBallCamKey = KeyCode.C;

        private Camera _cam;
        private Vector3 _currentVelocity;
        private float _shakeTrauma = 0f;
        private CarController _carController;

        private void Awake()
        {
            _cam = GetComponent<Camera>();
            if (_cam == null) _cam = Camera.main;

            if (carTarget == null)
            {
                CarController[] cars = FindObjectsByType<CarController>(FindObjectsSortMode.None);
                foreach (var c in cars)
                {
                    if (!c.isAI)
                    {
                        carTarget = c.transform;
                        break;
                    }
                }
                if (carTarget == null && cars.Length > 0)
                {
                    carTarget = cars[0].transform;
                }
            }

            if (ballTarget == null)
            {
                BallController ball = FindFirstObjectByType<BallController>();
                if (ball != null) ballTarget = ball.transform;
            }

            if (carTarget != null)
            {
                _carController = carTarget.GetComponent<CarController>();
            }
        }

        private void OnEnable()
        {
            BallController.OnBallHit += HandleBallHit;
        }

        private void OnDisable()
        {
            BallController.OnBallHit -= HandleBallHit;
        }

        private void Update()
        {
            if (Input.GetKeyDown(toggleBallCamKey) || Input.GetKeyDown(KeyCode.JoystickButton3))
            {
                isBallCam = !isBallCam;
            }

            if (_shakeTrauma > 0f)
            {
                _shakeTrauma = Mathf.Max(0f, _shakeTrauma - Time.deltaTime * 1.6f);
            }
        }

        private void LateUpdate()
        {
            if (carTarget == null) return;

            Vector3 carPos = carTarget.position;
            Vector3 targetCamPos;
            Quaternion targetCamRot;

            if (isBallCam && ballTarget != null)
            {
                Vector3 toBall = (ballTarget.position - carPos);
                toBall.y = 0;
                if (toBall.sqrMagnitude < 0.01f) toBall = carTarget.forward;
                toBall.Normalize();

                targetCamPos = carPos - toBall * distance + Vector3.up * height;
                Vector3 lookTarget = ballTarget.position + Vector3.up * 0.4f;
                targetCamRot = Quaternion.LookRotation((lookTarget - targetCamPos).normalized, Vector3.up);
                targetCamRot *= Quaternion.Euler(pitchAngle, 0, 0);
            }
            else
            {
                Vector3 forward = carTarget.forward;
                forward.y = 0;
                forward.Normalize();

                targetCamPos = carPos - forward * distance + Vector3.up * height;
                Vector3 lookTarget = carPos + forward * 4f + Vector3.up * 1.2f;
                targetCamRot = Quaternion.LookRotation((lookTarget - targetCamPos).normalized, Vector3.up);
                targetCamRot *= Quaternion.Euler(pitchAngle, 0, 0);
            }

            // Prevent ground clipping
            if (targetCamPos.y < 0.5f)
            {
                targetCamPos.y = 0.5f;
            }

            float smoothTime = Mathf.Lerp(0.18f, 0.02f, stiffness);
            transform.position = Vector3.SmoothDamp(transform.position, targetCamPos, ref _currentVelocity, smoothTime);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetCamRot, swivelSpeed * Time.deltaTime);

            // Supersonic FOV Warp
            float targetFov = fieldOfView;
            if (_carController != null && _carController.IsSupersonic)
            {
                targetFov += supersonicFovBoost;
            }
            if (_cam != null)
            {
                _cam.fieldOfView = Mathf.Lerp(_cam.fieldOfView, targetFov, 8f * Time.deltaTime);
            }

            // Trauma camera shake
            if (_shakeTrauma > 0.01f)
            {
                float shakePower = _shakeTrauma * _shakeTrauma;
                float offsetX = (Mathf.PerlinNoise(Time.time * 25f, 0f) * 2f - 1f) * 0.25f * shakePower;
                float offsetY = (Mathf.PerlinNoise(0f, Time.time * 25f) * 2f - 1f) * 0.25f * shakePower;
                transform.position += transform.right * offsetX + transform.up * offsetY;
            }
        }

        public void AddShake(float traumaAmount)
        {
            _shakeTrauma = Mathf.Clamp01(_shakeTrauma + traumaAmount);
        }

        private void HandleBallHit(Vector3 hitPos, float hitSpeed)
        {
            if (hitSpeed > 15.0f)
            {
                AddShake(Mathf.Clamp01(hitSpeed / 40.0f) * 0.4f);
            }
        }
    }
}
