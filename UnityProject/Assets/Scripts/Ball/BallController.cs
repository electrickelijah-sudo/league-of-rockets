using System;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Rocket League authentic ball physics controller (1 Unit = 1 Meter scale).
    /// Exact dimensions:
    /// - Ball Diameter: 2.5 m
    /// - Ball Radius: 1.25 m
    /// - SphereCollider Radius: 1.25 m
    /// - Kickoff Center: (0, 1.25, 0)
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(SphereCollider))]
    public class BallController : MonoBehaviour
    {
        [Header("=== BALL DIMENSIONS ===")]
        [Tooltip("Ball radius in meters (1.25 m = 2.5m diameter)")]
        public float radius = 1.25f;

        [Tooltip("Kickoff center position")]
        public Vector3 kickoffPosition = new Vector3(0f, 1.25f, 0f);

        [Header("=== DYNAMICS & BOUNCE ===")]
        [Range(0.4f, 0.95f)]
        public float bounciness = 0.82f;

        [Tooltip("Maximum linear speed clamp")]
        public float maxSpeed = 45.0f;

        [Tooltip("Downforce gravity multiplier")]
        public float gravityMultiplier = 1.25f;

        [Tooltip("Car front bumper strike impulse multiplier")]
        public float bumperHitMultiplier = 1.4f;

        [Tooltip("Upward pop factor on collision")]
        public float verticalPopFactor = 0.32f;

        [Header("=== VISUALS & FX ===")]
        public Transform groundIndicator;
        public TrailRenderer speedTrail;
        public float trailSpeedThreshold = 18.0f;
        public ParticleSystem bounceParticles;

        [Header("=== AUDIO ===")]
        public AudioSource audioSource;
        public AudioClip bounceSound;
        public AudioClip carHitSound;

        // Events
        public static event Action<Vector3, float> OnBallHit;
        public static event Action<int> OnGoalScored; // 0 = Blue Goal, 1 = Orange Goal

        private Rigidbody _rb;
        private SphereCollider _col;
        private bool _isFrozen = false;

        public Rigidbody Rb => _rb;
        public Vector3 Position => transform.position;
        public Vector3 Velocity => _rb != null ? _rb.linearVelocity : Vector3.zero;
        public float CurrentSpeed => _rb != null ? _rb.linearVelocity.magnitude : 0f;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _col = GetComponent<SphereCollider>();

            _rb.mass = 35.0f;
            _rb.linearDamping = 0.08f;
            _rb.angularDamping = 0.15f;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;

            _col.radius = radius;
            PhysicsMaterial mat = new PhysicsMaterial("BallBounceMat")
            {
                bounciness = bounciness,
                bounceCombine = PhysicsMaterialCombine.Maximum,
                dynamicFriction = 0.35f,
                staticFriction = 0.35f,
                frictionCombine = PhysicsMaterialCombine.Multiply
            };
            _col.material = mat;
        }

        private void FixedUpdate()
        {
            if (_isFrozen) return;

            // Apply gravity tuning
            _rb.AddForce(Physics.gravity * (gravityMultiplier - 1f), ForceMode.Acceleration);

            // Clamp max velocity
            if (_rb.linearVelocity.sqrMagnitude > maxSpeed * maxSpeed)
            {
                _rb.linearVelocity = _rb.linearVelocity.normalized * maxSpeed;
            }

            // Anti-Stuck Watchdog: Nudge ball back into play if pinned in corner/posts
            if (_rb.linearVelocity.sqrMagnitude < 0.2f && transform.position.y > 0.5f)
            {
                _stuckTimer += Time.fixedDeltaTime;
                if (_stuckTimer > 3.5f)
                {
                    _stuckTimer = 0f;
                    Vector3 centerDir = (Vector3.up * 2.5f - transform.position).normalized;
                    _rb.AddForce(centerDir * 14f, ForceMode.Impulse);
                    Debug.Log("<color=yellow>[BallController]</color> Anti-Stuck Watchdog activated: Ball nudged into play!");
                }
            }
            else
            {
                _stuckTimer = 0f;
            }
        }

        private float _stuckTimer = 0f;

        private void Update()
        {
            // Ground projection decal position
            if (groundIndicator != null)
            {
                if (Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit, 60f, LayerMask.GetMask("Default", "Ground", "Arena")))
                {
                    groundIndicator.position = hit.point + Vector3.up * 0.02f;
                    groundIndicator.rotation = Quaternion.FromToRotation(Vector3.up, hit.normal);
                    float h = transform.position.y - hit.point.y;
                    float ringScale = Mathf.Clamp(1f + h * 0.08f, 1f, 3.5f);
                    groundIndicator.localScale = new Vector3(ringScale, 1f, ringScale);
                }
            }

            if (speedTrail != null)
            {
                speedTrail.emitting = CurrentSpeed >= trailSpeedThreshold;
            }
        }

        private void OnCollisionEnter(Collision collision)
        {
            float impactSpeed = collision.relativeVelocity.magnitude;

            CarController car = collision.gameObject.GetComponentInParent<CarController>();
            if (car != null)
            {
                Vector3 hitDir = (transform.position - car.transform.position).normalized;
                hitDir += Vector3.up * verticalPopFactor;
                hitDir.Normalize();

                float carSpeed = Vector3.Dot(car.Rb.linearVelocity, car.transform.forward);
                float force = Mathf.Max(14.0f, carSpeed * bumperHitMultiplier + 9.0f);
                _rb.AddForce(hitDir * force, ForceMode.Impulse);

                if (audioSource != null && carHitSound != null)
                {
                    audioSource.PlayOneShot(carHitSound, Mathf.Clamp01(impactSpeed / 25f));
                }
                OnBallHit?.Invoke(collision.contacts[0].point, impactSpeed);
            }
            else
            {
                if (impactSpeed > 4f)
                {
                    if (bounceParticles != null)
                    {
                        bounceParticles.transform.position = collision.contacts[0].point;
                        bounceParticles.Play();
                    }
                    if (audioSource != null && bounceSound != null)
                    {
                        audioSource.PlayOneShot(bounceSound, Mathf.Clamp01(impactSpeed / 35f));
                    }
                }
            }
        }

        private void OnTriggerEnter(Collider other)
        {
            string objName = other.gameObject.name;
            if (objName.Contains("Blue") || objName.Contains("Goal_Blue"))
            {
                OnGoalScored?.Invoke(1); // Orange scored in Blue goal
            }
            else if (objName.Contains("Orange") || objName.Contains("Goal_Orange"))
            {
                OnGoalScored?.Invoke(0); // Blue scored in Orange goal
            }
        }

        public void SetFrozen(bool frozen)
        {
            _isFrozen = frozen;
            if (_rb != null)
            {
                if (!frozen) _rb.isKinematic = false;
                if (!_rb.isKinematic)
                {
                    _rb.linearVelocity = Vector3.zero;
                    _rb.angularVelocity = Vector3.zero;
                }
                if (frozen) _rb.isKinematic = true;
            }
        }

        public void ResetKickoff()
        {
            transform.position = kickoffPosition;
            SetFrozen(false);
            if (_rb != null && !_rb.isKinematic)
            {
                _rb.linearVelocity = Vector3.zero;
                _rb.angularVelocity = Vector3.zero;
            }
        }
    }
}
