using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace RocketLeague
{
    /// <summary>
    /// Master main menu UI navigation controller.
    /// Manages sub-panels: PLAY, GARAGE, TRAINING, CUSTOM MATCH, SETTINGS, PROFILE, QUIT.
    /// </summary>
    public class MainMenuUI : MonoBehaviour
    {
        [Header("=== MENU PANELS ===")]
        public GameObject mainPanel;
        public GameObject playModePanel;
        public GameObject arenaSelectPanel;
        public GameObject garagePanel;
        public GameObject customMatchPanel;
        public GameObject settingsPanel;
        public GameObject profilePanel;

        [Header("=== HEADER STATS ===")]
        public Text playerLevelText;
        public Text playerXPText;
        public Text playerCoinsText;

        private GameModeType _selectedMode = GameModeType.Duel1v1;
        private ArenaThemeType _selectedArena = ArenaThemeType.SunsetCircuit;

        private void Start()
        {
            ShowPanel(mainPanel);
            UpdateHeaderStats();
        }

        public void UpdateHeaderStats()
        {
            SaveData data = SaveSystem.CurrentData;
            if (playerLevelText != null) playerLevelText.text = $"LVL {data.playerLevel}";
            if (playerXPText != null) playerXPText.text = $"XP: {data.currentXP} / {800 + data.playerLevel * 250}";
            if (playerCoinsText != null) playerCoinsText.text = $"🪙 {data.coins}";
        }

        public void ShowPanel(GameObject panelToShow)
        {
            if (mainPanel != null) mainPanel.SetActive(panelToShow == mainPanel);
            if (playModePanel != null) playModePanel.SetActive(panelToShow == playModePanel);
            if (arenaSelectPanel != null) arenaSelectPanel.SetActive(panelToShow == arenaSelectPanel);
            if (garagePanel != null) garagePanel.SetActive(panelToShow == garagePanel);
            if (customMatchPanel != null) customMatchPanel.SetActive(panelToShow == customMatchPanel);
            if (settingsPanel != null) settingsPanel.SetActive(panelToShow == settingsPanel);
            if (profilePanel != null) profilePanel.SetActive(panelToShow == profilePanel);

            UpdateHeaderStats();
        }

        // Navigation button callbacks
        public void OnClickPlay() => ShowPanel(playModePanel);
        public void OnClickGarage() => ShowPanel(garagePanel);
        public void OnClickCustomMatch() => ShowPanel(customMatchPanel);
        public void OnClickSettings() => ShowPanel(settingsPanel);
        public void OnClickProfile() => ShowPanel(profilePanel);
        public void OnClickBackToMain() => ShowPanel(mainPanel);

        public void SelectGameMode(int modeIndex)
        {
            _selectedMode = (GameModeType)modeIndex;
            ShowPanel(arenaSelectPanel);
        }

        public void SelectArenaAndLaunch(int arenaIndex)
        {
            _selectedArena = (ArenaThemeType)arenaIndex;
            LaunchMatch(_selectedMode, _selectedArena);
        }

        public void LaunchMatch(GameModeType mode, ArenaThemeType arena)
        {
            Debug.Log($"<color=green>[MainMenuUI]</color> Starting {mode} match in {arena}!");
            // SceneManager.LoadScene can load the stadium scene with configured parameters
            ArenaManager arenaMgr = FindObjectsByType<ArenaManager>(FindObjectsSortMode.None).Length > 0 
                ? FindObjectsByType<ArenaManager>(FindObjectsSortMode.None)[0] : null;

            if (arenaMgr != null)
            {
                gameObject.SetActive(false);
            }
        }

        public void OnClickQuit()
        {
            Debug.Log("[MainMenuUI] Quitting game...");
            Application.Quit();
        }
    }
}
