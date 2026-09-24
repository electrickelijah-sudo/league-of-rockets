#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace RocketLeague.Editor
{
    /// <summary>
    /// Unity Editor Menus for one-click Arena generation, Car creation, and specification validation.
    /// </summary>
    public static class RocketLeagueEditorMenu
    {
        [MenuItem("Rocket League/1. Build Complete Arena Scene", false, 1)]
        public static void BuildCompleteArena()
        {
            GameObject arenaRoot = GameObject.Find("RL_Arena");
            if (arenaRoot == null)
            {
                arenaRoot = new GameObject("RL_Arena");
                Undo.RegisterCreatedObjectUndo(arenaRoot, "Create RL Arena");
            }

            ArenaMeshBuilder builder = arenaRoot.GetComponent<ArenaMeshBuilder>();
            if (builder == null) builder = arenaRoot.AddComponent<ArenaMeshBuilder>();

            ArenaSetup setup = arenaRoot.GetComponent<ArenaSetup>();
            if (setup == null) setup = arenaRoot.AddComponent<ArenaSetup>();
            setup.meshBuilder = builder;

            setup.BuildCompleteScene();
            EditorUtility.SetDirty(arenaRoot);
            Debug.Log("<color=green>[Rocket League]</color> Complete 100m x 80m Arena successfully generated in current scene!");
        }

        [MenuItem("Rocket League/2. Create Player Car (Exact Dimensions)", false, 2)]
        public static void CreatePlayerCar()
        {
            GameObject carObj = new GameObject("Car_Player_Blue");
            carObj.transform.position = new Vector3(-35f, 0.8f, 0f);
            carObj.transform.rotation = Quaternion.Euler(0, 90f, 0); // Face center (+X)
            Undo.RegisterCreatedObjectUndo(carObj, "Create Player Car");

            CarController controller = carObj.AddComponent<CarController>();
            CarCustomizer customizer = carObj.AddComponent<CarCustomizer>();
            CarPrefabBuilder builder = carObj.AddComponent<CarPrefabBuilder>();

            builder.BuildCar();
            EditorUtility.SetDirty(carObj);
            Selection.activeGameObject = carObj;
            Debug.Log("<color=cyan>[Rocket League]</color> Player car created at (-35, 0.8, 0) facing center with exact dimensions!");
        }

        [MenuItem("Rocket League/3. Validate Dimensions & Physics Specs", false, 3)]
        public static void ValidateSpecifications()
        {
            Debug.Log("<b><color=yellow>=== ROCKET LEAGUE SPECIFICATION VALIDATION ===</color></b>");

            // Validate Arena
            ArenaMeshBuilder arena = Object.FindFirstObjectByType<ArenaMeshBuilder>();
            if (arena != null)
            {
                bool fieldOk = Mathf.Approximately(arena.fieldLength, 100f) && Mathf.Approximately(arena.fieldWidth, 80f);
                bool wallOk = Mathf.Approximately(arena.wallHeight, 8f) && Mathf.Approximately(arena.floorToWallRadius, 8f);
                bool cornerOk = Mathf.Approximately(arena.cornerRadius, 12f);
                bool goalOk = Mathf.Approximately(arena.goalWidth, 20f) && Mathf.Approximately(arena.goalHeight, 8f) && Mathf.Approximately(arena.goalDepth, 8f);
                bool ceilingOk = Mathf.Approximately(arena.ceilingHeight, 20f);

                Debug.Log($"Field Dimensions (100x80m): {(fieldOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Wall Height & Quarter-Pipe Ramp (8m / 8m radius): {(wallOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Curved Corner Radius (12m): {(cornerOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Goal Dimensions (20x8x8m): {(goalOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Ceiling Dome Height (20m): {(ceilingOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
            }
            else
            {
                Debug.LogWarning("No ArenaMeshBuilder found in scene. Run 'Rocket League > 1. Build Complete Arena Scene' first.");
            }

            // Validate Car
            CarController car = Object.FindFirstObjectByType<CarController>();
            if (car != null)
            {
                bool massOk = Mathf.Approximately(car.vehicleMass, 1500f);
                bool speedOk = Mathf.Approximately(car.maxGroundSpeed, 22f) && Mathf.Approximately(car.maxBoostSpeed, 35f);
                bool accelOk = Mathf.Approximately(car.boostAcceleration, 25f);
                bool jumpOk = Mathf.Approximately(car.jumpForce, 7f);
                bool wheelOk = Mathf.Approximately(car.wheelRadius, 0.4f) && Mathf.Approximately(car.suspensionTravel, 0.3f);

                Debug.Log($"Car Mass (1500 kg): {(massOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Car Ground & Boost Speeds (22 m/s & 35 m/s): {(speedOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Boost Acceleration (~25 m/s²): {(accelOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Jump Force (~7 m/s): {(jumpOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
                Debug.Log($"Wheel Radius & Travel (0.4m & 0.3m): {(wheelOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
            }

            // Validate Ball
            BallController ball = Object.FindFirstObjectByType<BallController>();
            if (ball != null)
            {
                bool ballOk = Mathf.Approximately(ball.radius, 1.25f);
                Debug.Log($"Ball Radius (1.25m / 2.5m diameter): {(ballOk ? "<color=green>PASSED</color>" : "<color=red>FAILED</color>")}");
            }

            Debug.Log("<b><color=yellow>==============================================</color></b>");
        }

        [MenuItem("Rocket League/4. Build Complete Playable Match (All Systems)", false, 4)]
        public static void BuildCompletePlayableMatch()
        {
            GameObject bootObj = GameObject.Find("RL_MasterBootstrap");
            if (bootObj == null)
            {
                bootObj = new GameObject("RL_MasterBootstrap");
                Undo.RegisterCreatedObjectUndo(bootObj, "Create RL Master Bootstrap");
            }

            GameBootstrap bootstrap = bootObj.GetComponent<GameBootstrap>();
            if (bootstrap == null) bootstrap = bootObj.AddComponent<GameBootstrap>();
            bootstrap.runOnAwake = true;
            bootstrap.matchMode = GameModeType.Duel1v1;
            bootstrap.stadiumTheme = ArenaThemeType.SunsetCircuit;

            bootstrap.InitializeFullMatch(bootstrap.matchMode, bootstrap.stadiumTheme);
            EditorUtility.SetDirty(bootObj);
            Debug.Log("<color=green><b>[Rocket League] COMPLETE 3X SUNSET PLAYABLE MATCH SUCCESSFULLY BUILT! Ready to hit Play in Editor!</b></color>");
        }

        [MenuItem("Rocket League/5. Spawn Blender 3X Sunset Stadium Model", false, 5)]
        public static void SpawnBlenderSunsetModel()
        {
            AssetDatabase.Refresh();
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/SunsetStadiumArena.fbx");
            if (prefab == null)
            {
                prefab = Resources.Load<GameObject>("SunsetStadiumArena");
            }

            if (prefab != null)
            {
                GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                instance.name = "Blender_SunsetStadium_3X";
                instance.transform.position = Vector3.zero;
                instance.transform.rotation = Quaternion.identity;
                instance.transform.localScale = Vector3.one;
                Undo.RegisterCreatedObjectUndo(instance, "Spawn Blender 3X Sunset Stadium");
                Selection.activeGameObject = instance;
                Debug.Log("<color=green><b>[Rocket League] Successfully spawned Blender 3X Sunset Stadium model into the scene!</b></color>");
            }
            else
            {
                Debug.LogWarning("[Rocket League] Could not find SunsetStadiumArena.fbx in Assets/Art/Models/ or Assets/Resources/.");
            }
        }

        [MenuItem("Rocket League/6. Save Match Scene to Assets/Scenes/MainArena.unity", false, 6)]
        public static void SaveMatchScene()
        {
            if (!System.IO.Directory.Exists("Assets/Scenes"))
            {
                System.IO.Directory.CreateDirectory("Assets/Scenes");
            }

            UnityEngine.SceneManagement.Scene activeScene = UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene();
            string scenePath = "Assets/Scenes/MainArena.unity";
            bool success = UnityEditor.SceneManagement.EditorSceneManager.SaveScene(activeScene, scenePath);
            AssetDatabase.Refresh();

            if (success)
            {
                Debug.Log($"<color=green><b>[Rocket League] Scene saved successfully to {scenePath}!</b></color>");
            }
            else
            {
                Debug.LogWarning($"[Rocket League] Failed to save scene to {scenePath}.");
            }
        }
    }
}
#endif
