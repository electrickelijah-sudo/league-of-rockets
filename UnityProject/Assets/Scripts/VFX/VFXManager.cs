using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Procedurally manages and generates dynamic visual particle effects:
    /// - Jet rocket boost flames & sparks
    /// - Tire skid smoke
    /// - Ball collision sparks
    /// - Goal explosion shockwaves & confetti
    /// </summary>
    public class VFXManager : MonoBehaviour
    {
        public static VFXManager Instance { get; private set; }

        [Header("=== PARTICLE POOLS ===")]
        public ParticleSystem boostFlamePrefab;
        public ParticleSystem tireSmokePrefab;
        public ParticleSystem ballImpactSparksPrefab;
        public ParticleSystem goalShockwavePrefab;

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);
        }

        public void SpawnBallImpactSparks(Vector3 position, float impactForce)
        {
            SpawnBallImpactSparks(position, Vector3.up, impactForce);
        }

        public void SpawnBallImpactSparks(Vector3 position, Vector3 normal, float impactForce)
        {
            if (ballImpactSparksPrefab != null)
            {
                Quaternion rot = normal != Vector3.zero ? Quaternion.LookRotation(normal) : Quaternion.identity;
                ParticleSystem ps = Instantiate(ballImpactSparksPrefab, position, rot);
                ps.transform.localScale = Vector3.one * Mathf.Clamp(impactForce / 20f, 0.5f, 2.5f);
                ps.Play();
                Destroy(ps.gameObject, 2.0f);
            }
        }

        public void SpawnTireSkidSmoke(Vector3 position, Vector3 velocity, float driftFactor)
        {
            if (tireSmokePrefab != null && driftFactor > 0.3f)
            {
                ParticleSystem ps = Instantiate(tireSmokePrefab, position, Quaternion.identity);
                var main = ps.main;
                main.startSpeed = Mathf.Clamp(velocity.magnitude * 0.2f, 1f, 5f);
                ps.transform.localScale = Vector3.one * Mathf.Clamp01(driftFactor);
                ps.Play();
                Destroy(ps.gameObject, 1.2f);
            }
        }

        public void SpawnBoostFlame(Transform nozzle, Color flameColor, bool supersonic)
        {
            if (boostFlamePrefab != null && nozzle != null)
            {
                ParticleSystem ps = Instantiate(boostFlamePrefab, nozzle.position, nozzle.rotation, nozzle);
                var main = ps.main;
                main.startColor = flameColor;
                if (supersonic)
                {
                    main.startSpeed = main.startSpeed.constant * 1.5f;
                }
                ps.Play();
                Destroy(ps.gameObject, 0.35f);
            }
        }

        public void SpawnGoalShockwave(Vector3 position, Color teamColor)
        {
            if (goalShockwavePrefab != null)
            {
                ParticleSystem ps = Instantiate(goalShockwavePrefab, position, Quaternion.identity);
                var main = ps.main;
                main.startColor = teamColor;
                ps.Play();
                Destroy(ps.gameObject, 4.0f);
            }
        }
    }
}
