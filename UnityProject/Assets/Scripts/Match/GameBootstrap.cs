using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    /// <summary>
    /// Master Runtime and Editor Bootstrapper for Turbo Strike 3D / Rocket League.
    /// Guarantees that whether launching an empty scene, entering Play mode, or calling
    /// the setup menu, the entire production-grade game is procedurally constructed,
    /// wired, and ready to play in seconds.
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public class GameBootstrap : MonoBehaviour
    {
        public static GameBootstrap Instance { get; private set; }

        [Header("=== BOOTSTRAP CONFIGURATION ===")]
        public bool runOnAwake = true;
        public GameModeType matchMode = GameModeType.Duel1v1;
        public ArenaThemeType stadiumTheme = ArenaThemeType.SunsetCircuit;

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            if (runOnAwake)
            {
                InitializeFullMatch(matchMode, stadiumTheme);
            }
        }

        /// <summary>
        /// Global runtime entry point: if no bootstrap exists in scene upon play,
        /// automatically instantiate bootstrap and run.
        /// </summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void AutoInitializeScene()
        {
            // If an ArenaManager already exists and is configured, skip
            if (FindFirstObjectByType<ArenaManager>() != null) return;

            GameObject bootObj = new GameObject("RL_MasterBootstrap");
            GameBootstrap bootstrap = bootObj.AddComponent<GameBootstrap>();
            bootstrap.InitializeFullMatch(GameModeType.Duel1v1, ArenaThemeType.SunsetCircuit);
        }

        [ContextMenu("Build Full Match Scene")]
        public void BuildInEditor()
        {
            InitializeFullMatch(matchMode, stadiumTheme);
        }

        public void InitializeFullMatch(GameModeType mode, ArenaThemeType theme)
        {
            Debug.Log("<color=cyan><b>[GameBootstrap] Initializing Complete Turbo Strike 3D Match...</b></color>");

            // 1. Audio Manager
            AudioManager audioMgr = SetupAudioManager();

            // 2. VFX Manager
            SetupVFXManager();

            // 3. Stadium Environment & Arena Geometry
            ArenaMeshBuilder meshBuilder;
            ArenaSetup arenaSetup = SetupArena(out meshBuilder);

            // 4. Directional Lighting & Stadium Theme
            SetupLightingAndTheme(theme, meshBuilder);

            // 5. Physics Ball
            BallController ball = SetupBall();

            // 6. Vehicles (Cobalt Player & Amber Opponent Bot)
            CarController playerCar = SetupPlayerCar();
            CarController botCar = SetupBotOpponentCar(ball);

            // 7. Follow Camera & Replay Camera
            SetupCameras(playerCar, ball);

            // 8. Tournament Canvas HUD & Overlay UI
            InGameHUD hud = SetupTournamentHUD(playerCar, ball);

            // 9. Match Managers & Game Flow Engine
            SetupMatchEngine(ball, playerCar, botCar, hud, audioMgr);

            Debug.Log("<color=green><b>[GameBootstrap] Turbo Strike 3D Match Initialized Successfully! Kickoff Ready!</b></color>");
        }

        private AudioManager SetupAudioManager()
        {
            AudioManager mgr = FindFirstObjectByType<AudioManager>();
            if (mgr == null)
            {
                GameObject audioRoot = new GameObject("RL_AudioManager");
                mgr = audioRoot.AddComponent<AudioManager>();

                // Audio Sources for channels
                mgr.musicSource = audioRoot.AddComponent<AudioSource>();
                mgr.musicSource.loop = true;
                mgr.musicSource.playOnAwake = false;

                mgr.sfxSource = audioRoot.AddComponent<AudioSource>();
                mgr.sfxSource.playOnAwake = false;

                mgr.crowdSource = audioRoot.AddComponent<AudioSource>();
                mgr.crowdSource.loop = true;
                mgr.crowdSource.playOnAwake = false;

                mgr.announcerSource = audioRoot.AddComponent<AudioSource>();
                mgr.announcerSource.playOnAwake = false;
            }

            mgr.InitializeAudioClips();
            return mgr;
        }

        private VFXManager SetupVFXManager()
        {
            VFXManager vfx = FindFirstObjectByType<VFXManager>();
            if (vfx == null)
            {
                GameObject vfxRoot = new GameObject("RL_VFXManager");
                vfx = vfxRoot.AddComponent<VFXManager>();
            }
            return vfx;
        }

        private ArenaSetup SetupArena(out ArenaMeshBuilder meshBuilder)
        {
            GameObject arenaRoot = GameObject.Find("RL_Arena");
            if (arenaRoot == null)
            {
                arenaRoot = new GameObject("RL_Arena");
            }

            meshBuilder = arenaRoot.GetComponent<ArenaMeshBuilder>();
            if (meshBuilder == null) meshBuilder = arenaRoot.AddComponent<ArenaMeshBuilder>();

            ArenaSetup setup = arenaRoot.GetComponent<ArenaSetup>();
            if (setup == null) setup = arenaRoot.AddComponent<ArenaSetup>();
            setup.meshBuilder = meshBuilder;

            // Build complete stadium geometry, boost pads, and markings
            setup.BuildCompleteScene();
            return setup;
        }

        private void SetupLightingAndTheme(ArenaThemeType theme, ArenaMeshBuilder meshBuilder)
        {
            Light sunLight = null;
            Light[] lights = FindObjectsByType<Light>(FindObjectsSortMode.None);
            foreach (var l in lights)
            {
                if (l.type == LightType.Directional)
                {
                    sunLight = l;
                    break;
                }
            }

            if (sunLight == null)
            {
                GameObject lightObj = new GameObject("Directional_SunLight");
                sunLight = lightObj.AddComponent<Light>();
                sunLight.type = LightType.Directional;
                sunLight.shadows = LightShadows.Soft;
            }

            GameObject arenaRoot = GameObject.Find("RL_Arena");
            ArenaThemeManager themeMgr = arenaRoot != null ? arenaRoot.GetComponent<ArenaThemeManager>() : null;
            if (themeMgr == null && arenaRoot != null)
            {
                themeMgr = arenaRoot.AddComponent<ArenaThemeManager>();
            }

            if (themeMgr != null)
            {
                themeMgr.mainDirectionalLight = sunLight;
                if (meshBuilder != null)
                {
                    themeMgr.fieldTurfRenderer = meshBuilder.fieldTurfRenderer;
                    themeMgr.arenaDomeRenderer = meshBuilder.arenaDomeRenderer;
                    themeMgr.stadiumWallsRenderer = meshBuilder.stadiumWallsRenderer;
                }
                themeMgr.ApplyTheme(theme);
            }
        }

        private BallController SetupBall()
        {
            BallController ball = FindFirstObjectByType<BallController>();
            if (ball != null) return ball;

            GameObject ballObj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            ballObj.name = "Ball";
            ballObj.transform.position = new Vector3(0f, 3.75f, 0f);
            ballObj.transform.localScale = new Vector3(7.5f, 7.5f, 7.5f); // 7.5m diameter, 3.75m radius (3x)

            SphereCollider col = ballObj.GetComponent<SphereCollider>();
            col.radius = 0.5f;

            PhysicsMaterial ballMat = new PhysicsMaterial("BallPhysicsMat")
            {
                bounciness = 0.82f,
                dynamicFriction = 0.38f,
                staticFriction = 0.42f,
                bounceCombine = PhysicsMaterialCombine.Maximum,
                frictionCombine = PhysicsMaterialCombine.Average
            };
            col.material = ballMat;

            Rigidbody rb = ballObj.AddComponent<Rigidbody>();
            rb.mass = 105f;
            rb.linearDamping = 0.08f;
            rb.angularDamping = 0.25f;
            rb.interpolation = RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

            ball = ballObj.AddComponent<BallController>();
            ball.radius = 3.75f;
            ball.kickoffPosition = new Vector3(0f, 3.75f, 0f);

            // Altitude indicator ring and high-speed motion trail
            ballObj.AddComponent<BallTrailProjector>();

            // Cybernetic Rocket League Ball Material
            Shader stdShader = Shader.Find("Standard");
            if (stdShader == null) stdShader = Shader.Find("Universal Render Pipeline/Lit");
            if (stdShader == null) stdShader = Shader.Find("Mobile/Diffuse");
            Material ballVisualMat = new Material(stdShader);
            ballVisualMat.name = "Mat_OfficialBall";
            ballVisualMat.color = new Color(0.92f, 0.94f, 0.98f);
            if (ballVisualMat.HasProperty("_Glossiness")) ballVisualMat.SetFloat("_Glossiness", 0.65f);
            if (ballVisualMat.HasProperty("_Smoothness")) ballVisualMat.SetFloat("_Smoothness", 0.65f);
            if (ballVisualMat.HasProperty("_Metallic")) ballVisualMat.SetFloat("_Metallic", 0.35f);
            ballVisualMat.EnableKeyword("_EMISSION");
            if (ballVisualMat.HasProperty("_EmissionColor")) ballVisualMat.SetColor("_EmissionColor", new Color(0.2f, 0.6f, 1f) * 1.2f);
            ballObj.GetComponent<Renderer>().sharedMaterial = ballVisualMat;

            return ball;
        }

        private CarController SetupPlayerCar()
        {
            GameObject carObj = GameObject.Find("Car_Player_Cobalt");
            if (carObj == null)
            {
                carObj = new GameObject("Car_Player_Cobalt");
                carObj.transform.position = new Vector3(-105f, 2.4f, 0f); // 3x distance
                carObj.transform.rotation = Quaternion.Euler(0, 90f, 0); // Face center (+X)
                carObj.transform.localScale = Vector3.one * 3f; // 3x car size
            }
            else
            {
                carObj.transform.localScale = Vector3.one * 3f;
            }

            CarController controller = carObj.GetComponent<CarController>();
            if (controller == null) controller = carObj.AddComponent<CarController>();
            controller.isAI = false;

            // Scaled vehicle dynamics for 3x pitch
            controller.maxGroundSpeed = 55f;
            controller.maxBoostSpeed = 85f;
            controller.driveAcceleration = 35f;
            controller.boostAcceleration = 65f;
            controller.jumpForce = 18f;
            controller.doubleJumpForce = 18f;
            controller.dodgeImpulse = 30f;

            EquippedLoadout loadout = SaveSystem.CurrentData.loadout;

            CarPrefabBuilder builder = carObj.GetComponent<CarPrefabBuilder>();
            if (builder == null) builder = carObj.AddComponent<CarPrefabBuilder>();

            if (loadout.chassisId == "viper_gt") builder.chassisType = VehicleChassisType.ViperGT;
            else if (loadout.chassisId == "specter_rs") builder.chassisType = VehicleChassisType.SpecterRS;
            else if (loadout.chassisId == "ion_phantom") builder.chassisType = VehicleChassisType.IonPhantom;
            else if (loadout.chassisId == "titan_juggernaut") builder.chassisType = VehicleChassisType.TitanJuggernaut;
            else builder.chassisType = VehicleChassisType.ApexVanguard;

            builder.wheelsId = !string.IsNullOrEmpty(loadout.wheelsId) ? loadout.wheelsId : "tuner_aero";
            builder.BuildCar();

            CarCustomizer customizer = carObj.GetComponent<CarCustomizer>();
            if (customizer == null) customizer = carObj.AddComponent<CarCustomizer>();
            customizer.ApplyLoadout(loadout);

            return controller;
        }

        private CarController SetupBotOpponentCar(BallController ball)
        {
            GameObject botObj = GameObject.Find("Car_Bot_Amber");
            if (botObj == null)
            {
                botObj = new GameObject("Car_Bot_Amber");
                botObj.transform.position = new Vector3(105f, 2.4f, 0f); // 3x distance
                botObj.transform.rotation = Quaternion.Euler(0, -90f, 0); // Face center (-X)
                botObj.transform.localScale = Vector3.one * 3f; // 3x car size
            }
            else
            {
                botObj.transform.localScale = Vector3.one * 3f;
            }

            CarController controller = botObj.GetComponent<CarController>();
            if (controller == null) controller = botObj.AddComponent<CarController>();
            controller.isAI = true;

            controller.maxGroundSpeed = 55f;
            controller.maxBoostSpeed = 85f;
            controller.driveAcceleration = 35f;
            controller.boostAcceleration = 65f;
            controller.jumpForce = 18f;
            controller.doubleJumpForce = 18f;
            controller.dodgeImpulse = 30f;

            BotController bot = botObj.GetComponent<BotController>();
            if (bot == null) bot = botObj.AddComponent<BotController>();
            bot.botName = "Amber Bot";
            bot.isBlueTeam = false;
            bot.difficulty = (BotController.BotDifficulty)Mathf.Clamp(SaveSystem.CurrentData.settings.botDifficultyIndex, 0, 2);
            bot.targetBall = ball;

            CarCustomizer customizer = botObj.GetComponent<CarCustomizer>();
            if (customizer == null) customizer = botObj.AddComponent<CarCustomizer>();
            customizer.primaryColor = new Color(1f, 0.42f, 0f); // Fiery Amber
            customizer.secondaryColor = new Color(0.18f, 0.18f, 0.2f);

            CarPrefabBuilder builder = botObj.GetComponent<CarPrefabBuilder>();
            if (builder == null) builder = botObj.AddComponent<CarPrefabBuilder>();
            builder.chassisType = VehicleChassisType.ViperGT;
            builder.BuildCar();

            customizer.ApplyCustomization();
            return controller;
        }

        private void SetupCameras(CarController playerCar, BallController ball)
        {
            Camera cam = Camera.main;
            if (cam == null)
            {
                cam = FindFirstObjectByType<Camera>();
            }
            if (cam == null)
            {
                GameObject camObj = new GameObject("Main Camera");
                camObj.tag = "MainCamera";
                cam = camObj.AddComponent<Camera>();
                camObj.AddComponent<AudioListener>();
            }

            cam.enabled = true;
            cam.gameObject.SetActive(true);
            cam.tag = "MainCamera";
            cam.targetDisplay = 0;
            cam.depth = 0;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.12f, 0.10f, 0.22f); // Deep dusk twilight sky
            cam.cullingMask = ~0; // Render all layers

            CameraController camCtrl = cam.GetComponent<CameraController>();
            if (camCtrl == null) camCtrl = cam.gameObject.AddComponent<CameraController>();
            if (playerCar != null) camCtrl.carTarget = playerCar.transform;
            if (ball != null) camCtrl.ballTarget = ball.transform;
            camCtrl.isBallCam = true;
            camCtrl.distance = 22.5f; // 3x follow distance
            camCtrl.height = 8.4f;    // 3x follow height

            GoalReplayCamera replayCam = cam.GetComponent<GoalReplayCamera>();
            if (replayCam == null) replayCam = cam.gameObject.AddComponent<GoalReplayCamera>();
            replayCam.orbitDistance = 25.5f;
            replayCam.orbitHeight = 9.6f;
        }

        private InGameHUD SetupTournamentHUD(CarController playerCar, BallController ball)
        {
            InGameHUD hud = FindFirstObjectByType<InGameHUD>();
            if (hud != null) return hud;

            // Builtin font fallback
            Font uiFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (uiFont == null) uiFont = Resources.GetBuiltinResource<Font>("Arial.ttf");
            if (uiFont == null) uiFont = Font.CreateDynamicFontFromOSFont("Arial", 16);

            // Canvas Root
            GameObject canvasObj = new GameObject("HUD_Canvas");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObj.AddComponent<CanvasScaler>();
            canvasObj.AddComponent<GraphicRaycaster>();

            hud = canvasObj.AddComponent<InGameHUD>();
            hud.playerCar = playerCar;
            hud.ball = ball;
            hud.mainCam = Camera.main;

            // 1. Scoreboard Header (Top Center)
            GameObject scoreHeader = new GameObject("ScoreboardHeader");
            scoreHeader.transform.SetParent(canvasObj.transform, false);
            RectTransform headerRt = scoreHeader.AddComponent<RectTransform>();
            headerRt.anchorMin = new Vector2(0.5f, 1f);
            headerRt.anchorMax = new Vector2(0.5f, 1f);
            headerRt.pivot = new Vector2(0.5f, 1f);
            headerRt.anchoredPosition = new Vector2(0, -18);
            headerRt.sizeDelta = new Vector2(400, 60);

            // Header Background
            Image headerBg = scoreHeader.AddComponent<Image>();
            headerBg.color = new Color(0.08f, 0.1f, 0.14f, 0.88f);

            // Blue Score
            GameObject blueScoreObj = CreateUIText(scoreHeader.transform, "BlueScoreText", "0", 32, TextAnchor.MiddleCenter, new Color(0.1f, 0.65f, 1f), uiFont);
            RectTransform blueRt = blueScoreObj.GetComponent<RectTransform>();
            blueRt.anchorMin = new Vector2(0f, 0f);
            blueRt.anchorMax = new Vector2(0.28f, 1f);
            blueRt.offsetMin = Vector2.zero;
            blueRt.offsetMax = Vector2.zero;
            hud.blueScoreText = blueScoreObj.GetComponent<Text>();

            // Match Clock
            GameObject timerObj = CreateUIText(scoreHeader.transform, "TimerText", "05:00", 28, TextAnchor.MiddleCenter, Color.white, uiFont);
            RectTransform timerRt = timerObj.GetComponent<RectTransform>();
            timerRt.anchorMin = new Vector2(0.3f, 0f);
            timerRt.anchorMax = new Vector2(0.7f, 1f);
            timerRt.offsetMin = Vector2.zero;
            timerRt.offsetMax = Vector2.zero;
            hud.matchTimerText = timerObj.GetComponent<Text>();

            // Orange Score
            GameObject orangeScoreObj = CreateUIText(scoreHeader.transform, "OrangeScoreText", "0", 32, TextAnchor.MiddleCenter, new Color(1f, 0.5f, 0.05f), uiFont);
            RectTransform orangeRt = orangeScoreObj.GetComponent<RectTransform>();
            orangeRt.anchorMin = new Vector2(0.72f, 0f);
            orangeRt.anchorMax = new Vector2(1f, 1f);
            orangeRt.offsetMin = Vector2.zero;
            orangeRt.offsetMax = Vector2.zero;
            hud.orangeScoreText = orangeScoreObj.GetComponent<Text>();

            // Overtime indicator
            GameObject otObj = CreateUIText(scoreHeader.transform, "OvertimeText", "+OT", 16, TextAnchor.MiddleCenter, Color.yellow, uiFont);
            otObj.SetActive(false);
            hud.overtimeIndicator = otObj;

            // 2. Speedometer (Bottom Right)
            GameObject speedObj = CreateUIText(canvasObj.transform, "SpeedometerText", "0 KM/H", 24, TextAnchor.MiddleRight, new Color(0.85f, 0.9f, 1f), uiFont);
            RectTransform speedRt = speedObj.GetComponent<RectTransform>();
            speedRt.anchorMin = new Vector2(1f, 0f);
            speedRt.anchorMax = new Vector2(1f, 0f);
            speedRt.pivot = new Vector2(1f, 0f);
            speedRt.anchoredPosition = new Vector2(-40, 160);
            speedRt.sizeDelta = new Vector2(200, 40);
            hud.speedKmhText = speedObj.GetComponent<Text>();

            // 3. Boost Meter (Bottom Right)
            GameObject boostGroup = new GameObject("BoostGaugeGroup");
            boostGroup.transform.SetParent(canvasObj.transform, false);
            RectTransform boostRt = boostGroup.AddComponent<RectTransform>();
            boostRt.anchorMin = new Vector2(1f, 0f);
            boostRt.anchorMax = new Vector2(1f, 0f);
            boostRt.pivot = new Vector2(1f, 0f);
            boostRt.anchoredPosition = new Vector2(-40, 40);
            boostRt.sizeDelta = new Vector2(120, 120);

            // Boost circle/box background
            Image boostBg = boostGroup.AddComponent<Image>();
            boostBg.color = new Color(0.1f, 0.12f, 0.18f, 0.85f);

            // Boost numeric value
            GameObject boostValObj = CreateUIText(boostGroup.transform, "BoostValueText", "33", 44, TextAnchor.MiddleCenter, new Color(1f, 0.75f, 0.1f), uiFont);
            RectTransform valRt = boostValObj.GetComponent<RectTransform>();
            valRt.anchorMin = Vector2.zero;
            valRt.anchorMax = Vector2.one;
            valRt.offsetMin = Vector2.zero;
            valRt.offsetMax = Vector2.zero;
            hud.boostValueText = boostValObj.GetComponent<Text>();

            // Supersonic Badge
            GameObject supersonicObj = CreateUIText(boostGroup.transform, "SupersonicBadge", "SUPERSONIC", 13, TextAnchor.MiddleCenter, Color.cyan, uiFont);
            RectTransform superRt = supersonicObj.GetComponent<RectTransform>();
            superRt.anchorMin = new Vector2(0f, 1f);
            superRt.anchorMax = new Vector2(1f, 1f);
            superRt.pivot = new Vector2(0.5f, 0f);
            superRt.anchoredPosition = new Vector2(0, 5);
            superRt.sizeDelta = new Vector2(120, 24);
            supersonicObj.SetActive(false);
            hud.supersonicIcon = supersonicObj;

            // 4. Center Announcement Banner
            GameObject announceObj = CreateUIText(canvasObj.transform, "AnnouncementBanner", "", 52, TextAnchor.MiddleCenter, Color.white, uiFont);
            RectTransform announceRt = announceObj.GetComponent<RectTransform>();
            announceRt.anchorMin = new Vector2(0.5f, 0.65f);
            announceRt.anchorMax = new Vector2(0.5f, 0.65f);
            announceRt.pivot = new Vector2(0.5f, 0.5f);
            announceRt.sizeDelta = new Vector2(600, 100);
            hud.kickoffCountdownBanner = announceObj;
            hud.countdownNumberText = announceObj.GetComponent<Text>();

            // 5. Stat Notification Badge (Top Right)
            GameObject statBadge = new GameObject("StatNotificationBadge");
            statBadge.transform.SetParent(canvasObj.transform, false);
            RectTransform badgeRt = statBadge.AddComponent<RectTransform>();
            badgeRt.anchorMin = new Vector2(1f, 1f);
            badgeRt.anchorMax = new Vector2(1f, 1f);
            badgeRt.pivot = new Vector2(1f, 1f);
            badgeRt.anchoredPosition = new Vector2(-30, -30);
            badgeRt.sizeDelta = new Vector2(240, 60);

            Image badgeBg = statBadge.AddComponent<Image>();
            badgeBg.color = new Color(0.12f, 0.16f, 0.25f, 0.9f);

            GameObject badgeTextObj = CreateUIText(statBadge.transform, "StatBadgeText", "SHOT ON GOAL\n+30", 18, TextAnchor.MiddleCenter, Color.yellow, uiFont);
            RectTransform btRt = badgeTextObj.GetComponent<RectTransform>();
            btRt.anchorMin = Vector2.zero;
            btRt.anchorMax = Vector2.one;
            btRt.offsetMin = Vector2.zero;
            btRt.offsetMax = Vector2.zero;
            hud.statNotificationBadge = statBadge;
            hud.statBadgeText = badgeTextObj.GetComponent<Text>();
            statBadge.SetActive(false);

            // 6. Pause Menu UI
            GameObject pauseObj = new GameObject("PauseManager");
            pauseObj.transform.SetParent(canvasObj.transform, false);
            pauseObj.AddComponent<PauseMenuUI>();

            // 7. Match Result UI
            GameObject resultObj = new GameObject("MatchResultManager");
            resultObj.transform.SetParent(canvasObj.transform, false);
            resultObj.AddComponent<MatchResultUI>();

            return hud;
        }

        private GameObject CreateUIText(Transform parent, string name, string initialText, int fontSize, TextAnchor alignment, Color color, Font font)
        {
            GameObject textObj = new GameObject(name);
            textObj.transform.SetParent(parent, false);
            Text text = textObj.AddComponent<Text>();
            text.text = initialText;
            text.fontSize = fontSize;
            text.font = font;
            text.alignment = alignment;
            text.color = color;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            return textObj;
        }

        private void SetupMatchEngine(BallController ball, CarController playerCar, CarController botCar, InGameHUD hud, AudioManager audioMgr)
        {
            GameObject matchRoot = GameObject.Find("RL_MatchEngine");
            if (matchRoot == null)
            {
                matchRoot = new GameObject("RL_MatchEngine");
            }

            ArenaManager arenaMgr = matchRoot.GetComponent<ArenaManager>();
            if (arenaMgr == null) arenaMgr = matchRoot.AddComponent<ArenaManager>();

            arenaMgr.ball = ball;
            arenaMgr.blueCars.Clear();
            if (playerCar != null) arenaMgr.blueCars.Add(playerCar);

            arenaMgr.orangeCars.Clear();
            if (botCar != null) arenaMgr.orangeCars.Add(botCar);

            if (hud != null)
            {
                arenaMgr.inGameHUD = hud;
                if (hud.countdownNumberText != null) arenaMgr.announcementText = hud.countdownNumberText;
            }

            if (audioMgr != null)
            {
                arenaMgr.audioSource = audioMgr.sfxSource;
                arenaMgr.countdownBeep = audioMgr.countdownBeepClip;
                arenaMgr.goWhistle = audioMgr.goBeepClip;
                arenaMgr.goalHorn = audioMgr.goalHornClip;
                arenaMgr.matchOverBuzzer = audioMgr.dodgeClip;
            }

            // Boost Manager
            BoostManager boostMgr = matchRoot.GetComponent<BoostManager>();
            if (boostMgr == null) boostMgr = matchRoot.AddComponent<BoostManager>();
            boostMgr.RefreshPadList();

            // Scoreboard Manager & Player Progression
            ScoreboardManager scoreMgr = matchRoot.GetComponent<ScoreboardManager>();
            if (scoreMgr == null) scoreMgr = matchRoot.AddComponent<ScoreboardManager>();

            PlayerProgression prog = matchRoot.GetComponent<PlayerProgression>();
            if (prog == null) prog = matchRoot.AddComponent<PlayerProgression>();
        }
    }
}
