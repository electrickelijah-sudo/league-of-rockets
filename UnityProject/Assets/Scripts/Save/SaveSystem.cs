using System;
using System.IO;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Handles persistent JSON serialization and disk I/O to Application.persistentDataPath.
    /// </summary>
    public static class SaveSystem
    {
        private static string SaveFilePath => Path.Combine(Application.persistentDataPath, "turbostrike_save.json");
        private static SaveData _cachedData;

        public static SaveData CurrentData
        {
            get
            {
                if (_cachedData == null) Load();
                return _cachedData;
            }
        }

        public static void Save()
        {
            try
            {
                if (_cachedData == null) _cachedData = new SaveData();
                string json = JsonUtility.ToJson(_cachedData, true);
                File.WriteAllText(SaveFilePath, json);
                Debug.Log($"<color=green>[SaveSystem]</color> Game saved successfully to: {SaveFilePath}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SaveSystem] Failed to save game: {ex.Message}");
            }
        }

        public static SaveData Load()
        {
            try
            {
                if (File.Exists(SaveFilePath))
                {
                    string json = File.ReadAllText(SaveFilePath);
                    _cachedData = JsonUtility.FromJson<SaveData>(json);
                    Debug.Log("<color=green>[SaveSystem]</color> Loaded existing save profile.");
                }
                else
                {
                    _cachedData = new SaveData();
                    Save();
                    Debug.Log("<color=cyan>[SaveSystem]</color> Created fresh save profile.");
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[SaveSystem] Error loading save, creating fallback: {ex.Message}");
                _cachedData = new SaveData();
            }

            return _cachedData;
        }

        public static void ResetProfile()
        {
            _cachedData = new SaveData();
            Save();
        }
    }
}
