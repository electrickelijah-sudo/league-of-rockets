using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Manages XP accumulation, level ups, coin payouts, and match stat recording.
    /// </summary>
    public class PlayerProgression : MonoBehaviour
    {
        public static PlayerProgression Instance { get; private set; }

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);
        }

        public int GetXPForNextLevel(int level)
        {
            return 800 + (level * 250);
        }

        public void AddMatchResults(bool won, int goals, int saves, int shots, int assists, float durationSec)
        {
            SaveData data = SaveSystem.CurrentData;

            // Career Stats
            data.stats.matchesPlayed++;
            if (won) data.stats.wins++;
            else data.stats.losses++;

            data.stats.goals += goals;
            data.stats.saves += saves;
            data.stats.shots += shots;
            data.stats.assists += assists;
            data.stats.totalPlayTimeSeconds += durationSec;

            // XP and Coins Calculation
            int earnedXP = (won ? 350 : 150) + (goals * 100) + (saves * 75) + (shots * 20) + (assists * 50);
            int earnedCoins = (won ? 50 : 20) + (goals * 10) + (saves * 5);

            data.currentXP += earnedXP;
            data.coins += earnedCoins;

            // Level Up Loop
            int neededXP = GetXPForNextLevel(data.playerLevel);
            while (data.currentXP >= neededXP)
            {
                data.currentXP -= neededXP;
                data.playerLevel++;
                data.coins += 100; // Level up coin bonus
                Debug.Log($"<color=yellow>[Progression]</color> LEVEL UP! Reached Level {data.playerLevel}!");
                neededXP = GetXPForNextLevel(data.playerLevel);
            }

            SaveSystem.Save();
        }

        public void AddMatchRewards(bool won, int bonusXP, int bonusCoins)
        {
            SaveData data = SaveSystem.CurrentData;
            data.stats.matchesPlayed++;
            if (won) data.stats.wins++;
            else data.stats.losses++;

            data.currentXP += bonusXP;
            data.coins += bonusCoins;

            int neededXP = GetXPForNextLevel(data.playerLevel);
            while (data.currentXP >= neededXP)
            {
                data.currentXP -= neededXP;
                data.playerLevel++;
                data.coins += 100;
                Debug.Log($"<color=yellow>[Progression]</color> LEVEL UP! Reached Level {data.playerLevel}!");
                neededXP = GetXPForNextLevel(data.playerLevel);
            }

            SaveSystem.Save();
        }
    }
}
