using System.Collections;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Smoothly focuses and orbits the scoring car or goal net during goal celebrations.
    /// </summary>
    public class GoalReplayCamera : MonoBehaviour
    {
        public static GoalReplayCamera Instance { get; private set; }

        [Header("=== REPLAY SETTINGS ===")]
        public float orbitDistance = 8.5f;
        public float orbitHeight = 3.2f;
        public float orbitSpeed = 45f;

        private bool _isReplaying = false;
        private Transform _replayTarget;
        private float _currentAngle = 0f;
        private Camera _replayCam;

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this)
            {
                Destroy(this);
                return;
            }

            _replayCam = GetComponent<Camera>();
            if (_replayCam != null)
            {
                _replayCam.enabled = true;
            }
        }

        public void PlayCelebrationReplay(Transform targetCar, float duration)
        {
            _replayTarget = targetCar;
            _isReplaying = true;
            _currentAngle = 0f;
            if (_replayCam != null) _replayCam.enabled = true;

            var camCtrl = GetComponent<CameraController>();
            if (camCtrl != null) camCtrl.enabled = false;

            StartCoroutine(StopReplayAfter(duration));
        }

        private IEnumerator StopReplayAfter(float duration)
        {
            yield return new WaitForSeconds(duration);
            _isReplaying = false;

            var camCtrl = GetComponent<CameraController>();
            if (camCtrl != null) camCtrl.enabled = true;
            if (_replayCam != null) _replayCam.enabled = true;
        }

        private void LateUpdate()
        {
            if (!_isReplaying || _replayTarget == null) return;

            _currentAngle += orbitSpeed * Time.deltaTime;
            float rad = _currentAngle * Mathf.Deg2Rad;

            Vector3 offset = new Vector3(Mathf.Sin(rad) * orbitDistance, orbitHeight, Mathf.Cos(rad) * orbitDistance);
            transform.position = _replayTarget.position + offset;
            transform.LookAt(_replayTarget.position + Vector3.up * 0.8f);
        }
    }
}
