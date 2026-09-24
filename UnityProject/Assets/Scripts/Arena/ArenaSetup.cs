using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Master Scene Setup and Spawner for the exact 100m x 80m Rocket League Arena.
    /// Places all 12 Small Boost Pads and 4 Large Boost Pads at exact coordinates,
    /// constructs the ball at (0, 1.25, 0), and positions all team cars.
    /// </summary>
    [ExecuteInEditMode]
    public class ArenaSetup : MonoBehaviour
    {
        [Header("=== PREFABS & REFERENCES ===")]
        public ArenaMeshBuilder meshBuilder;
        public GameObject carPrefab;
        public GameObject ballPrefab;

        [Header("=== EXACT BOOST PAD COORDINATES (3X SCALE) ===")]
        public readonly Vector3[] smallPadPositions = new Vector3[]
        {
            new Vector3(-105f, 0.3f, -75f),
            new Vector3(-105f, 0.3f,  75f),
            new Vector3( -45f, 0.3f, -90f),
            new Vector3( -45f, 0.3f,  90f),
            new Vector3(   0f, 0.3f, -75f),
            new Vector3(   0f, 0.3f,  75f),
            new Vector3(  45f, 0.3f, -90f),
            new Vector3(  45f, 0.3f,  90f),
            new Vector3( 105f, 0.3f, -75f),
            new Vector3( 105f, 0.3f,  75f),
            new Vector3( -75f, 0.3f,   0f),
            new Vector3(  75f, 0.3f,   0f)
        };

        public readonly Vector3[] largePadPositions = new Vector3[]
        {
            new Vector3(-126f, 0.45f, -96f),
            new Vector3(-126f, 0.45f,  96f),
            new Vector3( 126f, 0.45f, -96f),
            new Vector3( 126f, 0.45f,  96f)
        };

        [ContextMenu("Build Complete Arena Scene")]
        public void BuildCompleteScene()
        {
            // 1. Build Stadium Geometry
            if (meshBuilder == null) meshBuilder = GetComponentInChildren<ArenaMeshBuilder>();
            if (meshBuilder != null)
            {
                meshBuilder.BuildArena();
            }

            // 2. Build Boost Pads
            BuildAllBoostPads();

            // 3. Build Center Field Markings
            BuildCenterFieldMarkings();

            // 4. Build Ball
            BuildBall();

            Debug.Log("<color=green>[ArenaSetup]</color> Complete Rocket League arena setup constructed with exact dimensions!");
        }

        private void BuildAllBoostPads()
        {
            GameObject padHolder = transform.Find("BoostPads")?.gameObject;
            if (padHolder != null) DestroyImmediate(padHolder);

            padHolder = new GameObject("BoostPads");
            padHolder.transform.SetParent(transform, false);

            // Small Pads (Diameter 6m, Height 0.45m)
            for (int i = 0; i < smallPadPositions.Length; i++)
            {
                CreatePad(padHolder.transform, $"SmallPad_{i + 1}", smallPadPositions[i], BoostPad.PadType.SmallPad, 6f, 0.45f);
            }

            // Large Corner Pads (Diameter 12m, Height 0.6m)
            for (int i = 0; i < largePadPositions.Length; i++)
            {
                CreatePad(padHolder.transform, $"LargePad_Corner_{i + 1}", largePadPositions[i], BoostPad.PadType.LargeOrb, 12f, 0.6f);
            }
        }

        private void CreatePad(Transform parent, string name, Vector3 pos, BoostPad.PadType type, float diameter, float height)
        {
            GameObject padObj = new GameObject(name);
            padObj.transform.SetParent(parent, false);
            padObj.transform.position = pos;

            // Trigger cylinder collider
            SphereCollider trigger = padObj.AddComponent<SphereCollider>();
            trigger.isTrigger = true;
            trigger.radius = diameter * 0.6f;

            // Visual Disc
            GameObject disc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            disc.name = "Pad_Disc";
            disc.transform.SetParent(padObj.transform, false);
            disc.transform.localScale = new Vector3(diameter, height * 0.5f, diameter);
            disc.transform.localPosition = new Vector3(0, height * 0.5f, 0);
            DestroyImmediate(disc.GetComponent<Collider>());

            BoostPad pad = padObj.AddComponent<BoostPad>();
            pad.padType = type;
            pad.padDiameter = diameter;
            pad.padHeight = height;
            pad.activeVisuals = disc;

            if (type == BoostPad.PadType.LargeOrb)
            {
                // Floating rotating crystal
                GameObject crystal = GameObject.CreatePrimitive(PrimitiveType.Cube);
                crystal.name = "FloatingCrystal";
                crystal.transform.SetParent(padObj.transform, false);
                crystal.transform.localPosition = new Vector3(0, 3.6f, 0);
                crystal.transform.localScale = new Vector3(2.1f, 3.6f, 2.1f);
                crystal.transform.localRotation = Quaternion.Euler(45f, 45f, 0);
                DestroyImmediate(crystal.GetComponent<Collider>());
                pad.floatingCrystal = crystal.transform;
            }
        }

        private void BuildCenterFieldMarkings()
        {
            GameObject centerObj = transform.Find("CenterMarkings")?.gameObject;
            if (centerObj != null) DestroyImmediate(centerObj);

            centerObj = new GameObject("CenterMarkings");
            centerObj.transform.SetParent(transform, false);

            // Center Line: Length 240m, Width 0.45m across Z axis
            GameObject line = GameObject.CreatePrimitive(PrimitiveType.Cube);
            line.name = "CenterLine";
            line.transform.SetParent(centerObj.transform, false);
            line.transform.position = new Vector3(0, 0.31f, 0);
            line.transform.localScale = new Vector3(0.45f, 0.02f, 240f);
            DestroyImmediate(line.GetComponent<Collider>());

            // Center Circle: Radius 24m (Diameter 48m)
            GameObject circle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            circle.name = "CenterCircleDecal";
            circle.transform.SetParent(centerObj.transform, false);
            circle.transform.position = new Vector3(0, 0.305f, 0);
            circle.transform.localScale = new Vector3(48f, 0.01f, 48f);
            DestroyImmediate(circle.GetComponent<Collider>());

            Shader s = Shader.Find("Standard");
            if (s == null) s = Shader.Find("Universal Render Pipeline/Lit");
            if (s == null) s = Shader.Find("Mobile/Diffuse");
            Material goldLineMat = new Material(s);
            goldLineMat.color = new Color(0.92f, 0.75f, 0.35f, 0.75f);
            goldLineMat.EnableKeyword("_EMISSION");
            goldLineMat.SetColor("_EmissionColor", new Color(0.92f, 0.75f, 0.35f) * 1.2f);
            line.GetComponent<Renderer>().sharedMaterial = goldLineMat;
            circle.GetComponent<Renderer>().sharedMaterial = goldLineMat;
        }

        private void BuildBall()
        {
            GameObject ballObj = transform.Find("Ball")?.gameObject;
            if (ballObj != null) DestroyImmediate(ballObj);

            ballObj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            ballObj.name = "Ball";
            ballObj.transform.SetParent(transform, false);
            ballObj.transform.position = new Vector3(0f, 3.75f, 0f);
            ballObj.transform.localScale = new Vector3(7.5f, 7.5f, 7.5f); // 7.5m diameter, 3.75m radius (3x)

            SphereCollider col = ballObj.GetComponent<SphereCollider>();
            col.radius = 0.5f; // Radius 0.5 with scale 7.5 = 3.75m world radius

            Rigidbody rb = ballObj.AddComponent<Rigidbody>();
            rb.mass = 105f;

            BallController bc = ballObj.AddComponent<BallController>();
            bc.radius = 3.75f;
            bc.kickoffPosition = new Vector3(0f, 3.75f, 0f);
        }
    }
}
