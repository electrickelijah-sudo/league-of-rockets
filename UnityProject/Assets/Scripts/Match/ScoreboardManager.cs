using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    [System.Serializable]
    public class PlayerMatchStats
    {
        public string playerName = "Player";
        public bool isBlueTeam = true;
        public bool isAI = false;
        public int score = 0;
        public int goals = 0;
        public int assists = 0;
        public int saves = 0;
        public int shots = 0;

        public void AddGoal()
        {
            goals++;
            score += 100;
        }

        public void AddSave()
        {
            saves++;
            score += 75;
        }

        public void AddShot()
        {
            shots++;
            score += 20;
        }

        public void AddAssist()
        {
            assists++;
            score += 50;
        }

        public void AddFirstTouch()
        {
            score += 25;
        }
    }

    /// <summary>
    /// Tracks in-game player scores, shots, saves, assists, and calculates match rewards.
    /// </summary>
    public class ScoreboardManager : MonoBehaviour
    {
        public static ScoreboardManager Instance { get; private set; }

        public List<PlayerMatchStats> allPlayerStats = new List<PlayerMatchStats>();
        public PlayerMatchStats humanPlayerStats = new PlayerMatchStats { playerName = "Apex Striker", isBlueTeam = true, isAI = false };

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);

            if (!allPlayerStats.Contains(humanPlayerStats))
            {
                allPlayerStats.Add(humanPlayerStats);
            }
        }

        public void RegisterStat(string playerName, string statType)
        {
            PlayerMatchStats stats = allPlayerStats.Find(p => p.playerName == playerName) ?? humanPlayerStats;

            switch (statType)
            {
                case "GOAL": stats.AddGoal(); break;
                case "SAVE": stats.AddSave(); break;
                case "SHOT": stats.AddShot(); break;
                case "ASSIST": stats.AddAssist(); break;
                case "FIRST_TOUCH": stats.AddFirstTouch(); break;
            }
        }

        public PlayerMatchStats GetMVP()
        {
            PlayerMatchStats mvp = null;
            int highestScore = -1;
            foreach (var p in allPlayerStats)
            {
                if (p.score > highestScore)
                {
                    highestScore = p.score;
                    mvp = p;
                }
            }
            return mvp;
        }
    }
}
