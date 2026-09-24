using System.Collections;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League Boost Pickup Pad (1 Unit = 1 Meter scale).
    /// Small Pad: Diameter 2m, Height 0.15m (+12 Boost, 4s respawn)
    /// Large Pad: Diameter 4m, Height 0.20m (+100 Boost, 10s respawn)
    /// </summary>
    public class BoostPad : MonoBehaviour
    {
        public enum PadType
        {
            SmallPad,
            LargeOrb
        }

        [Header("=== CONFIGURATION ===")]
        public PadType padType = PadType.SmallPad;
        public float boostAmount = 12f;
        public float respawnTime = 4.0f;
        public float padDiameter = 2.0f;
        public float padHeight = 0.15f;

        [Header("=== VISUALS ===")]
        public GameObject activeVisuals;
        public GameObject inactiveVisuals;
        public Transform floatingCrystal;
        public Light glowLight;
        public ParticleSystem pickupParticles;

        [Header("=== AUDIO ===")]
        public AudioSource audioSource;
        public AudioClip pickupSound;

        private bool _isAvailable = true;
        private Vector3 _crystalStartPos;

        public bool IsAvailable => _isAvailable;
        public bool IsActive => _isAvailable;
        public bool isFullBoost => padType == PadType.LargeOrb;

        private void Awake()
        {
            if (padType == PadType.LargeOrb)
            {
                boostAmount = 100f;
                respawnTime = 10.0f;
                padDiameter = 4.0f;
                padHeight = 0.2f;
            }
            else
            {
                boostAmount = 12f;
                respawnTime = 4.0f;
                padDiameter = 2.0f;
                padHeight = 0.15f;
            }

            if (floatingCrystal != null)
            {
                _crystalStartPos = floatingCrystal.localPosition;
            }

            SetState(true);
        }

        private void Update()
        {
            if (!_isAvailable) return;

            if (floatingCrystal != null)
            {
                floatingCrystal.Rotate(Vector3.up, 90f * Time.deltaTime, Space.World);
                float yOffset = Mathf.Sin(Time.time * 2.5f) * 0.18f;
                floatingCrystal.localPosition = _crystalStartPos + new Vector3(0, yOffset, 0);
            }
        }

        private void OnTriggerEnter(Collider other)
        {
            if (!_isAvailable) return;

            CarController car = other.GetComponentInParent<CarController>();
            if (car != null)
            {
                if (car.CurrentBoost < 100f)
                {
                    car.AddBoost(boostAmount);
                    Consume();
                }
            }
        }

        public void Consume()
        {
            if (!_isAvailable) return;

            _isAvailable = false;
            SetState(false);

            if (pickupParticles != null) pickupParticles.Play();
            if (audioSource != null && pickupSound != null) audioSource.PlayOneShot(pickupSound);

            StartCoroutine(RespawnRoutine());
        }

        private IEnumerator RespawnRoutine()
        {
            yield return new WaitForSeconds(respawnTime);
            _isAvailable = true;
            SetState(true);
        }

        private void SetState(bool active)
        {
            if (activeVisuals != null) activeVisuals.SetActive(active);
            if (inactiveVisuals != null) inactiveVisuals.SetActive(!active);
            if (glowLight != null) glowLight.enabled = active;
            if (floatingCrystal != null) floatingCrystal.gameObject.SetActive(active);
        }

        public void ResetPad()
        {
            StopAllCoroutines();
            _isAvailable = true;
            SetState(true);
        }
    }
}
