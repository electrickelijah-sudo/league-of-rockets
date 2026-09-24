using UnityEngine;

namespace RocketLeague
{
    public enum ArenaThemeType
    {
        ForbiddenTemple, // Traditional Japanese sanctuary with pagoda towers, moon bridges, cherry blossoms, and Zen court
        SunsetCircuit,   // Coastal golden-hour stadium
        NeonMetro,       // Cyberpunk metropolis night arena
        FrozenPeak       // Alpine glacial mountain stadium
    }

    /// <summary>
    /// Manages stadium atmospheric theming, lighting, skybox color, and materials across
    /// official arenas including Forbidden Temple, Sunset Circuit, Neon Metro, and Frozen Peak.
    /// </summary>
    [ExecuteInEditMode]
    public class ArenaThemeManager : MonoBehaviour
    {
        [Header("=== ARENA THEME ===")]
        public ArenaThemeType currentTheme = ArenaThemeType.SunsetCircuit;

        [Header("=== LIGHTING REFERENCES ===")]
        public Light mainDirectionalLight;
        public Light blueGoalLight;
        public Light orangeGoalLight;

        [Header("=== POST-PROCESSING & ATMOSPHERIC SETTINGS ===")]
        [Tooltip("Bloom threshold and intensity for emissive materials, boost flames, and floodlights")]
        public float bloomIntensity = 1.25f;
        public float bloomThreshold = 0.85f;

        [Tooltip("ACES Tonemapping exposure compensation")]
        public float toneMappingExposure = 1.35f;

        [Tooltip("Screen-space Ambient Occlusion intensity for ground contact")]
        public float ambientOcclusionIntensity = 0.65f;

        [Tooltip("Screen-space reflections for metallic arena elements and wet turf")]
        public bool enableReflections = true;

        [Header("=== RENDERERS TO TINT ===")]
        public Renderer fieldTurfRenderer;
        public Renderer arenaDomeRenderer;
        public Renderer stadiumWallsRenderer;

        private void Start()
        {
            ApplyTheme(currentTheme);
        }

        [ContextMenu("Apply Current Theme")]
        public void ApplyCurrentTheme()
        {
            ApplyTheme(currentTheme);
        }

        public void ApplyTheme(ArenaThemeType theme)
        {
            currentTheme = theme;

            switch (theme)
            {
                case ArenaThemeType.ForbiddenTemple:
                    ApplyForbiddenTemple();
                    break;
                case ArenaThemeType.SunsetCircuit:
                    ApplySunsetCircuit();
                    break;
                case ArenaThemeType.NeonMetro:
                    ApplyNeonMetro();
                    break;
                case ArenaThemeType.FrozenPeak:
                    ApplyFrozenPeak();
                    break;
            }

            ConfigureGoalLights();
            Debug.Log($"<color=orange>[ArenaThemeManager]</color> Applied theme: {theme} with ACES tone mapping and PBR lighting.");
        }

        private void ConfigureGoalLights()
        {
            if (blueGoalLight != null)
            {
                blueGoalLight.type = LightType.Point;
                blueGoalLight.color = new Color(0f, 0.8f, 1f);
                blueGoalLight.intensity = 2.5f;
                blueGoalLight.range = 25f;
            }

            if (orangeGoalLight != null)
            {
                orangeGoalLight.type = LightType.Point;
                orangeGoalLight.color = new Color(1f, 0.45f, 0f);
                orangeGoalLight.intensity = 2.5f;
                orangeGoalLight.range = 25f;
            }
        }

        private void ApplyForbiddenTemple()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.70f, 0.54f, 0.65f); // Mountain twilight rose & indigo
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.32f, 0.24f, 0.42f);    // Misty twilight mountain haze
            RenderSettings.fogDensity = 0.0028f;

            if (mainDirectionalLight != null)
            {
                mainDirectionalLight.color = new Color(1.0f, 0.78f, 0.52f); // Golden sunset sunbeams
                mainDirectionalLight.intensity = 1.6f;
                mainDirectionalLight.transform.rotation = Quaternion.Euler(30f, -40f, 0f);
                mainDirectionalLight.shadows = LightShadows.Soft;
                mainDirectionalLight.shadowResolution = UnityEngine.Rendering.LightShadowResolution.High;
                mainDirectionalLight.shadowStrength = 0.85f;
            }

            if (Camera.main != null)
            {
                Camera.main.clearFlags = CameraClearFlags.SolidColor;
                Camera.main.backgroundColor = new Color(0.22f, 0.16f, 0.32f); // Twilight mountain dusk sky
            }

            if (fieldTurfRenderer != null && fieldTurfRenderer.sharedMaterial != null)
            {
                if (fieldTurfRenderer.sharedMaterial.mainTexture != null)
                    fieldTurfRenderer.sharedMaterial.color = Color.white;
                else
                    fieldTurfRenderer.sharedMaterial.color = new Color(0.08f, 0.12f, 0.11f);
            }

            if (arenaDomeRenderer != null && arenaDomeRenderer.sharedMaterial != null)
            {
                arenaDomeRenderer.sharedMaterial.color = new Color(0.65f, 0.38f, 0.68f, 0.18f); // Ethereal purple/rose shield
            }
        }

        private void ApplySunsetCircuit()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.65f, 0.48f, 0.58f); // Dusk rose-indigo ambient
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.55f, 0.32f, 0.38f);    // Distant mountain sunset haze
            RenderSettings.fogDensity = 0.0007f;                          // Adjusted for 3x stadium scale

            if (mainDirectionalLight != null)
            {
                mainDirectionalLight.color = new Color(1.0f, 0.72f, 0.45f); // Golden sunset sunbeams
                mainDirectionalLight.intensity = 1.8f;
                mainDirectionalLight.transform.rotation = Quaternion.Euler(32f, -35f, 0f);
                mainDirectionalLight.shadows = LightShadows.Soft;
                mainDirectionalLight.shadowResolution = UnityEngine.Rendering.LightShadowResolution.High;
                mainDirectionalLight.shadowStrength = 0.85f;
            }

            if (Camera.main != null)
            {
                Camera.main.clearFlags = CameraClearFlags.SolidColor;
                Camera.main.backgroundColor = new Color(0.12f, 0.10f, 0.22f); // Deep twilight indigo sky
            }

            if (fieldTurfRenderer != null && fieldTurfRenderer.sharedMaterial != null)
            {
                fieldTurfRenderer.sharedMaterial.color = Color.white;
            }

            if (arenaDomeRenderer != null && arenaDomeRenderer.sharedMaterial != null)
            {
                arenaDomeRenderer.sharedMaterial.color = new Color(0.15f, 1.0f, 0.45f, 0.25f); // Neon green wireframe glow
            }
        }

        private void ApplyNeonMetro()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.15f, 0.18f, 0.35f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.08f, 0.05f, 0.18f);
            RenderSettings.fogDensity = 0.004f;

            if (mainDirectionalLight != null)
            {
                mainDirectionalLight.color = new Color(0.35f, 0.45f, 0.95f);
                mainDirectionalLight.intensity = 0.85f;
                mainDirectionalLight.transform.rotation = Quaternion.Euler(75f, 30f, 0f);
            }

            if (fieldTurfRenderer != null && fieldTurfRenderer.sharedMaterial != null)
            {
                fieldTurfRenderer.sharedMaterial.color = new Color(0.08f, 0.16f, 0.22f);
            }

            if (arenaDomeRenderer != null && arenaDomeRenderer.sharedMaterial != null)
            {
                arenaDomeRenderer.sharedMaterial.color = new Color(0f, 0.9f, 1f, 0.35f);
            }
        }

        private void ApplyFrozenPeak()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.75f, 0.85f, 0.95f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.75f, 0.85f, 0.98f);
            RenderSettings.fogDensity = 0.003f;

            if (mainDirectionalLight != null)
            {
                mainDirectionalLight.color = new Color(0.92f, 0.96f, 1.0f);
                mainDirectionalLight.intensity = 1.35f;
                mainDirectionalLight.transform.rotation = Quaternion.Euler(45f, -60f, 0f);
            }

            if (fieldTurfRenderer != null && fieldTurfRenderer.sharedMaterial != null)
            {
                fieldTurfRenderer.sharedMaterial.color = new Color(0.35f, 0.65f, 0.72f);
            }

            if (arenaDomeRenderer != null && arenaDomeRenderer.sharedMaterial != null)
            {
                arenaDomeRenderer.sharedMaterial.color = new Color(0.8f, 0.95f, 1f, 0.45f);
            }
        }
    }
}
