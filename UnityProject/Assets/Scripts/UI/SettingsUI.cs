using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    /// <summary>
    /// Settings menu options for graphics quality, audio volumes, camera settings, and controls.
    /// </summary>
    public class SettingsUI : MonoBehaviour
    {
        [Header("=== GRAPHICS ===")]
        public Dropdown qualityDropdown;
        public Toggle fullscreenToggle;

        [Header("=== AUDIO ===")]
        public Slider masterVolumeSlider;
        public Slider sfxVolumeSlider;
        public Slider musicVolumeSlider;

        [Header("=== CAMERA ===")]
        public Slider cameraDistanceSlider;
        public Slider cameraFovSlider;
        public Toggle cameraShakeToggle;

        private void Start()
        {
            LoadCurrentSettings();
        }

        public void LoadCurrentSettings()
        {
            GameSettingsData s = SaveSystem.CurrentData.settings;

            if (masterVolumeSlider != null) masterVolumeSlider.value = s.masterVolume;
            if (sfxVolumeSlider != null) sfxVolumeSlider.value = s.sfxVolume;
            if (musicVolumeSlider != null) musicVolumeSlider.value = s.musicVolume;

            if (cameraDistanceSlider != null) cameraDistanceSlider.value = s.cameraDistance;
            if (cameraFovSlider != null) cameraFovSlider.value = s.cameraFov;
            if (cameraShakeToggle != null) cameraShakeToggle.isOn = s.cameraShake;

            if (qualityDropdown != null) qualityDropdown.value = s.graphicsQualityIndex;
            if (fullscreenToggle != null) fullscreenToggle.isOn = s.fullscreen;
        }

        public void ApplyAndSaveSettings()
        {
            GameSettingsData s = SaveSystem.CurrentData.settings;

            if (masterVolumeSlider != null) s.masterVolume = masterVolumeSlider.value;
            if (sfxVolumeSlider != null) s.sfxVolume = sfxVolumeSlider.value;
            if (musicVolumeSlider != null) s.musicVolume = musicVolumeSlider.value;

            if (cameraDistanceSlider != null) s.cameraDistance = cameraDistanceSlider.value;
            if (cameraFovSlider != null) s.cameraFov = cameraFovSlider.value;
            if (cameraShakeToggle != null) s.cameraShake = cameraShakeToggle.isOn;

            if (qualityDropdown != null)
            {
                s.graphicsQualityIndex = qualityDropdown.value;
                QualitySettings.SetQualityLevel(s.graphicsQualityIndex);
            }

            if (fullscreenToggle != null)
            {
                s.fullscreen = fullscreenToggle.isOn;
                Screen.fullScreen = s.fullscreen;
            }

            AudioListener.volume = s.masterVolume;
            SaveSystem.Save();
            Debug.Log("<color=green>[SettingsUI]</color> Settings applied and saved successfully!");
        }
    }
}
