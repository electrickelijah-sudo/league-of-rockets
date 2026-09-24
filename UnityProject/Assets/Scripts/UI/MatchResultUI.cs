using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace RocketLeague
{
    /// <summary>
    /// Post-match results screen: Victory/Defeat banner, score recap, XP/Coin payout bar,
    /// Rematch, and Return to Main Menu.
    /// </summary>
    public class MatchResultUI : MonoBehaviour
    {
        [Header("=== UI ELEMENTS ===")]
        public GameObject rootPanel;
        public Text outcomeBannerText;
        public Text finalScoreText;
        public Text earnedXpText;
        public Text earnedCoinsText;
        public Slider xpProgressBar;

        public void ShowResults(bool won, int blueScore, int orangeScore, int earnedXP, int earnedCoins)
        {
            if (rootPanel != null) rootPanel.SetActive(true);

            if (outcomeBannerText != null)
            {
                outcomeBannerText.text = won ? "VICTORY!" : "DEFEAT";
                outcomeBannerText.color = won ? new Color(0f, 0.85f, 1f) : new Color(1f, 0.35f, 0f);
            }

            if (finalScoreText != null)
            {
                finalScoreText.text = $"BLUE {blueScore}  -  {orangeScore} ORANGE";
            }

            if (earnedXpText != null) earnedXpText.text = $"+{earnedXP} XP";
            if (earnedCoinsText != null) earnedCoinsText.text = $"+{earnedCoins} COINS";

            SaveData data = SaveSystem.CurrentData;
            int nextLvlXP = 800 + (data.playerLevel * 250);
            if (xpProgressBar != null)
            {
                xpProgressBar.maxValue = nextLvlXP;
                xpProgressBar.value = data.currentXP;
            }
        }

        public void OnClickRematch()
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }

        public void OnClickReturnToMenu()
        {
            SceneManager.LoadScene(0);
        }
    }
}
