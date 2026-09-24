using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Projects a dynamic altitude indicator ring directly below the ball onto the arena floor,
    /// and controls high-speed motion streak particles/trails.
    /// </summary>
    public class BallTrailProjector : MonoBehaviour
    {
        [Header("=== GROUND INDICATOR ===")]
        public GameObject indicatorPrefab;
        public float baseRadius = 1.25f;
        public LayerMask groundLayers;

        [Header("=== SPEED TRAIL ===")]
        public TrailRenderer speedTrail;
        public float supersonicSpeed = 26f;
        public Color normalTrailColor = new Color(1f, 0.85f, 0.2f, 0.6f);
        public Color supersonicTrailColor = new Color(0.2f, 0.8f, 1f, 0.9f);

        private Transform _indicatorInstance;
        private MeshRenderer _innerDiscRenderer;
        private MeshRenderer _outerRingRenderer;
        private Rigidbody _rb;

        private void Start()
        {
            _rb = GetComponent<Rigidbody>();
            if (groundLayers.value == 0)
            {
                groundLayers = LayerMask.GetMask("Default", "Ground", "Arena");
            }

            CreateGroundIndicator();
        }

        private void CreateGroundIndicator()
        {
            GameObject indicator = new GameObject("BallGroundIndicator");
            _indicatorInstance = indicator.transform;

            // Inner Core Disc
            GameObject inner = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            inner.name = "InnerDisc";
            inner.transform.SetParent(_indicatorInstance, false);
            inner.transform.localScale = new Vector3(baseRadius * 0.9f, 0.01f, baseRadius * 0.9f);
            DestroyImmediate(inner.GetComponent<Collider>());
            _innerDiscRenderer = inner.GetComponent<MeshRenderer>();

            // Outer Altitude Ring
            GameObject outer = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            outer.name = "OuterRing";
            outer.transform.SetParent(_indicatorInstance, false);
            outer.transform.localScale = new Vector3(baseRadius * 1.5f, 0.008f, baseRadius * 1.5f);
            DestroyImmediate(outer.GetComponent<Collider>());
            _outerRingRenderer = outer.GetComponent<MeshRenderer>();

            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color") ?? Shader.Find("Mobile/Diffuse");
            if (unlit != null)
            {
                Material mInner = new Material(unlit);
                mInner.color = new Color(1f, 0.7f, 0f, 0.5f);
                _innerDiscRenderer.sharedMaterial = mInner;

                Material mOuter = new Material(unlit);
                mOuter.color = new Color(1f, 0.9f, 0.2f, 0.75f);
                _outerRingRenderer.sharedMaterial = mOuter;
            }
        }

        private void Update()
        {
            if (_indicatorInstance == null) return;

            // Project ray downward to arena surface
            if (Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit, 75f, groundLayers))
            {
                _indicatorInstance.position = hit.point + hit.normal * 0.025f;
                _indicatorInstance.rotation = Quaternion.FromToRotation(Vector3.up, hit.normal);

                float altitude = Mathf.Max(0f, transform.position.y - hit.point.y);
                float outerScale = baseRadius * (1.2f + altitude * 0.07f);
                _indicatorInstance.localScale = new Vector3(outerScale, 1f, outerScale);

                _indicatorInstance.gameObject.SetActive(true);
            }
            else
            {
                _indicatorInstance.gameObject.SetActive(false);
            }

            // Update trail color based on speed
            if (speedTrail != null && _rb != null)
            {
                float speed = _rb.linearVelocity.magnitude;
                speedTrail.emitting = speed > 10f;
                speedTrail.startColor = (speed >= supersonicSpeed) ? supersonicTrailColor : normalTrailColor;
            }
        }

        private void OnDestroy()
        {
            if (_indicatorInstance != null)
            {
                Destroy(_indicatorInstance.gameObject);
            }
        }
    }
}
