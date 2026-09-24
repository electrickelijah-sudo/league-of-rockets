using UnityEngine;

namespace RocketLeague
{
    public enum GameModeType
    {
        FreePlay,
        Duel1v1,
        Doubles2v2,
        Standard3v3,
        LocalVsBots,
        Training
    }

    /// <summary>
    /// Configuration data for match mode settings, team sizes, and bot setups.
    /// </summary>
    [System.Serializable]
    public class GameModeConfig
    {
        public GameModeType modeType = GameModeType.Duel1v1;
        public int teamSize = 1;
        public float matchDuration = 300f; // 5:00
        public bool hasBots = true;
        public BotController.BotDifficulty botDifficulty = BotController.BotDifficulty.Pro;
        public bool infiniteBoost = false;

        public static GameModeConfig CreateDefault(GameModeType type)
        {
            GameModeConfig config = new GameModeConfig { modeType = type };
            switch (type)
            {
                case GameModeType.FreePlay:
                    config.teamSize = 1;
                    config.matchDuration = 0f; // Unlimited
                    config.hasBots = false;
                    config.infiniteBoost = true;
                    break;
                case GameModeType.Duel1v1:
                    config.teamSize = 1;
                    config.matchDuration = 300f;
                    config.hasBots = true;
                    break;
                case GameModeType.Doubles2v2:
                    config.teamSize = 2;
                    config.matchDuration = 300f;
                    config.hasBots = true;
                    break;
                case GameModeType.Standard3v3:
                    config.teamSize = 3;
                    config.matchDuration = 300f;
                    config.hasBots = true;
                    break;
                case GameModeType.LocalVsBots:
                    config.teamSize = 3;
                    config.matchDuration = 300f;
                    config.hasBots = true;
                    break;
                case GameModeType.Training:
                    config.teamSize = 1;
                    config.matchDuration = 0f;
                    config.hasBots = false;
                    config.infiniteBoost = true;
                    break;
            }
            return config;
        }
    }
}
