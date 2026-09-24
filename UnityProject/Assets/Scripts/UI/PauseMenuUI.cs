using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace RocketLeague
{
    /// <summary>
    /// In-match pause menu with Resume, Restart Match, Settings, and Return to Menu.
    /// </summary>
    public class PauseMenuUI : MonoBehaviour
    {
        public GameObject pauseCanvas;
        public GameObject settingsSubPanel;

        private bool _isPaused = false;

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                TogglePause();
            }
        }

        public void TogglePause()
        {
            _isPaused = !_isPaused;
            if (pauseCanvas != null) pauseCanvas.SetActive(_isPaused);
            Time.timeScale = _isPaused ? 0f : 1f;
        }

        public void OnClickResume()
        {
            TogglePause();
        }

        public void OnClickRestart()
        {
            Time.timeScale = 1f;
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }

        public void OnClickSettings()
        {
            if (settingsSubPanel != null) settingsSubPanel.SetActive(true);
        }

        public void OnClickMainMenu()
        {
            Time.timeScale = 1f;
            SceneManager.LoadScene(0); // Main menu
        }
    }
}
