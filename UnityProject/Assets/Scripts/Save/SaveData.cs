using System;
using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    [Serializable]
    public class EquippedLoadout
    {
        public string chassisId = "apex_vanguard";
        public string primaryPaintColorHex = "#0066FF"; // Cobalt Blue
        public string secondaryPaintColorHex = "#FFFFFF"; // Frost White
        public string wheelsId = "tuner_aero";
        public string boostEffectId = "hyper_cyan";
        public string boostTrailId = "hyper_cyan"; // backward compatibility
        public string trailId = "laser_streak";
        public string goalExplosionId = "shockwave_burst";
        public string engineSoundId = "twin_turbo_v6";
    }

    [Serializable]
    public class CareerStats
    {
        public int matchesPlayed = 0;
        public int wins = 0;
        public int losses = 0;
        public int goals = 0;
        public int saves = 0;
        public int assists = 0;
        public int shots = 0;
        public float totalPlayTimeSeconds = 0f;

        public float WinRate => matchesPlayed > 0 ? ((float)wins / matchesPlayed) * 100f : 0f;
    }

    [Serializable]
    public class GameSettingsData
    {
        public float masterVolume = 1.0f;
        public float musicVolume = 0.8f;
        public float sfxVolume = 1.0f;
        public float crowdVolume = 0.85f;

        public float cameraDistance = 13.0f;
        public float cameraHeight = 4.8f;
        public float cameraFov = 72.0f;
        public bool cameraShake = true;
        public bool ballCameraToggle = true;

        public int graphicsQualityIndex = 2; // High
        public bool fullscreen = true;
        public int targetFrameRate = 60;
        public int botDifficultyIndex = 1; // 0 = Easy, 1 = Medium, 2 = Hard
    }

    /// <summary>
    /// Root persistent save model serialized to JSON on disk.
    /// </summary>
    [Serializable]
    public class SaveData
    {
        public string playerName = "Apex Striker";
        public int playerLevel = 1;
        public int currentXP = 0;
        public int coins = 250;

        public EquippedLoadout loadout = new EquippedLoadout();
        public CareerStats stats = new CareerStats();
        public GameSettingsData settings = new GameSettingsData();

        public List<string> unlockedCosmetics = new List<string>
        {
            "apex_vanguard", "viper_gt", "specter_rs",
            "tuner_aero", "muscle_star", "cyber_blade",
            "hyper_cyan", "plasma_orange", "frost_glacier",
            "shockwave_standard", "solar_flare", "cryo_blast",
            "sunset_circuit", "neon_metro", "frozen_peak"
        };
    }
}
