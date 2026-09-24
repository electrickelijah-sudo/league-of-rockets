using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Procedural Rocket League Arena Generator in Unity.
    /// Builds authentic stadium geometry using 1 Unity unit = 1 meter:
    /// - Field: 100m Length x 80m Width x 0.1m Grass Height
    /// - Walls: 8m Height, 0.5m Thickness
    /// - Floor-to-Wall Curved Ramps: 8m Radius
    /// - Curved Corners: 12m Radius
    /// - Upper Curved Wall: Y = 8m to 12m
    /// - Transparent Dome: 110m L x 90m W x 20m H, 0.25m thickness
    /// - Goals: 20m W x 8m H x 8m D at X = -50m (Blue) and X = +50m (Orange)
    /// - Detection Volume: 19m W x 7m H x 7m D
    /// - All parameters fully editable in the Unity Inspector!
    /// </summary>
    [ExecuteInEditMode]
    public class ArenaMeshBuilder : MonoBehaviour
    {
        [Header("=== FIELD DIMENSIONS (3X SCALE) ===")]
        [Tooltip("Total field length along X-axis (Blue goal at -150, Orange at +150)")]
        public float fieldLength = 300f;

        [Tooltip("Total field width along Z-axis (-120 to +120)")]
        public float fieldWidth = 240f;

        [Tooltip("Playable grass height")]
        public float grassHeight = 0.3f;

        [Header("=== WALLS & CURVES (3X SCALE) ===")]
        [Tooltip("Vertical side wall height")]
        public float wallHeight = 24f;

        [Tooltip("Wall physical thickness")]
        public float wallThickness = 1.5f;

        [Tooltip("Floor to wall curved transition radius")]
        public float floorToWallRadius = 24f;

        [Tooltip("Curved corner radius")]
        public float cornerRadius = 36f;

        [Tooltip("Upper curved wall start height")]
        public float upperWallStartHeight = 24f;

        [Tooltip("Upper curved wall top height")]
        public float upperWallTopHeight = 36f;

        [Tooltip("Ceiling apex height")]
        public float ceilingHeight = 60f;

        [Tooltip("Number of curve segments for smooth ramps")]
        [Range(6, 24)]
        public int curveSegments = 12;

        [Header("=== GOALS (Centered on End Walls) (3X SCALE) ===")]
        public float goalWidth = 60f;
        public float goalHeight = 24f;
        public float goalDepth = 24f;
        public float postThickness = 2.25f;
        public float detectionWidth = 57f;
        public float detectionHeight = 21f;
        public float detectionDepth = 21f;

        [Header("=== CENTER MARKINGS (3X SCALE) ===")]
        public float centerCircleRadius = 24f;
        public float centerLineWidth = 0.45f;

        [Header("=== STADIUM & DOME (3X SCALE) ===")]
        public float domeLength = 330f;
        public float domeWidth = 270f;
        public float domeHeight = 60f;
        public float domeThickness = 0.75f;
        public float standOffset = 36f;
        public float standHeight = 30f;
        public Vector2 screenDimensions = new Vector2(36f, 21f);
        public float floodlightHeight = 60f;
        public float structuralBeamThickness = 2.25f;

        [Header("=== MATERIALS ===")]
        public Material grassMaterial;
        public Material wallMaterial;
        public Material glassDomeMaterial;
        public Material goalBlueMaterial;
        public Material goalOrangeMaterial;
        public Material stadiumMaterial;

        [Header("=== RENDERER REFERENCES ===")]
        public Renderer fieldTurfRenderer;
        public Renderer arenaDomeRenderer;
        public Renderer stadiumWallsRenderer;

        [ContextMenu("Build Arena")]
        public void BuildArena()
        {
            EnsureMaterials();

            // Clean existing procedural children
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                DestroyImmediate(transform.GetChild(i).gameObject);
            }

            // 1. Spawn High-Fidelity 3X Blender Sunset Stadium Model (mountains, grandstands, floodlights, screens)
            SpawnBlenderSunsetStadium();

            // 2. Build PhysX Driving Physics Ramps & Goal Volumes
            BuildQuarterPipeRamps();
            BuildCornerRamps();
            BuildWallsAndCeiling();
            BuildGoals();

            Debug.Log("<color=green>[ArenaMeshBuilder]</color> Successfully built 3X Sunset Stadium Arena!");
        }

        public void SpawnBlenderSunsetStadium()
        {
            GameObject prefab = null;
#if UNITY_EDITOR
            prefab = UnityEditor.AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/SunsetStadiumArena.fbx");
#endif
            if (prefab == null)
            {
                prefab = Resources.Load<GameObject>("SunsetStadiumArena");
            }

            if (prefab != null)
            {
                GameObject stadiumObj = Instantiate(prefab, transform, false);
                stadiumObj.name = "Blender_SunsetStadium_3X";
                stadiumObj.transform.localPosition = Vector3.zero;
                stadiumObj.transform.localRotation = Quaternion.identity;
                stadiumObj.transform.localScale = Vector3.one;

                ApplyStadiumTexturesAndColliders(stadiumObj);
            }
            else
            {
                BuildTurf();
                BuildDome();
            }
        }

        private void ApplyStadiumTexturesAndColliders(GameObject root)
        {
            Texture2D turfTex = LoadTexture("Assets/Art/Textures/turf_grass_unity_arena.png");
            Texture2D bannerTex = LoadTexture("Assets/Art/Textures/banner_unity6_physics.png");
            Texture2D turboTex = LoadTexture("Assets/Art/Textures/screen_turbo_boost.png");
            Texture2D unityTex = LoadTexture("Assets/Art/Textures/screen_unity_vertical.png");
            Texture2D lightTex = LoadTexture("Assets/Art/Textures/floodlight_fixture.png");
            Texture2D orangeSeatsTex = LoadTexture("Assets/Art/Textures/stadium_seats_orange.png");
            Texture2D blueSeatsTex = LoadTexture("Assets/Art/Textures/stadium_seats_blue.png");

            MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
            foreach (var mr in renderers)
            {
                string n = mr.gameObject.name;
                Material mat = mr.material;

                if (n.Contains("Playable_Turf"))
                {
                    if (turfTex != null) mat.mainTexture = turfTex;
                    mat.color = Color.white;
                    fieldTurfRenderer = mr;

                    MeshCollider mc = mr.gameObject.GetComponent<MeshCollider>();
                    if (mc == null) mc = mr.gameObject.AddComponent<MeshCollider>();
                }
                else if (n.Contains("Wireframe_Cage"))
                {
                    mat.color = new Color(0.15f, 1.0f, 0.45f);
                    mat.EnableKeyword("_EMISSION");
                    mat.SetColor("_EmissionColor", new Color(0.15f, 1.0f, 0.45f) * 2f);
                    arenaDomeRenderer = mr;
                }
                else if (n.Contains("FasciaBanner"))
                {
                    if (bannerTex != null)
                    {
                        mat.mainTexture = bannerTex;
                        mat.EnableKeyword("_EMISSION");
                        mat.SetColor("_EmissionColor", Color.white * 0.8f);
                    }
                }
                else if (n.Contains("TurboBoost"))
                {
                    if (turboTex != null)
                    {
                        mat.mainTexture = turboTex;
                        mat.EnableKeyword("_EMISSION");
                        mat.SetColor("_EmissionColor", new Color(0f, 0.85f, 1f) * 1.5f);
                    }
                }
                else if (n.Contains("UnityVertical"))
                {
                    if (unityTex != null)
                    {
                        mat.mainTexture = unityTex;
                        mat.EnableKeyword("_EMISSION");
                        mat.SetColor("_EmissionColor", new Color(0f, 0.7f, 1f) * 1.5f);
                    }
                }
                else if (n.Contains("FloodlightHead"))
                {
                    if (lightTex != null)
                    {
                        mat.mainTexture = lightTex;
                        mat.EnableKeyword("_EMISSION");
                        mat.SetColor("_EmissionColor", Color.white * 2.5f);
                    }
                }
                else if (n.Contains("LightBeam"))
                {
                    mat.color = new Color(0.9f, 0.95f, 1.0f, 0.12f);
                    mat.EnableKeyword("_EMISSION");
                    mat.SetColor("_EmissionColor", new Color(0.9f, 0.95f, 1.0f) * 0.5f);
                }
                else if (n.Contains("Seats_Orange"))
                {
                    if (orangeSeatsTex != null) mat.mainTexture = orangeSeatsTex;
                    mat.color = new Color(0.85f, 0.35f, 0.06f);
                }
                else if (n.Contains("Seats_Blue"))
                {
                    if (blueSeatsTex != null) mat.mainTexture = blueSeatsTex;
                    mat.color = new Color(0.08f, 0.40f, 0.85f);
                }
                else if (n.Contains("Mountain"))
                {
                    mat.color = new Color(0.08f, 0.10f, 0.14f);
                }
            }
        }

        private Texture2D LoadTexture(string path)
        {
#if UNITY_EDITOR
            Texture2D t = UnityEditor.AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (t != null) return t;
#endif
            string full = System.IO.Path.Combine(Application.dataPath, path.Replace("Assets/", ""));
            if (System.IO.File.Exists(full))
            {
                byte[] b = System.IO.File.ReadAllBytes(full);
                Texture2D tex = new Texture2D(2, 2);
                if (tex.LoadImage(b)) return tex;
            }
            return null;
        }

        private void BuildTurf()
        {
            GameObject turfObj = new GameObject("Playable_Turf");
            turfObj.transform.SetParent(transform, false);

            MeshFilter mf = turfObj.AddComponent<MeshFilter>();
            MeshRenderer mr = turfObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = grassMaterial;
            fieldTurfRenderer = mr;

            float halfX = (fieldLength * 0.5f) - floorToWallRadius;
            float halfZ = (fieldWidth * 0.5f) - floorToWallRadius;

            Mesh mesh = new Mesh { name = "TurfMesh" };
            Vector3[] verts = new Vector3[]
            {
                new Vector3(-halfX, grassHeight, -halfZ),
                new Vector3( halfX, grassHeight, -halfZ),
                new Vector3( halfX, grassHeight,  halfZ),
                new Vector3(-halfX, grassHeight,  halfZ)
            };
            Vector2[] uvs = new Vector2[]
            {
                new Vector2(0, 0),
                new Vector2(1, 0),
                new Vector2(1, 1),
                new Vector2(0, 1)
            };
            int[] tris = new int[] { 0, 2, 1, 0, 3, 2 };

            mesh.vertices = verts;
            mesh.uv = uvs;
            mesh.triangles = tris;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;

            BoxCollider col = turfObj.AddComponent<BoxCollider>();
            col.size = new Vector3(fieldLength, grassHeight * 2f, fieldWidth);
            col.center = new Vector3(0, 0, 0);
        }

        private void BuildQuarterPipeRamps()
        {
            float halfX = fieldLength * 0.5f;
            float halfZ = fieldWidth * 0.5f;
            float r = floorToWallRadius;

            // Straight section lengths between corner curves
            float straightXLen = fieldLength - (cornerRadius * 2f);
            float straightZLen = fieldWidth - (cornerRadius * 2f);

            // North Side Wall Ramp (+Z)
            CreateLinearRamp("Ramp_North_+Z",
                new Vector3(0, grassHeight, halfZ - r),
                Vector3.forward, Vector3.right, straightXLen, r, wallHeight);

            // South Side Wall Ramp (-Z)
            CreateLinearRamp("Ramp_South_-Z",
                new Vector3(0, grassHeight, -halfZ + r),
                Vector3.back, Vector3.right, straightXLen, r, wallHeight);

            // East End Wall Ramp (+X - Orange side, leaving gap for goal opening)
            float goalGapHalf = goalWidth * 0.5f;
            float sideWingZLen = (straightZLen - goalWidth) * 0.5f;

            if (sideWingZLen > 0.5f)
            {
                float zCenter = goalGapHalf + sideWingZLen * 0.5f;
                // East +Z wing
                CreateLinearRamp("Ramp_East_Wing_+Z",
                    new Vector3(halfX - r, grassHeight, zCenter),
                    Vector3.right, Vector3.forward, sideWingZLen, r, wallHeight);
                // East -Z wing
                CreateLinearRamp("Ramp_East_Wing_-Z",
                    new Vector3(halfX - r, grassHeight, -zCenter),
                    Vector3.right, Vector3.forward, sideWingZLen, r, wallHeight);

                // West +Z wing (Blue side)
                CreateLinearRamp("Ramp_West_Wing_+Z",
                    new Vector3(-halfX + r, grassHeight, zCenter),
                    Vector3.left, Vector3.forward, sideWingZLen, r, wallHeight);
                // West -Z wing
                CreateLinearRamp("Ramp_West_Wing_-Z",
                    new Vector3(-halfX + r, grassHeight, -zCenter),
                    Vector3.left, Vector3.forward, sideWingZLen, r, wallHeight);
            }
        }

        private void CreateLinearRamp(string name, Vector3 basePos, Vector3 wallDir, Vector3 spanDir, float length, float radius, float targetHeight)
        {
            GameObject rampObj = new GameObject(name);
            rampObj.transform.SetParent(transform, false);

            MeshFilter mf = rampObj.AddComponent<MeshFilter>();
            MeshRenderer mr = rampObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = wallMaterial;
            if (stadiumWallsRenderer == null) stadiumWallsRenderer = mr;

            Mesh mesh = new Mesh { name = name + "_Mesh" };
            List<Vector3> verts = new List<Vector3>();
            List<Vector2> uvs = new List<Vector2>();
            List<int> tris = new List<int>();

            float halfLen = length * 0.5f;

            for (int i = 0; i <= curveSegments; i++)
            {
                float t = (float)i / curveSegments;
                float angle = t * Mathf.PI * 0.5f; // 0 to 90 deg

                float dOffset = (1f - Mathf.Cos(angle)) * radius;
                float yOffset = Mathf.Sin(angle) * (targetHeight - grassHeight);

                Vector3 centerPt = basePos + wallDir * dOffset + Vector3.up * yOffset;

                verts.Add(centerPt - spanDir * halfLen);
                verts.Add(centerPt + spanDir * halfLen);

                uvs.Add(new Vector2(0, t));
                uvs.Add(new Vector2(1, t));

                if (i < curveSegments)
                {
                    int r0 = i * 2;
                    int r1 = (i + 1) * 2;

                    tris.Add(r0);
                    tris.Add(r1);
                    tris.Add(r0 + 1);

                    tris.Add(r0 + 1);
                    tris.Add(r1);
                    tris.Add(r1 + 1);
                }
            }

            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;

            MeshCollider mc = rampObj.AddComponent<MeshCollider>();
            mc.sharedMesh = mesh;
        }

        private void BuildCornerRamps()
        {
            // 4 Curved corner transitions (Radius = 12m)
            float cx = (fieldLength * 0.5f) - cornerRadius;
            float cz = (fieldWidth * 0.5f) - cornerRadius;

            CreateCornerMesh("Corner_NE", new Vector3(cx, grassHeight, cz), 0f);
            CreateCornerMesh("Corner_NW", new Vector3(-cx, grassHeight, cz), 90f);
            CreateCornerMesh("Corner_SW", new Vector3(-cx, grassHeight, -cz), 180f);
            CreateCornerMesh("Corner_SE", new Vector3(cx, grassHeight, -cz), 270f);
        }

        private void CreateCornerMesh(string name, Vector3 cornerCenter, float angleDeg)
        {
            GameObject cornerObj = new GameObject(name);
            cornerObj.transform.SetParent(transform, false);

            MeshFilter mf = cornerObj.AddComponent<MeshFilter>();
            MeshRenderer mr = cornerObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = wallMaterial;

            Mesh mesh = new Mesh { name = name + "_Mesh" };
            List<Vector3> verts = new List<Vector3>();
            List<Vector2> uvs = new List<Vector2>();
            List<int> tris = new List<int>();

            int radialSegments = 10;
            float baseAngle = angleDeg * Mathf.Deg2Rad;

            for (int r = 0; r <= curveSegments; r++)
            {
                float tR = (float)r / curveSegments;
                float verticalAngle = tR * Mathf.PI * 0.5f;

                float rDist = cornerRadius - (floorToWallRadius * Mathf.Cos(verticalAngle));
                float y = grassHeight + floorToWallRadius * Mathf.Sin(verticalAngle);

                for (int a = 0; a <= radialSegments; a++)
                {
                    float tA = (float)a / radialSegments;
                    float currentAngle = baseAngle + tA * Mathf.PI * 0.5f;

                    float x = cornerCenter.x + Mathf.Cos(currentAngle) * rDist;
                    float z = cornerCenter.z + Mathf.Sin(currentAngle) * rDist;

                    verts.Add(new Vector3(x, y, z));
                    uvs.Add(new Vector2(tA, tR));

                    if (r < curveSegments && a < radialSegments)
                    {
                        int row0 = r * (radialSegments + 1);
                        int row1 = (r + 1) * (radialSegments + 1);

                        tris.Add(row0 + a);
                        tris.Add(row1 + a);
                        tris.Add(row0 + a + 1);

                        tris.Add(row0 + a + 1);
                        tris.Add(row1 + a);
                        tris.Add(row1 + a + 1);
                    }
                }
            }

            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;

            MeshCollider mc = cornerObj.AddComponent<MeshCollider>();
            mc.sharedMesh = mesh;
        }

        private void BuildWallsAndCeiling()
        {
            float halfX = fieldLength * 0.5f;
            float halfZ = fieldWidth * 0.5f;

            // Side Walls (+Z and -Z)
            CreateWallCollider("Wall_+Z", new Vector3(0, wallHeight * 0.5f, halfZ + wallThickness * 0.5f), new Vector3(fieldLength, wallHeight, wallThickness));
            CreateWallCollider("Wall_-Z", new Vector3(0, wallHeight * 0.5f, -halfZ - wallThickness * 0.5f), new Vector3(fieldLength, wallHeight, wallThickness));

            // Upper curved walls (Y = 8 to 12)
            CreateWallCollider("UpperWall_+Z", new Vector3(0, 10f, halfZ - 1.5f), new Vector3(fieldLength, 4f, 0.5f));
            CreateWallCollider("UpperWall_-Z", new Vector3(0, 10f, -halfZ + 1.5f), new Vector3(fieldLength, 4f, 0.5f));

            // Ceiling Flat Boundary at Y = 20
            CreateWallCollider("Ceiling_Barrier", new Vector3(0, ceilingHeight + 0.25f, 0), new Vector3(fieldLength, 0.5f, fieldWidth));
        }

        private void CreateWallCollider(string name, Vector3 pos, Vector3 size)
        {
            GameObject wall = new GameObject(name);
            wall.transform.SetParent(transform, false);
            wall.transform.position = pos;

            BoxCollider col = wall.AddComponent<BoxCollider>();
            col.size = size;
        }

        private void BuildGoals()
        {
            float halfX = fieldLength * 0.5f;

            // Blue Goal at X = -50m
            CreateGoalStructure("Goal_Blue", new Vector3(-halfX, 0, 0), -1f, goalBlueMaterial);

            // Orange Goal at X = +50m
            CreateGoalStructure("Goal_Orange", new Vector3(halfX, 0, 0), 1f, goalOrangeMaterial);
        }

        private void CreateGoalStructure(string name, Vector3 openingPos, float xDirection, Material mat)
        {
            GameObject goalRoot = new GameObject(name);
            goalRoot.transform.SetParent(transform, false);
            goalRoot.transform.position = openingPos;

            // Posts: 0.75m thick, 8m tall
            float halfW = goalWidth * 0.5f;
            CreateBeam(goalRoot.transform, "Post_Left", new Vector3(0, goalHeight * 0.5f, -halfW), new Vector3(postThickness, goalHeight, postThickness), mat);
            CreateBeam(goalRoot.transform, "Post_Right", new Vector3(0, goalHeight * 0.5f, halfW), new Vector3(postThickness, goalHeight, postThickness), mat);
            CreateBeam(goalRoot.transform, "Crossbar", new Vector3(0, goalHeight - (postThickness * 0.5f), 0), new Vector3(postThickness, postThickness, goalWidth), mat);

            // Emissive Neon Accent Beacons along goal posts and crossbar
            float neonThickness = 0.15f;
            float neonInset = (postThickness * 0.5f) + 0.05f;
            Color neonColor = xDirection < 0 ? new Color(0f, 0.85f, 1f) : new Color(1f, 0.45f, 0f);
            CreateEmissiveBeam(goalRoot.transform, "Neon_Left", new Vector3(-xDirection * neonInset, goalHeight * 0.5f, -halfW), new Vector3(neonThickness, goalHeight, neonThickness), neonColor);
            CreateEmissiveBeam(goalRoot.transform, "Neon_Right", new Vector3(-xDirection * neonInset, goalHeight * 0.5f, halfW), new Vector3(neonThickness, goalHeight, neonThickness), neonColor);
            CreateEmissiveBeam(goalRoot.transform, "Neon_Crossbar", new Vector3(-xDirection * neonInset, goalHeight - (postThickness * 0.5f), 0), new Vector3(neonThickness, neonThickness, goalWidth), neonColor);

            // Emissive Goal Interior Lighting
            GameObject goalLightObj = new GameObject("Goal_Interior_Light");
            goalLightObj.transform.SetParent(goalRoot.transform, false);
            goalLightObj.transform.localPosition = new Vector3(xDirection * 3f, goalHeight * 0.6f, 0);
            Light gLight = goalLightObj.AddComponent<Light>();
            gLight.type = LightType.Point;
            gLight.color = neonColor;
            gLight.intensity = 2.5f;
            gLight.range = 24f;

            // Goal Interior Back Wall: 8m deep
            Vector3 backWallPos = new Vector3(xDirection * goalDepth, goalHeight * 0.5f, 0);
            CreateBeam(goalRoot.transform, "BackWall", backWallPos, new Vector3(0.5f, goalHeight, goalWidth), mat);

            // Goal Interior Side Walls & Roof
            CreateBeam(goalRoot.transform, "GoalSide_-Z", new Vector3(xDirection * goalDepth * 0.5f, goalHeight * 0.5f, -halfW), new Vector3(goalDepth, goalHeight, 0.5f), mat);
            CreateBeam(goalRoot.transform, "GoalSide_+Z", new Vector3(xDirection * goalDepth * 0.5f, goalHeight * 0.5f, halfW), new Vector3(goalDepth, goalHeight, 0.5f), mat);
            CreateBeam(goalRoot.transform, "GoalRoof", new Vector3(xDirection * goalDepth * 0.5f, goalHeight, 0), new Vector3(goalDepth, 0.5f, goalWidth), mat);

            // Goal Detection Volume (Width: 19m, Height: 7m, Depth: 7m)
            string volName = "GoalDetectionVolume_" + (xDirection < 0 ? "Blue" : "Orange");
            GameObject detectObj = new GameObject(volName);
            detectObj.transform.SetParent(goalRoot.transform, false);
            detectObj.transform.localPosition = new Vector3(xDirection * (detectionDepth * 0.5f + 0.5f), detectionHeight * 0.5f, 0);

            BoxCollider detectCol = detectObj.AddComponent<BoxCollider>();
            detectCol.isTrigger = true;
            detectCol.size = new Vector3(detectionDepth, detectionHeight, detectionWidth);
        }

        private void CreateBeam(Transform parent, string name, Vector3 localPos, Vector3 size, Material mat)
        {
            GameObject beam = GameObject.CreatePrimitive(PrimitiveType.Cube);
            beam.name = name;
            beam.transform.SetParent(parent, false);
            beam.transform.localPosition = localPos;
            beam.transform.localScale = size;
            if (mat != null) beam.GetComponent<Renderer>().sharedMaterial = mat;
            else if (stadiumMaterial != null) beam.GetComponent<Renderer>().sharedMaterial = stadiumMaterial;
        }

        private void CreateEmissiveBeam(Transform parent, string name, Vector3 localPos, Vector3 size, Color emissiveColor)
        {
            GameObject beam = GameObject.CreatePrimitive(PrimitiveType.Cube);
            beam.name = name;
            beam.transform.SetParent(parent, false);
            beam.transform.localPosition = localPos;
            beam.transform.localScale = size;
            beam.GetComponent<Renderer>().sharedMaterial = CreatePBRMaterial("EmissiveBeamMat", emissiveColor, 0.2f, 0.1f, emissiveColor * 2.5f);
        }

        private void BuildDome()
        {
            GameObject domeObj = new GameObject("Transparent_Dome");
            domeObj.transform.SetParent(transform, false);

            MeshFilter mf = domeObj.AddComponent<MeshFilter>();
            MeshRenderer mr = domeObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = glassDomeMaterial;
            arenaDomeRenderer = mr;

            Mesh mesh = new Mesh { name = "DomeMesh" };
            List<Vector3> verts = new List<Vector3>();
            List<Vector2> uvs = new List<Vector2>();
            List<int> tris = new List<int>();

            int latSegments = 16;
            int lonSegments = 24;

            float hX = domeLength * 0.5f;
            float hZ = domeWidth * 0.5f;

            for (int lat = 0; lat <= latSegments; lat++)
            {
                float tLat = (float)lat / latSegments;
                float theta = tLat * Mathf.PI * 0.5f; // 0 to 90 deg
                float y = Mathf.Sin(theta) * domeHeight;
                float ringScale = Mathf.Cos(theta);

                for (int lon = 0; lon <= lonSegments; lon++)
                {
                    float tLon = (float)lon / lonSegments;
                    float phi = tLon * Mathf.PI * 2f;

                    float x = Mathf.Cos(phi) * hX * ringScale;
                    float z = Mathf.Sin(phi) * hZ * ringScale;

                    verts.Add(new Vector3(x, y, z));
                    uvs.Add(new Vector2(tLon, tLat));

                    if (lat < latSegments && lon < lonSegments)
                    {
                        int row0 = lat * (lonSegments + 1);
                        int row1 = (lat + 1) * (lonSegments + 1);

                        tris.Add(row0 + lon);
                        tris.Add(row1 + lon);
                        tris.Add(row0 + lon + 1);

                        tris.Add(row0 + lon + 1);
                        tris.Add(row1 + lon);
                        tris.Add(row1 + lon + 1);
                    }
                }
            }

            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;
        }

        private void BuildStadiumExterior()
        {
            GameObject stadiumRoot = new GameObject("Stadium_Exterior");
            stadiumRoot.transform.SetParent(transform, false);

            float standZ = (fieldWidth * 0.5f) + standOffset;
            float standX = (fieldLength * 0.5f) + standOffset;

            // Tiered Spectator Grandstands (5 tiers)
            int tiers = 5;
            for (int t = 0; t < tiers; t++)
            {
                float tierY = (t + 1) * (standHeight / tiers);
                float tierDepth = 2.5f;
                float offsetOut = t * tierDepth;

                // North & South Stands
                CreateBeam(stadiumRoot.transform, $"Stands_North_T{t}", new Vector3(0, tierY * 0.5f, standZ + offsetOut), new Vector3(fieldLength + 24f, tierY, tierDepth), stadiumMaterial);
                CreateBeam(stadiumRoot.transform, $"Stands_South_T{t}", new Vector3(0, tierY * 0.5f, -standZ - offsetOut), new Vector3(fieldLength + 24f, tierY, tierDepth), stadiumMaterial);

                // East & West Stands
                CreateBeam(stadiumRoot.transform, $"Stands_East_T{t}", new Vector3(standX + offsetOut, tierY * 0.5f, 0), new Vector3(tierDepth, tierY, fieldWidth + 24f), stadiumMaterial);
                CreateBeam(stadiumRoot.transform, $"Stands_West_T{t}", new Vector3(-standX - offsetOut, tierY * 0.5f, 0), new Vector3(tierDepth, tierY, fieldWidth + 24f), stadiumMaterial);
            }

            // Large Jumbotron Screens (12m x 7m) with glowing team border trim
            CreateBeam(stadiumRoot.transform, "Jumbotron_North", new Vector3(0, 16f, standZ + 4f), new Vector3(screenDimensions.x, screenDimensions.y, 0.5f), stadiumMaterial);
            CreateEmissiveBeam(stadiumRoot.transform, "Jumbotron_North_Trim", new Vector3(0, 16f, standZ + 3.7f), new Vector3(screenDimensions.x + 0.5f, screenDimensions.y + 0.5f, 0.1f), new Color(0f, 0.8f, 1f));

            CreateBeam(stadiumRoot.transform, "Jumbotron_South", new Vector3(0, 16f, -standZ - 4f), new Vector3(screenDimensions.x, screenDimensions.y, 0.5f), stadiumMaterial);
            CreateEmissiveBeam(stadiumRoot.transform, "Jumbotron_South_Trim", new Vector3(0, 16f, -standZ - 3.7f), new Vector3(screenDimensions.x + 0.5f, screenDimensions.y + 0.5f, 0.1f), new Color(1f, 0.45f, 0f));

            // 4 Traditional Stone & Vermilion Lantern Pylons with warm spotlights
            BuildLanternTower(stadiumRoot.transform, "LanternTower_NE", new Vector3(standX + 6f, 0, standZ + 6f));
            BuildLanternTower(stadiumRoot.transform, "LanternTower_NW", new Vector3(-standX - 6f, 0, standZ + 6f));
            BuildLanternTower(stadiumRoot.transform, "LanternTower_SE", new Vector3(standX + 6f, 0, -standZ - 6f));
            BuildLanternTower(stadiumRoot.transform, "LanternTower_SW", new Vector3(-standX - 6f, 0, -standZ - 6f));

            // Misty Mountain Valley Peaks surrounding the temple sanctuary
            BuildMistyMountainPeaks(stadiumRoot.transform);
        }

        private void BuildLanternTower(Transform parent, string name, Vector3 pos)
        {
            GameObject tower = new GameObject(name);
            tower.transform.SetParent(parent, false);
            tower.transform.position = pos;

            // Stone base pedestal
            CreateBeam(tower.transform, "Base", new Vector3(0, 2f, 0), new Vector3(4f, 4f, 4f), templeStoneMat);
            // Vermilion timber shaft
            CreateBeam(tower.transform, "Shaft", new Vector3(0, 11f, 0), new Vector3(2f, 14f, 2f), templeRedMat);
            // Glowing shoji lantern cage
            CreateBeam(tower.transform, "Lantern", new Vector3(0, 20f, 0), new Vector3(4.5f, 5f, 4.5f), lanternGlowMat);
            // Flared tile pagoda roof on top
            CreatePagodaRoof(tower.transform, new Vector3(0, 22.5f, 0), 7f, 2.5f);
            // Gold spire
            CreateBeam(tower.transform, "Finial", new Vector3(0, 25.5f, 0), new Vector3(0.6f, 3f, 0.6f), templeGoldMat);

            // Spotlight pointing down to field center
            GameObject lightObj = new GameObject("Lantern_Spot");
            lightObj.transform.SetParent(tower.transform, false);
            lightObj.transform.localPosition = new Vector3(0, 20f, 0);
            lightObj.transform.LookAt(Vector3.zero);

            Light spot = lightObj.AddComponent<Light>();
            spot.type = LightType.Spot;
            spot.color = new Color(1f, 0.88f, 0.65f);
            spot.intensity = 3.5f;
            spot.range = 160f;
            spot.spotAngle = 65f;
            spot.shadows = LightShadows.Soft;
        }

        private void BuildMistyMountainPeaks(Transform parent)
        {
            GameObject mountainRoot = new GameObject("Forbidden_Mountain_Ridges");
            mountainRoot.transform.SetParent(parent, false);

            Material mountainMat = CreatePBRMaterial("Mat_TwilightMountain", new Color(0.14f, 0.12f, 0.24f), 0.9f, 0.05f);
            Material pineMat = CreatePBRMaterial("Mat_DistantPine", new Color(0.08f, 0.16f, 0.10f), 0.85f, 0.02f);

            // Ring of 16 natural mountain ridges surrounding the temple sanctuary
            Vector3[] peakPositions = new Vector3[]
            {
                new Vector3(-120f, 0, -135f),
                new Vector3(-70f, 0, -150f),
                new Vector3(-10f, 0, -160f),
                new Vector3(50f, 0, -150f),
                new Vector3(110f, 0, -135f),
                new Vector3(150f, 0, -70f),
                new Vector3(160f, 0, 0f),
                new Vector3(150f, 0, 70f),
                new Vector3(110f, 0, 135f),
                new Vector3(50f, 0, 150f),
                new Vector3(-10f, 0, 160f),
                new Vector3(-70f, 0, 150f),
                new Vector3(-120f, 0, 135f),
                new Vector3(-150f, 0, 70f),
                new Vector3(-160f, 0, 0f),
                new Vector3(-150f, 0, -70f)
            };

            float[] peakHeights = new float[] { 85f, 115f, 95f, 125f, 90f, 85f, 110f, 95f, 120f, 90f, 115f, 85f, 105f, 90f, 120f, 95f };
            float[] peakWidths  = new float[] { 75f, 95f,  80f, 105f, 75f, 70f, 90f,  80f, 100f, 75f, 95f,  75f, 85f,  70f, 100f, 80f };

            for (int i = 0; i < peakPositions.Length; i++)
            {
                Vector3 basePos = peakPositions[i];
                float h = peakHeights[i];
                float w = peakWidths[i];

                CreateJaggedMountain(mountainRoot.transform, $"Mountain_{i}", basePos, w, h, mountainMat);

                for (int p = 0; p < 3; p++)
                {
                    float angle = (i * 0.4f + p * 1.8f);
                    Vector3 pinePos = basePos + new Vector3(Mathf.Sin(angle) * (w * 0.42f), 0, Mathf.Cos(angle) * (w * 0.42f));
                    CreateDistantPineTree(mountainRoot.transform, pinePos, 1.4f + p * 0.35f, pineMat);
                }
            }
        }

        private void CreateJaggedMountain(Transform parent, string name, Vector3 basePos, float width, float height, Material rockMat)
        {
            GameObject mtnObj = new GameObject(name);
            mtnObj.transform.SetParent(parent, false);
            mtnObj.transform.localPosition = basePos;

            MeshFilter mf = mtnObj.AddComponent<MeshFilter>();
            MeshRenderer mr = mtnObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = rockMat;

            Mesh mesh = new Mesh { name = name + "_Mesh" };
            int sides = 8;
            List<Vector3> verts = new List<Vector3>();
            List<int> tris = new List<int>();

            // Apex peak
            verts.Add(new Vector3(0, height, 0));

            // Mid tier ridge (shoulder)
            float midH = height * 0.55f;
            float midR = width * 0.42f;
            for (int s = 0; s < sides; s++)
            {
                float a = (float)s / sides * Mathf.PI * 2f;
                float jitter = ((s % 2 == 0) ? 1.15f : 0.88f);
                verts.Add(new Vector3(Mathf.Cos(a) * midR * jitter, midH, Mathf.Sin(a) * midR * jitter));
            }

            // Base footprint
            for (int s = 0; s < sides; s++)
            {
                float a = (float)s / sides * Mathf.PI * 2f;
                float jitter = ((s % 3 == 0) ? 1.18f : 0.92f);
                verts.Add(new Vector3(Mathf.Cos(a) * width * 0.5f * jitter, 0, Mathf.Sin(a) * width * 0.5f * jitter));
            }

            // Top cap triangles (Apex to shoulder)
            for (int s = 0; s < sides; s++)
            {
                int next = (s + 1) % sides;
                tris.Add(0);
                tris.Add(1 + s);
                tris.Add(1 + next);
            }

            // Mid to base quads (shoulder to base)
            for (int s = 0; s < sides; s++)
            {
                int next = (s + 1) % sides;
                int top0 = 1 + s;
                int top1 = 1 + next;
                int bot0 = 1 + sides + s;
                int bot1 = 1 + sides + next;

                tris.Add(top0);
                tris.Add(bot0);
                tris.Add(top1);

                tris.Add(top1);
                tris.Add(bot0);
                tris.Add(bot1);
            }

            mesh.SetVertices(verts);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;
        }

        private void CreateDistantPineTree(Transform parent, Vector3 pos, float scale, Material pineMat)
        {
            GameObject tree = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            tree.name = "PineTree";
            tree.transform.SetParent(parent, false);
            tree.transform.localPosition = pos + new Vector3(0, 5f * scale, 0);
            tree.transform.localScale = new Vector3(1.5f * scale, 5f * scale, 1.5f * scale);
            if (tree.GetComponent<Collider>() != null) DestroyImmediate(tree.GetComponent<Collider>());
            tree.GetComponent<Renderer>().sharedMaterial = pineMat;
        }

        #region Forbidden Temple Procedural Architecture

        private Material templeRedMat;
        private Material templeRoofMat;
        private Material templeStoneMat;
        private Material templeGoldMat;
        private Material lanternGlowMat;
        private Material sakuraBarkMat;
        private Material sakuraBlossomMat;
        private Material sakuraBlossomDeepMat;

        private void InitTempleMaterials()
        {
            if (templeRedMat == null)
                templeRedMat = CreatePBRMaterial("Temple_RedWood", new Color(0.85f, 0.12f, 0.08f), 0.45f, 0.05f);
            if (templeRoofMat == null)
                templeRoofMat = CreatePBRMaterial("Temple_DarkTile", new Color(0.12f, 0.14f, 0.18f), 0.35f, 0.15f);
            if (templeStoneMat == null)
                templeStoneMat = CreatePBRMaterial("Temple_GraniteStone", new Color(0.28f, 0.30f, 0.35f), 0.75f, 0.05f);
            if (templeGoldMat == null)
                templeGoldMat = CreatePBRMaterial("Temple_PolishedGold", new Color(1.0f, 0.82f, 0.22f), 0.25f, 0.85f, new Color(0.4f, 0.3f, 0.05f));
            if (lanternGlowMat == null)
                lanternGlowMat = CreatePBRMaterial("Temple_ShojiGlow", new Color(1.0f, 0.88f, 0.55f), 0.5f, 0f, new Color(1.0f, 0.8f, 0.4f) * 2.5f);
            if (sakuraBarkMat == null)
                sakuraBarkMat = CreatePBRMaterial("Sakura_TwistedBark", new Color(0.22f, 0.16f, 0.12f), 0.85f, 0.02f);
            if (sakuraBlossomMat == null)
                sakuraBlossomMat = CreatePBRMaterial("Sakura_BlossomPink", new Color(1.0f, 0.65f, 0.78f), 0.82f, 0f, new Color(0.35f, 0.15f, 0.22f));
            if (sakuraBlossomDeepMat == null)
                sakuraBlossomDeepMat = CreatePBRMaterial("Sakura_BlossomDeepRose", new Color(0.92f, 0.42f, 0.62f), 0.82f, 0f, new Color(0.3f, 0.1f, 0.18f));
        }

        private Material CreatePBRMaterial(string name, Color color, float roughness, float metallic, Color? emission = null)
        {
            Shader shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) shader = Shader.Find("Mobile/Diffuse");
            Material mat = new Material(shader);
            mat.name = name;
            mat.color = color;
            if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", 1f - roughness);
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", 1f - roughness);
            if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);
            if (emission.HasValue && emission.Value != Color.black)
            {
                mat.EnableKeyword("_EMISSION");
                if (mat.HasProperty("_EmissionColor")) mat.SetColor("_EmissionColor", emission.Value);
            }
            return mat;
        }

        private void EnsureMaterials()
        {
            InitTempleMaterials();

            if (grassMaterial == null)
            {
                grassMaterial = CreatePBRMaterial("Mat_TempleCourtyardTurf", Color.white, 0.75f, 0.05f);
                grassMaterial.mainTexture = GenerateForbiddenTempleTurfTexture();
            }
            if (wallMaterial == null)
            {
                wallMaterial = CreatePBRMaterial("Mat_TempleWallRamp", new Color(0.12f, 0.16f, 0.20f), 0.65f, 0.1f);
            }
            if (glassDomeMaterial == null)
            {
                glassDomeMaterial = CreatePBRMaterial("Mat_TempleDomeGlass", new Color(0.55f, 0.35f, 0.65f, 0.15f), 0.1f, 0.05f);
            }
            if (stadiumMaterial == null)
            {
                stadiumMaterial = CreatePBRMaterial("Mat_TempleTerraceStone", new Color(0.20f, 0.22f, 0.26f), 0.8f, 0.05f);
            }
            if (goalBlueMaterial == null)
            {
                goalBlueMaterial = CreatePBRMaterial("Mat_GoalBlue", new Color(0f, 0.75f, 1f), 0.2f, 0.1f, new Color(0f, 0.85f, 1f) * 2f);
            }
            if (goalOrangeMaterial == null)
            {
                goalOrangeMaterial = CreatePBRMaterial("Mat_GoalOrange", new Color(1f, 0.42f, 0.05f), 0.2f, 0.1f, new Color(1f, 0.45f, 0.05f) * 2f);
            }
        }

        private Texture2D GenerateForbiddenTempleTurfTexture()
        {
            int width = 512;
            int height = 512;
            Texture2D tex = new Texture2D(width, height, TextureFormat.RGBA32, true);
            Color[] pixels = new Color[width * height];

            Color slateBase = new Color(0.08f, 0.11f, 0.14f);      // Dark slate court
            Color slateTile = new Color(0.12f, 0.15f, 0.18f);      // Slate flagstone
            Color mossGreen = new Color(0.06f, 0.20f, 0.12f);      // Garden moss borders
            Color goldTrim  = new Color(0.92f, 0.75f, 0.35f);      // Courtyard gold lines
            Color zenRingCol = new Color(0.20f, 0.45f, 0.50f);     // Subtle Zen concentric ripples

            for (int y = 0; y < height; y++)
            {
                float v = (float)y / height;
                for (int x = 0; x < width; x++)
                {
                    float u = (float)x / width;

                    int tileX = (int)(u * 32);
                    int tileY = (int)(v * 32);
                    bool isGrout = (int)(u * 32 * 16) % 16 == 0 || (int)(v * 32 * 16) % 16 == 0;

                    float nuance = ((tileX + tileY) % 2 == 0) ? 1.05f : 0.95f;
                    Color col = Color.Lerp(slateBase, slateTile, nuance - 0.9f);
                    if (isGrout) col = slateBase * 0.75f;

                    float edgeDist = Mathf.Min(Mathf.Min(u, 1f - u), Mathf.Min(v, 1f - v));
                    if (edgeDist < 0.08f)
                    {
                        float mossBlend = 1f - (edgeDist / 0.08f);
                        col = Color.Lerp(col, mossGreen, mossBlend * 0.85f);
                    }

                    if (Mathf.Abs(u - 0.5f) < 0.005f)
                    {
                        col = goldTrim;
                    }

                    float dx = (u - 0.5f) * 1.25f;
                    float dy = (v - 0.5f);
                    float distCenter = Mathf.Sqrt(dx * dx + dy * dy);
                    if (Mathf.Abs(distCenter - 0.14f) < 0.005f)
                    {
                        col = goldTrim;
                    }

                    for (int r = 1; r <= 5; r++)
                    {
                        float ringRadius = r * 0.06f;
                        if (Mathf.Abs(distCenter - ringRadius) < 0.0035f)
                        {
                            col = Color.Lerp(col, zenRingCol, 0.6f);
                        }
                    }

                    pixels[y * width + x] = col;
                }
            }

            tex.SetPixels(pixels);
            tex.Apply();
            tex.wrapMode = TextureWrapMode.Clamp;
            tex.filterMode = FilterMode.Bilinear;
            return tex;
        }

        private void BuildForbiddenTempleLandmarks()
        {
            GameObject templeRoot = new GameObject("Forbidden_Temple_Structures");
            templeRoot.transform.SetParent(transform, false);

            InitTempleMaterials();

            // 1. Pagodas (Majestic multi-tier towers flanking the stadium terraces)
            CreatePagoda(templeRoot.transform, new Vector3(-38f, 0, -52f), 5, 13f, 4.4f);
            CreatePagoda(templeRoot.transform, new Vector3(38f, 0, 52f), 5, 13f, 4.4f);
            CreatePagoda(templeRoot.transform, new Vector3(-38f, 0, 52f), 5, 13f, 4.4f);
            CreatePagoda(templeRoot.transform, new Vector3(38f, 0, -52f), 5, 13f, 4.4f);

            // 2. Red Arched Moon Bridges spanning above both goals
            CreateMoonBridge(templeRoot.transform, new Vector3(-fieldLength * 0.5f, 0, 0), -1f);
            CreateMoonBridge(templeRoot.transform, new Vector3(fieldLength * 0.5f, 0, 0), 1f);

            // 3. Sacred Red Torii Gates at side midfield
            float halfW = fieldWidth * 0.5f;
            CreateToriiGate(templeRoot.transform, new Vector3(0, 0, -halfW - 8f), 0f, 1.25f);
            CreateToriiGate(templeRoot.transform, new Vector3(0, 0, halfW + 8f), 180f, 1.25f);

            // 4. Carved Stone Guardian Lions flanking the gates
            CreateGuardianLion(templeRoot.transform, new Vector3(-22f, 0, -halfW - 5f), 45f);
            CreateGuardianLion(templeRoot.transform, new Vector3(22f, 0, -halfW - 5f), -45f);
            CreateGuardianLion(templeRoot.transform, new Vector3(-22f, 0, halfW + 5f), 135f);
            CreateGuardianLion(templeRoot.transform, new Vector3(22f, 0, halfW + 5f), -135f);

            // 5. Pink Flowering Cherry Blossom Trees (Sakura)
            CreateSakuraTree(templeRoot.transform, new Vector3(-45f, 0, -halfW - 10f), 1.3f);
            CreateSakuraTree(templeRoot.transform, new Vector3(45f, 0, -halfW - 10f), 1.3f);
            CreateSakuraTree(templeRoot.transform, new Vector3(-45f, 0, halfW + 10f), 1.25f);
            CreateSakuraTree(templeRoot.transform, new Vector3(45f, 0, halfW + 10f), 1.25f);
            CreateSakuraTree(templeRoot.transform, new Vector3(-55f, 0, -22f), 1.4f);
            CreateSakuraTree(templeRoot.transform, new Vector3(-55f, 0, 22f), 1.35f);
            CreateSakuraTree(templeRoot.transform, new Vector3(55f, 0, -22f), 1.4f);
            CreateSakuraTree(templeRoot.transform, new Vector3(55f, 0, 22f), 1.35f);
            CreateSakuraTree(templeRoot.transform, new Vector3(-15f, 0, -halfW - 12f), 1.15f);
            CreateSakuraTree(templeRoot.transform, new Vector3(15f, 0, -halfW - 12f), 1.15f);
            CreateSakuraTree(templeRoot.transform, new Vector3(-15f, 0, halfW + 12f), 1.15f);
            CreateSakuraTree(templeRoot.transform, new Vector3(15f, 0, halfW + 12f), 1.15f);

            // 6. Zen Court Concentric Ripple Rings on the field
            CreateZenRipples(templeRoot.transform);
        }

        private void CreatePagoda(Transform parent, Vector3 pos, int tiers = 5, float baseW = 12f, float tierH = 4.2f)
        {
            GameObject pagodaObj = new GameObject("Forbidden_Pagoda");
            pagodaObj.transform.SetParent(parent, false);
            pagodaObj.transform.localPosition = pos;

            // Stone base plinth
            CreateBeam(pagodaObj.transform, "Plinth", new Vector3(0, 1.5f, 0), new Vector3(baseW * 1.3f, 3f, baseW * 1.3f), templeStoneMat);
            float curY = 3f;

            for (int t = 0; t < tiers; t++)
            {
                float tw = baseW * Mathf.Pow(0.9f, t);
                float th = tierH * Mathf.Pow(0.92f, t);

                // Core shoji lantern room
                CreateBeam(pagodaObj.transform, $"Core_T{t}", new Vector3(0, curY + th * 0.5f, 0), new Vector3(tw * 0.78f, th, tw * 0.78f), lanternGlowMat);

                // 4 Corner Vermilion Timber Pillars
                float colInset = tw * 0.38f;
                foreach (float cx in new float[] { -colInset, colInset })
                {
                    foreach (float cz in new float[] { -colInset, colInset })
                    {
                        GameObject pillar = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                        pillar.name = "Pillar";
                        pillar.transform.SetParent(pagodaObj.transform, false);
                        pillar.transform.localPosition = new Vector3(cx, curY + th * 0.5f, cz);
                        pillar.transform.localScale = new Vector3(0.5f, th * 0.5f, 0.5f);
                        if (pillar.GetComponent<Collider>() != null) DestroyImmediate(pillar.GetComponent<Collider>());
                        pillar.GetComponent<Renderer>().sharedMaterial = templeRedMat;
                    }
                }

                // Flared Japanese Tile Roof
                float roofW = tw * 1.45f;
                float roofH = 1.4f;
                CreatePagodaRoof(pagodaObj.transform, new Vector3(0, curY + th, 0), roofW, roofH);

                // Gold ridge beam
                CreateBeam(pagodaObj.transform, $"GoldRidge_T{t}", new Vector3(0, curY + th + roofH + 0.15f, 0), new Vector3(roofW * 0.85f, 0.35f, 0.35f), templeGoldMat);

                curY += th + roofH + 0.3f;
            }

            // Top Spire (Sorin)
            GameObject spire = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            spire.name = "SorinSpire";
            spire.transform.SetParent(pagodaObj.transform, false);
            spire.transform.localPosition = new Vector3(0, curY + 3.5f, 0);
            spire.transform.localScale = new Vector3(0.35f, 3.5f, 0.35f);
            if (spire.GetComponent<Collider>() != null) DestroyImmediate(spire.GetComponent<Collider>());
            spire.GetComponent<Renderer>().sharedMaterial = templeGoldMat;

            // Spire rings
            for (int r = 0; r < 5; r++)
            {
                CreateBeam(pagodaObj.transform, $"SpireRing_{r}", new Vector3(0, curY + 1.2f + r * 0.9f, 0), new Vector3(1.6f - r * 0.2f, 0.25f, 1.6f - r * 0.2f), templeGoldMat);
            }
        }

        private GameObject CreatePagodaRoof(Transform parent, Vector3 localPos, float width, float height)
        {
            GameObject roofObj = new GameObject("PagodaRoof");
            roofObj.transform.SetParent(parent, false);
            roofObj.transform.localPosition = localPos;

            MeshFilter mf = roofObj.AddComponent<MeshFilter>();
            MeshRenderer mr = roofObj.AddComponent<MeshRenderer>();
            mr.sharedMaterial = templeRoofMat;

            Mesh mesh = new Mesh { name = "FlaredRoofMesh" };
            float hw = width * 0.5f;
            float topW = width * 0.2f;

            Vector3[] verts = new Vector3[]
            {
                new Vector3(-topW, height, -topW),
                new Vector3( topW, height, -topW),
                new Vector3( topW, height,  topW),
                new Vector3(-topW, height,  topW),
                new Vector3(-hw, 0, -hw),
                new Vector3( hw, 0, -hw),
                new Vector3( hw, 0,  hw),
                new Vector3(-hw, 0,  hw)
            };

            int[] tris = new int[]
            {
                0, 1, 5, 0, 5, 4,
                1, 2, 6, 1, 6, 5,
                2, 3, 7, 2, 7, 6,
                3, 0, 4, 3, 4, 7,
                0, 2, 1, 0, 3, 2,
                4, 5, 6, 4, 6, 7
            };

            mesh.vertices = verts;
            mesh.triangles = tris;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mf.sharedMesh = mesh;
            return roofObj;
        }

        private void CreateMoonBridge(Transform parent, Vector3 goalPos, float xDirection)
        {
            GameObject bridgeObj = new GameObject("Forbidden_MoonBridge");
            bridgeObj.transform.SetParent(parent, false);
            bridgeObj.transform.localPosition = new Vector3(goalPos.x + (xDirection * 5.5f), goalHeight + 0.8f, 0);

            int segments = 16;
            float span = goalWidth + 6f; // 26m span
            float archH = 5.5f;
            float bridgeThickness = 0.6f;
            float bridgeDepth = 4.5f;

            for (int i = 0; i < segments; i++)
            {
                float t0 = (float)i / segments;
                float t1 = (float)(i + 1) / segments;

                float z0 = Mathf.Lerp(-span * 0.5f, span * 0.5f, t0);
                float z1 = Mathf.Lerp(-span * 0.5f, span * 0.5f, t1);

                float y0 = Mathf.Sin(t0 * Mathf.PI) * archH;
                float y1 = Mathf.Sin(t1 * Mathf.PI) * archH;

                Vector3 p0 = new Vector3(0, y0, z0);
                Vector3 p1 = new Vector3(0, y1, z1);
                Vector3 mid = (p0 + p1) * 0.5f;
                float segLen = Vector3.Distance(p0, p1);

                GameObject deckSeg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                deckSeg.name = $"BridgeDeck_{i}";
                deckSeg.transform.SetParent(bridgeObj.transform, false);
                deckSeg.transform.localPosition = mid;
                deckSeg.transform.localScale = new Vector3(bridgeDepth, bridgeThickness, segLen + 0.05f);
                deckSeg.transform.LookAt(bridgeObj.transform.TransformPoint(p1));
                if (deckSeg.GetComponent<Collider>() != null) DestroyImmediate(deckSeg.GetComponent<Collider>());
                deckSeg.GetComponent<Renderer>().sharedMaterial = templeStoneMat;

                float halfD = bridgeDepth * 0.45f;
                foreach (float sideOffset in new float[] { -halfD, halfD })
                {
                    GameObject post = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    post.name = "RailPost";
                    post.transform.SetParent(bridgeObj.transform, false);
                    post.transform.localPosition = mid + new Vector3(sideOffset, 0.65f, 0);
                    post.transform.localScale = new Vector3(0.2f, 0.6f, 0.2f);
                    if (post.GetComponent<Collider>() != null) DestroyImmediate(post.GetComponent<Collider>());
                    post.GetComponent<Renderer>().sharedMaterial = templeRedMat;

                    if (i % 3 == 0)
                    {
                        GameObject lantern = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                        lantern.name = "BridgeLantern";
                        lantern.transform.SetParent(bridgeObj.transform, false);
                        lantern.transform.localPosition = mid + new Vector3(sideOffset, 1.4f, 0);
                        lantern.transform.localScale = new Vector3(0.35f, 0.45f, 0.35f);
                        if (lantern.GetComponent<Collider>() != null) DestroyImmediate(lantern.GetComponent<Collider>());
                        lantern.GetComponent<Renderer>().sharedMaterial = lanternGlowMat;
                    }
                }
            }
        }

        private void CreateSakuraTree(Transform parent, Vector3 pos, float scale = 1f)
        {
            GameObject treeObj = new GameObject("CherryBlossomTree");
            treeObj.transform.SetParent(parent, false);
            treeObj.transform.localPosition = pos;

            float trunkH = 8f * scale;
            GameObject trunk = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            trunk.name = "Trunk";
            trunk.transform.SetParent(treeObj.transform, false);
            trunk.transform.localPosition = new Vector3(0, trunkH * 0.5f, 0);
            trunk.transform.localScale = new Vector3(0.7f * scale, trunkH * 0.5f, 0.7f * scale);
            trunk.transform.localRotation = Quaternion.Euler(4f, 15f, -3f);
            if (trunk.GetComponent<Collider>() != null) DestroyImmediate(trunk.GetComponent<Collider>());
            trunk.GetComponent<Renderer>().sharedMaterial = sakuraBarkMat;

            Vector4[] puffs = new Vector4[]
            {
                new Vector4(0f, trunkH, 0f, 3.2f * scale),
                new Vector4(-1.8f * scale, trunkH * 0.85f, 1.4f * scale, 2.6f * scale),
                new Vector4(1.9f * scale, trunkH * 0.9f, -1.2f * scale, 2.7f * scale),
                new Vector4(-1.2f * scale, trunkH * 1.15f, -1.4f * scale, 2.4f * scale),
                new Vector4(1.4f * scale, trunkH * 1.1f, 1.5f * scale, 2.6f * scale),
                new Vector4(0f, trunkH * 1.3f, 0f, 2.2f * scale)
            };

            for (int i = 0; i < puffs.Length; i++)
            {
                Vector4 p = puffs[i];
                GameObject puff = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                puff.name = $"BlossomPuff_{i}";
                puff.transform.SetParent(treeObj.transform, false);
                puff.transform.localPosition = new Vector3(p.x, p.y, p.z);
                puff.transform.localScale = new Vector3(p.w * 1.2f, p.w * 0.85f, p.w * 1.1f);
                if (puff.GetComponent<Collider>() != null) DestroyImmediate(puff.GetComponent<Collider>());
                puff.GetComponent<Renderer>().sharedMaterial = (i % 2 == 0) ? sakuraBlossomMat : sakuraBlossomDeepMat;
            }
        }

        private void CreateToriiGate(Transform parent, Vector3 pos, float rotY = 0f, float scale = 1f)
        {
            GameObject toriiObj = new GameObject("ToriiGate");
            toriiObj.transform.SetParent(parent, false);
            toriiObj.transform.localPosition = pos;
            toriiObj.transform.localRotation = Quaternion.Euler(0, rotY, 0);

            float w = 12f * scale;
            float h = 10f * scale;

            foreach (float cx in new float[] { -w * 0.5f, w * 0.5f })
            {
                GameObject col = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                col.name = "ToriiColumn";
                col.transform.SetParent(toriiObj.transform, false);
                col.transform.localPosition = new Vector3(cx, h * 0.5f, 0);
                col.transform.localScale = new Vector3(0.9f * scale, h * 0.5f, 0.9f * scale);
                if (col.GetComponent<Collider>() != null) DestroyImmediate(col.GetComponent<Collider>());
                col.GetComponent<Renderer>().sharedMaterial = templeRedMat;
            }

            CreateBeam(toriiObj.transform, "KasagiLintel", new Vector3(0, h + 0.3f * scale, 0), new Vector3(w * 1.45f, 0.8f * scale, 0.9f * scale), templeRoofMat);
            CreateBeam(toriiObj.transform, "NukiLintel", new Vector3(0, h * 0.78f, 0), new Vector3(w * 1.2f, 0.45f * scale, 0.45f * scale), templeRedMat);
            CreateBeam(toriiObj.transform, "GakuTablet", new Vector3(0, h * 0.88f, 0), new Vector3(1.4f * scale, 1.8f * scale, 0.2f * scale), templeGoldMat);
        }

        private void CreateGuardianLion(Transform parent, Vector3 pos, float rotY = 0f)
        {
            GameObject lionObj = new GameObject("GuardianLion");
            lionObj.transform.SetParent(parent, false);
            lionObj.transform.localPosition = pos;
            lionObj.transform.localRotation = Quaternion.Euler(0, rotY, 0);

            CreateBeam(lionObj.transform, "Plinth", new Vector3(0, 1.6f, 0), new Vector3(3.6f, 3.2f, 4.4f), templeStoneMat);

            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            body.name = "LionBody";
            body.transform.SetParent(lionObj.transform, false);
            body.transform.localPosition = new Vector3(0, 4.2f, 0);
            body.transform.localScale = new Vector3(2.2f, 2.5f, 3f);
            if (body.GetComponent<Collider>() != null) DestroyImmediate(body.GetComponent<Collider>());
            body.GetComponent<Renderer>().sharedMaterial = templeStoneMat;

            GameObject head = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            head.name = "LionHead";
            head.transform.SetParent(lionObj.transform, false);
            head.transform.localPosition = new Vector3(0, 5.8f, 1.2f);
            head.transform.localScale = new Vector3(1.8f, 1.8f, 1.8f);
            if (head.GetComponent<Collider>() != null) DestroyImmediate(head.GetComponent<Collider>());
            head.GetComponent<Renderer>().sharedMaterial = templeStoneMat;

            GameObject orb = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            orb.name = "LionOrb";
            orb.transform.SetParent(lionObj.transform, false);
            orb.transform.localPosition = new Vector3(0.8f, 3.8f, 1.5f);
            orb.transform.localScale = new Vector3(1f, 1f, 1f);
            if (orb.GetComponent<Collider>() != null) DestroyImmediate(orb.GetComponent<Collider>());
            orb.GetComponent<Renderer>().sharedMaterial = templeGoldMat;
        }

        private void CreateZenRipples(Transform parent)
        {
            GameObject zenRoot = new GameObject("Zen_Ripple_Rings");
            zenRoot.transform.SetParent(parent, false);

            float[] radii = new float[] { 5f, 9f, 14f, 20f, 27f };
            for (int r = 0; r < radii.Length; r++)
            {
                CreateZenRing(zenRoot.transform, Vector3.zero, radii[r], 0.12f, new Color(0.95f, 0.78f, 0.45f, 0.6f));
            }

            float[] goalRadii = new float[] { 6f, 11f, 16f };
            for (int r = 0; r < goalRadii.Length; r++)
            {
                CreateZenRing(zenRoot.transform, new Vector3(-32f, 0, 0), goalRadii[r], 0.12f, new Color(0f, 0.85f, 1f, 0.5f));
                CreateZenRing(zenRoot.transform, new Vector3(32f, 0, 0), goalRadii[r], 0.12f, new Color(1f, 0.45f, 0.05f, 0.5f));
            }
        }

        private void CreateZenRing(Transform parent, Vector3 center, float radius, float thickness, Color color)
        {
            int segments = 40;
            for (int i = 0; i < segments; i++)
            {
                float t0 = (float)i / segments * Mathf.PI * 2f;
                float t1 = (float)(i + 1) / segments * Mathf.PI * 2f;

                Vector3 p0 = center + new Vector3(Mathf.Cos(t0) * radius, 0.03f, Mathf.Sin(t0) * radius);
                Vector3 p1 = center + new Vector3(Mathf.Cos(t1) * radius, 0.03f, Mathf.Sin(t1) * radius);
                Vector3 mid = (p0 + p1) * 0.5f;
                float segLen = Vector3.Distance(p0, p1);

                GameObject ringSeg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                ringSeg.name = "ZenRingSeg";
                ringSeg.transform.SetParent(parent, false);
                ringSeg.transform.localPosition = mid;
                ringSeg.transform.localScale = new Vector3(thickness, 0.02f, segLen + 0.02f);
                ringSeg.transform.LookAt(parent.TransformPoint(p1));
                if (ringSeg.GetComponent<Collider>() != null) DestroyImmediate(ringSeg.GetComponent<Collider>());
                ringSeg.GetComponent<Renderer>().sharedMaterial = CreatePBRMaterial("ZenRingMat", color, 0.3f, 0f, color * 1.5f);
            }
        }

        #endregion
    }
}
