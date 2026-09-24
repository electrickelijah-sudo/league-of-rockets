using UnityEngine;

namespace RocketLeague
{
    public enum VehicleChassisType
    {
        ApexVanguard,    // Aerodynamic agile formula-rally striker
        ViperGT,         // Muscular heavy-hitting muscle coupe
        SpecterRS,       // Low-slung futuristic exotic hypercar
        IonPhantom,      // Cybernetic stealth interceptor with angular aero blades
        TitanJuggernaut  // Armored high-clearance off-road striker
    }

    /// <summary>
    /// Procedurally constructs authentic sports-car vehicle meshes and components:
    /// - Low, wide sports-car body
    /// - Front bumper & splitter
    /// - Rear bumper & diffuser
    /// - Hood & roof canopy
    /// - Side skirts & air intakes
    /// - Racing spoiler
    /// - 4 wheels with rubber tires & metallic rims
    /// - Emissive headlights & taillights
    /// - Rocket boost thruster nozzles & point light
    /// </summary>
    [ExecuteInEditMode]
    public class CarPrefabBuilder : MonoBehaviour
    {
        [Header("=== CHASSIS CONFIGURATION ===")]
        public VehicleChassisType chassisType = VehicleChassisType.ApexVanguard;
        public string wheelsId = "tuner_aero";

        [Header("=== DIMENSIONS (Meters) ===")]
        public float totalLength = 4.2f;
        public float totalWidth = 2.0f;
        public float totalHeight = 1.3f;
        public float wheelRadius = 0.4f;
        public float groundClearance = 0.25f;

        [Header("=== MATERIALS ===")]
        public Material bodyPaintMaterial;
        public Material secondaryPaintMaterial;
        public Material glassMaterial;
        public Material tireMaterial;
        public Material rimMaterial;
        public Material lightMaterial;
        public Material taillightMaterial;
        public Material exhaustMaterial;

        [ContextMenu("Build Procedural Sports Car")]
        public void BuildCar()
        {
            // Clear existing children
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                DestroyImmediate(transform.GetChild(i).gameObject);
            }

            float baseRideHeight = groundClearance + wheelRadius; // 0.65m

            // 1. Box Collider for physics hitbox (exact Rocket League Octane/Dominus size: 4.2m x 2.0m x 1.3m)
            BoxCollider mainCol = GetComponent<BoxCollider>();
            if (mainCol == null) mainCol = gameObject.AddComponent<BoxCollider>();
            mainCol.size = new Vector3(totalWidth, totalHeight, totalLength);
            mainCol.center = new Vector3(0, baseRideHeight + (totalHeight * 0.5f) - 0.15f, 0);

            // Container for visuals
            GameObject visualRoot = new GameObject("VisualModel");
            visualRoot.transform.SetParent(transform, false);

            // Create materials if null
            CreateDefaultMaterials();

            // Build chassis according to type
            switch (chassisType)
            {
                case VehicleChassisType.ApexVanguard:
                    BuildApexVanguard(visualRoot.transform, baseRideHeight);
                    break;
                case VehicleChassisType.ViperGT:
                    BuildViperGT(visualRoot.transform, baseRideHeight);
                    break;
                case VehicleChassisType.SpecterRS:
                    BuildSpecterRS(visualRoot.transform, baseRideHeight);
                    break;
                case VehicleChassisType.IonPhantom:
                    BuildIonPhantom(visualRoot.transform, baseRideHeight);
                    break;
                case VehicleChassisType.TitanJuggernaut:
                    BuildTitanJuggernaut(visualRoot.transform, baseRideHeight);
                    break;
            }

            // Build Wheels
            BuildWheels(visualRoot.transform, baseRideHeight);

            // Build Exhaust Thrusters & Boost Light
            BuildThrusters(visualRoot.transform, baseRideHeight);

            // Build Headlights & Taillights
            BuildLights(visualRoot.transform, baseRideHeight);

            Debug.Log($"<color=cyan>[CarPrefabBuilder]</color> Successfully generated {chassisType} vehicle!");
        }

        private void CreateDefaultMaterials()
        {
            Shader standardShader = Shader.Find("Standard") ?? Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Mobile/Diffuse");

            if (bodyPaintMaterial == null && standardShader != null)
            {
                bodyPaintMaterial = new Material(standardShader);
                bodyPaintMaterial.color = (chassisType == VehicleChassisType.ApexVanguard) ? new Color(0f, 0.45f, 1f) : new Color(1f, 0.35f, 0f);
                bodyPaintMaterial.SetFloat("_Metallic", 0.85f);
                bodyPaintMaterial.SetFloat("_Glossiness", 0.9f);
            }

            if (secondaryPaintMaterial == null && standardShader != null)
            {
                secondaryPaintMaterial = new Material(standardShader);
                secondaryPaintMaterial.color = new Color(0.12f, 0.14f, 0.18f);
                secondaryPaintMaterial.SetFloat("_Metallic", 0.5f);
                secondaryPaintMaterial.SetFloat("_Glossiness", 0.7f);
            }

            if (glassMaterial == null && standardShader != null)
            {
                glassMaterial = new Material(standardShader);
                glassMaterial.color = new Color(0.05f, 0.08f, 0.12f);
                glassMaterial.SetFloat("_Glossiness", 0.95f);
            }

            if (tireMaterial == null && standardShader != null)
            {
                tireMaterial = new Material(standardShader);
                tireMaterial.color = new Color(0.15f, 0.15f, 0.15f);
                tireMaterial.SetFloat("_Glossiness", 0.2f);
            }

            if (rimMaterial == null && standardShader != null)
            {
                rimMaterial = new Material(standardShader);
                rimMaterial.color = new Color(0.85f, 0.85f, 0.9f);
                rimMaterial.SetFloat("_Metallic", 0.95f);
                rimMaterial.SetFloat("_Glossiness", 0.95f);
            }

            if (lightMaterial == null && standardShader != null)
            {
                lightMaterial = new Material(standardShader);
                lightMaterial.color = new Color(0.8f, 0.95f, 1f);
                lightMaterial.EnableKeyword("_EMISSION");
                lightMaterial.SetColor("_EmissionColor", new Color(0.8f, 0.95f, 1f) * 2.5f);
            }

            if (taillightMaterial == null && standardShader != null)
            {
                taillightMaterial = new Material(standardShader);
                taillightMaterial.color = new Color(1f, 0.05f, 0.1f);
                taillightMaterial.EnableKeyword("_EMISSION");
                taillightMaterial.SetColor("_EmissionColor", new Color(1f, 0.05f, 0.1f) * 2.5f);
            }

            if (exhaustMaterial == null && standardShader != null)
            {
                exhaustMaterial = new Material(standardShader);
                exhaustMaterial.color = new Color(0.3f, 0.3f, 0.35f);
                exhaustMaterial.SetFloat("_Metallic", 0.9f);
            }
        }

        private void BuildApexVanguard(Transform root, float baseRideHeight)
        {
            // Lower Monocoque Body
            CreateMeshPart(root, "Body_Chassis", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.35f, 0), new Vector3(1.85f, 0.55f, 3.8f), bodyPaintMaterial);

            // Aerodynamic Tapered Hood
            CreateMeshPart(root, "Body_Hood", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.48f, 0.95f), new Vector3(1.65f, 0.32f, 1.7f), bodyPaintMaterial);

            // Cockpit Canopy (Dark Glass Dome)
            CreateMeshPart(root, "Cockpit_Canopy", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.78f, -0.2f), new Vector3(1.4f, 0.42f, 1.8f), glassMaterial);

            // Front Bumper Splitter
            CreateMeshPart(root, "Front_Splitter", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.18f, 2.05f), new Vector3(1.95f, 0.2f, 0.4f), secondaryPaintMaterial);

            // Side Skirts
            CreateMeshPart(root, "SideSkirt_Left", PrimitiveType.Cube, new Vector3(-0.95f, baseRideHeight + 0.22f, 0), new Vector3(0.15f, 0.25f, 2.8f), secondaryPaintMaterial);
            CreateMeshPart(root, "SideSkirt_Right", PrimitiveType.Cube, new Vector3(0.95f, baseRideHeight + 0.22f, 0), new Vector3(0.15f, 0.25f, 2.8f), secondaryPaintMaterial);

            // Dual GT Racing Spoiler
            CreateMeshPart(root, "Spoiler_Wing", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.98f, -1.75f), new Vector3(1.8f, 0.08f, 0.45f), secondaryPaintMaterial);
            CreateMeshPart(root, "Spoiler_Strut_L", PrimitiveType.Cube, new Vector3(-0.55f, baseRideHeight + 0.72f, -1.75f), new Vector3(0.08f, 0.45f, 0.12f), secondaryPaintMaterial);
            CreateMeshPart(root, "Spoiler_Strut_R", PrimitiveType.Cube, new Vector3(0.55f, baseRideHeight + 0.72f, -1.75f), new Vector3(0.08f, 0.45f, 0.12f), secondaryPaintMaterial);
        }

        private void BuildViperGT(Transform root, float baseRideHeight)
        {
            // Wide Muscle Body
            CreateMeshPart(root, "Body_Chassis", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.38f, 0), new Vector3(1.95f, 0.6f, 3.9f), bodyPaintMaterial);

            // Bulging Muscle Hood
            CreateMeshPart(root, "Body_Hood", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.55f, 1.0f), new Vector3(1.75f, 0.38f, 1.8f), bodyPaintMaterial);

            // Hood Scoop Air Intake
            CreateMeshPart(root, "Hood_Scoop", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.76f, 0.9f), new Vector3(0.65f, 0.14f, 0.8f), secondaryPaintMaterial);

            // Fastback Cabin Roof
            CreateMeshPart(root, "Cabin_Roof", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.82f, -0.3f), new Vector3(1.5f, 0.45f, 1.9f), glassMaterial);

            // Heavy Front Bumper Bullnose
            CreateMeshPart(root, "Front_Bumper", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.25f, 2.1f), new Vector3(1.98f, 0.35f, 0.35f), secondaryPaintMaterial);

            // Ducktail Rear Lip Spoiler
            CreateMeshPart(root, "Ducktail_Spoiler", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.75f, -1.95f), new Vector3(1.85f, 0.18f, 0.22f), secondaryPaintMaterial);
        }

        private void BuildSpecterRS(Transform root, float baseRideHeight)
        {
            // Ultra-Low Wedge Hypercar Chassis
            CreateMeshPart(root, "Body_Chassis", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.28f, 0), new Vector3(2.05f, 0.48f, 4.05f), bodyPaintMaterial);

            // Sharply Sloped Nose Cone
            CreateMeshPart(root, "Nose_Cone", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.35f, 1.35f), new Vector3(1.8f, 0.28f, 1.4f), bodyPaintMaterial);

            // Jet-Fighter Glass Bubble Cockpit
            CreateMeshPart(root, "Cockpit_Bubble", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.68f, -0.1f), new Vector3(1.35f, 0.42f, 1.85f), glassMaterial);

            // Carbon Front Splitter Canards
            CreateMeshPart(root, "Splitter_Canard_L", PrimitiveType.Cube, new Vector3(-0.98f, baseRideHeight + 0.18f, 1.95f), new Vector3(0.35f, 0.08f, 0.35f), secondaryPaintMaterial);
            CreateMeshPart(root, "Splitter_Canard_R", PrimitiveType.Cube, new Vector3(0.98f, baseRideHeight + 0.18f, 1.95f), new Vector3(0.35f, 0.08f, 0.35f), secondaryPaintMaterial);

            // Active Aero Rear Wing
            CreateMeshPart(root, "Active_Aero_Wing", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.88f, -1.9f), new Vector3(1.95f, 0.06f, 0.48f), secondaryPaintMaterial);
            CreateMeshPart(root, "Wing_Endplate_L", PrimitiveType.Cube, new Vector3(-1.0f, baseRideHeight + 0.88f, -1.9f), new Vector3(0.05f, 0.22f, 0.52f), secondaryPaintMaterial);
            CreateMeshPart(root, "Wing_Endplate_R", PrimitiveType.Cube, new Vector3(1.0f, baseRideHeight + 0.88f, -1.9f), new Vector3(0.05f, 0.22f, 0.52f), secondaryPaintMaterial);
        }

        private void BuildIonPhantom(Transform root, float baseRideHeight)
        {
            // Cybernetic Stealth Interceptor Body
            CreateMeshPart(root, "Body_Chassis", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.32f, 0), new Vector3(1.82f, 0.48f, 4.15f), bodyPaintMaterial);

            // Forward Sloped Faceted Nose
            CreateMeshPart(root, "Stealth_Nose", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.40f, 1.35f), new Vector3(1.65f, 0.3f, 1.55f), bodyPaintMaterial);

            // Angular Canopy Glass
            CreateMeshPart(root, "Stealth_Canopy", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.72f, -0.15f), new Vector3(1.22f, 0.38f, 1.75f), glassMaterial);

            // Forward-Swept Aero Blades
            CreateMeshPart(root, "AeroBlade_L", PrimitiveType.Cube, new Vector3(-0.95f, baseRideHeight + 0.25f, 1.6f), new Vector3(0.18f, 0.15f, 0.7f), secondaryPaintMaterial);
            CreateMeshPart(root, "AeroBlade_R", PrimitiveType.Cube, new Vector3(0.95f, baseRideHeight + 0.25f, 1.6f), new Vector3(0.18f, 0.15f, 0.7f), secondaryPaintMaterial);

            // Twin Vertical Tail Stabilizers
            CreateMeshPart(root, "TailFin_L", PrimitiveType.Cube, new Vector3(-0.68f, baseRideHeight + 0.82f, -1.85f), new Vector3(0.06f, 0.55f, 0.52f), secondaryPaintMaterial);
            CreateMeshPart(root, "TailFin_R", PrimitiveType.Cube, new Vector3(0.68f, baseRideHeight + 0.82f, -1.85f), new Vector3(0.06f, 0.55f, 0.52f), secondaryPaintMaterial);

            // Low-Profile Rear Diffuser
            CreateMeshPart(root, "Rear_Diffuser", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.16f, -2.02f), new Vector3(1.72f, 0.18f, 0.35f), secondaryPaintMaterial);
        }

        private void BuildTitanJuggernaut(Transform root, float baseRideHeight)
        {
            // Heavy Armored Striker Chassis
            CreateMeshPart(root, "Body_Chassis", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.42f, 0), new Vector3(2.1f, 0.65f, 4.0f), bodyPaintMaterial);

            // Elevated Truck Hood
            CreateMeshPart(root, "Heavy_Hood", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.68f, 1.05f), new Vector3(1.85f, 0.42f, 1.8f), bodyPaintMaterial);

            // Armored Truck Cabin
            CreateMeshPart(root, "Cabin_Roof", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.95f, -0.3f), new Vector3(1.6f, 0.52f, 1.8f), glassMaterial);

            // Heavy Front Bullbar / Brush Guard
            CreateMeshPart(root, "Front_Bullbar", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 0.38f, 2.15f), new Vector3(2.15f, 0.42f, 0.28f), secondaryPaintMaterial);

            // Reinforced Roof LED Light Bar
            CreateMeshPart(root, "Roof_LightBar", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 1.25f, -0.05f), new Vector3(1.4f, 0.12f, 0.18f), lightMaterial);

            // Heavy Tailgate Rollbar Structure
            CreateMeshPart(root, "Rollbar_L", PrimitiveType.Cube, new Vector3(-0.85f, baseRideHeight + 0.85f, -1.85f), new Vector3(0.12f, 0.52f, 0.12f), secondaryPaintMaterial);
            CreateMeshPart(root, "Rollbar_R", PrimitiveType.Cube, new Vector3(0.85f, baseRideHeight + 0.85f, -1.85f), new Vector3(0.12f, 0.52f, 0.12f), secondaryPaintMaterial);
            CreateMeshPart(root, "Rollbar_Cross", PrimitiveType.Cube, new Vector3(0, baseRideHeight + 1.1f, -1.85f), new Vector3(1.75f, 0.12f, 0.12f), secondaryPaintMaterial);
        }

        private void BuildWheels(Transform root, float baseRideHeight)
        {
            float halfBase = 1.3f;
            float halfSpace = 0.82f;
            float wheelWidth = 0.35f;

            Vector3[] wheelPos = new Vector3[]
            {
                new Vector3(-halfSpace, baseRideHeight,  halfBase), // FL
                new Vector3( halfSpace, baseRideHeight,  halfBase), // FR
                new Vector3(-halfSpace, baseRideHeight, -halfBase), // RL
                new Vector3( halfSpace, baseRideHeight, -halfBase)  // RR
            };

            string[] wheelNames = { "Wheel_FL", "Wheel_FR", "Wheel_RL", "Wheel_RR" };
            Transform[] anchors = new Transform[4];
            Transform[] renderers = new Transform[4];

            GameObject wheelGroup = new GameObject("Wheels");
            wheelGroup.transform.SetParent(root, false);

            WheelRotator rotator = GetComponent<WheelRotator>();
            if (rotator == null) rotator = gameObject.AddComponent<WheelRotator>();
            rotator.wheelRadius = wheelRadius;

            for (int i = 0; i < 4; i++)
            {
                // Wheel Anchor
                GameObject anchor = new GameObject(wheelNames[i] + "_Anchor");
                anchor.transform.SetParent(wheelGroup.transform, false);
                anchor.transform.localPosition = wheelPos[i];
                anchors[i] = anchor.transform;

                // Rubber Tire Cylinder
                GameObject tire = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                tire.name = wheelNames[i] + "_Tire";
                tire.transform.SetParent(anchor.transform, false);
                tire.transform.localRotation = Quaternion.Euler(0, 0, 90f);
                tire.transform.localScale = new Vector3(wheelRadius * 2f, wheelWidth * 0.5f, wheelRadius * 2f);
                DestroyImmediate(tire.GetComponent<Collider>());
                if (tireMaterial != null) tire.GetComponent<Renderer>().sharedMaterial = tireMaterial;
                renderers[i] = tire.transform;

                // Metallic Center Rim with design variation
                GameObject rim = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                rim.name = "Rim";
                rim.transform.SetParent(tire.transform, false);
                rim.transform.localPosition = new Vector3(0, 0.05f, 0);
                rim.transform.localScale = new Vector3(0.65f, 1.05f, 0.65f);
                DestroyImmediate(rim.GetComponent<Collider>());
                if (rimMaterial != null) rim.GetComponent<Renderer>().sharedMaterial = rimMaterial;

                if (wheelsId == "cyber_blade")
                {
                    // Neon ring overlay
                    GameObject neonRing = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    neonRing.name = "NeonRimRing";
                    neonRing.transform.SetParent(rim.transform, false);
                    neonRing.transform.localPosition = new Vector3(0, 0.08f, 0);
                    neonRing.transform.localScale = new Vector3(0.85f, 0.2f, 0.85f);
                    DestroyImmediate(neonRing.GetComponent<Collider>());
                    if (lightMaterial != null) neonRing.GetComponent<Renderer>().sharedMaterial = lightMaterial;
                }
                else if (wheelsId == "titan_heavy")
                {
                    // Heavy beadlock ring
                    GameObject beadlock = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    beadlock.name = "BeadlockRing";
                    beadlock.transform.SetParent(rim.transform, false);
                    beadlock.transform.localPosition = new Vector3(0, 0.06f, 0);
                    beadlock.transform.localScale = new Vector3(0.95f, 0.3f, 0.95f);
                    DestroyImmediate(beadlock.GetComponent<Collider>());
                    if (secondaryPaintMaterial != null) beadlock.GetComponent<Renderer>().sharedMaterial = secondaryPaintMaterial;
                }

                // Register to CarCustomizer if present
                CarCustomizer customizer = GetComponent<CarCustomizer>();
                if (customizer != null && !customizer.wheelRimRenderers.Contains(rim.GetComponent<MeshRenderer>()))
                {
                    customizer.wheelRimRenderers.Add(rim.GetComponent<MeshRenderer>());
                }

                // Assign to WheelRotator
                if (i == 0) rotator.frontLeftWheel = tire.transform;
                else if (i == 1) rotator.frontRightWheel = tire.transform;
                else if (i == 2) rotator.rearLeftWheel = tire.transform;
                else if (i == 3) rotator.rearRightWheel = tire.transform;
            }

            // Wire up CarController
            CarController car = GetComponent<CarController>();
            if (car != null)
            {
                car.wheelAnchors = anchors;
                car.wheelMeshRenderers = renderers;
                car.wheelRadius = wheelRadius;
                car.groundClearance = groundClearance;
            }
        }

        private void BuildThrusters(Transform root, float baseRideHeight)
        {
            GameObject thrusterGroup = new GameObject("ExhaustThrusters");
            thrusterGroup.transform.SetParent(root, false);

            float[] thrusterX = { -0.32f, 0.32f };
            foreach (float tx in thrusterX)
            {
                // Chrome nozzle
                GameObject nozzle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                nozzle.name = "Nozzle";
                nozzle.transform.SetParent(thrusterGroup.transform, false);
                nozzle.transform.localPosition = new Vector3(tx, baseRideHeight + 0.42f, -1.98f);
                nozzle.transform.localRotation = Quaternion.Euler(90f, 0, 0);
                nozzle.transform.localScale = new Vector3(0.24f, 0.2f, 0.24f);
                DestroyImmediate(nozzle.GetComponent<Collider>());
                if (exhaustMaterial != null) nozzle.GetComponent<Renderer>().sharedMaterial = exhaustMaterial;
            }

            // Boost Point Light
            GameObject bLight = new GameObject("BoostLight");
            bLight.transform.SetParent(thrusterGroup.transform, false);
            bLight.transform.localPosition = new Vector3(0, baseRideHeight + 0.45f, -2.1f);
            Light lightComp = bLight.AddComponent<Light>();
            lightComp.type = LightType.Point;
            lightComp.color = (chassisType == VehicleChassisType.ApexVanguard) ? new Color(0f, 0.8f, 1f) : new Color(1f, 0.45f, 0f);
            lightComp.range = 8f;
            lightComp.intensity = 0f; // enabled while boosting
        }

        private void BuildLights(Transform root, float baseRideHeight)
        {
            GameObject lightsGroup = new GameObject("Lights");
            lightsGroup.transform.SetParent(root, false);

            // Dual Headlights
            float[] hx = { -0.65f, 0.65f };
            foreach (float x in hx)
            {
                GameObject hl = GameObject.CreatePrimitive(PrimitiveType.Cube);
                hl.name = "Headlight";
                hl.transform.SetParent(lightsGroup.transform, false);
                hl.transform.localPosition = new Vector3(x, baseRideHeight + 0.42f, 2.02f);
                hl.transform.localScale = new Vector3(0.32f, 0.12f, 0.08f);
                DestroyImmediate(hl.GetComponent<Collider>());
                if (lightMaterial != null) hl.GetComponent<Renderer>().sharedMaterial = lightMaterial;
            }

            // Dual Taillights
            foreach (float x in hx)
            {
                GameObject tl = GameObject.CreatePrimitive(PrimitiveType.Cube);
                tl.name = "Taillight";
                tl.transform.SetParent(lightsGroup.transform, false);
                tl.transform.localPosition = new Vector3(x, baseRideHeight + 0.45f, -1.98f);
                tl.transform.localScale = new Vector3(0.28f, 0.1f, 0.06f);
                DestroyImmediate(tl.GetComponent<Collider>());
                if (taillightMaterial != null) tl.GetComponent<Renderer>().sharedMaterial = taillightMaterial;
            }
        }

        private GameObject CreateMeshPart(Transform parent, string name, PrimitiveType type, Vector3 localPos, Vector3 scale, Material mat)
        {
            GameObject part = GameObject.CreatePrimitive(type);
            part.name = name;
            part.transform.SetParent(parent, false);
            part.transform.localPosition = localPos;
            part.transform.localScale = scale;
            DestroyImmediate(part.GetComponent<Collider>());
            if (mat != null) part.GetComponent<Renderer>().sharedMaterial = mat;
            return part;
        }
    }
}
