using System;
using UnityEngine;

namespace RocketLeague
{
    public enum CosmeticCategory
    {
        CarBody,
        PrimaryPaint,
        SecondaryPaint,
        Wheels,
        BoostEffect,
        Trail,
        GoalExplosion,
        EngineSound,
        Decal
    }

    public enum RarityTier
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary
    }

    [Serializable]
    public class CosmeticItem
    {
        public string id;
        public string displayName;
        public CosmeticCategory category;
        public RarityTier rarity;
        public Color primaryColor = Color.white;
        public Color secondaryColor = Color.white;
        public string hexColor = "#FFFFFF";
        public string iconEmoji = "🚗";
        public string description = "";
        public int unlockLevel = 1;
        public int coinCost = 0;

        public static Color GetRarityColor(RarityTier tier)
        {
            switch (tier)
            {
                case RarityTier.Common:    return new Color(0.7f, 0.7f, 0.7f);
                case RarityTier.Uncommon:  return new Color(0.2f, 0.8f, 0.2f);
                case RarityTier.Rare:      return new Color(0.1f, 0.5f, 1.0f);
                case RarityTier.Epic:      return new Color(0.75f, 0.2f, 0.95f);
                case RarityTier.Legendary: return new Color(1.0f, 0.75f, 0.0f);
                default:                   return Color.white;
            }
        }
    }
}
