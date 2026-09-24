using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Central catalog of original cosmetic unlockables, items, paints, wheels, and effects.
    /// </summary>
    public static class CosmeticDatabase
    {
        private static List<CosmeticItem> _items;

        public static List<CosmeticItem> GetAllItems()
        {
            if (_items == null) Initialize();
            return _items;
        }

        private static void Initialize()
        {
            _items = new List<CosmeticItem>
            {
                // ==================== 1. CAR BODIES ====================
                new CosmeticItem { id = "apex_vanguard", displayName = "Apex Vanguard", category = CosmeticCategory.CarBody, rarity = RarityTier.Common, iconEmoji = "🏎️", description = "Agile, aerodynamic formula-rally striker with low drag and GT spoiler.", unlockLevel = 1 },
                new CosmeticItem { id = "viper_gt", displayName = "Viper GT", category = CosmeticCategory.CarBody, rarity = RarityTier.Rare, iconEmoji = "🏎️", description = "Muscular widebody coupe with hood scoop and massive bumper pop.", unlockLevel = 3, coinCost = 500 },
                new CosmeticItem { id = "specter_rs", displayName = "Specter RS", category = CosmeticCategory.CarBody, rarity = RarityTier.Legendary, iconEmoji = "🏎️", description = "Low-slung exotic wedge hypercar with active aero splitters.", unlockLevel = 8, coinCost = 1200 },
                new CosmeticItem { id = "ion_phantom", displayName = "Ion Phantom", category = CosmeticCategory.CarBody, rarity = RarityTier.Epic, iconEmoji = "🏎️", description = "Cybernetic stealth interceptor with angular aero blades.", unlockLevel = 5, coinCost = 850 },
                new CosmeticItem { id = "titan_juggernaut", displayName = "Titan Juggernaut", category = CosmeticCategory.CarBody, rarity = RarityTier.Rare, iconEmoji = "🚙", description = "Armored high-clearance off-road striker with external bullbars.", unlockLevel = 4, coinCost = 600 },

                // ==================== 2. PRIMARY PAINTS ====================
                new CosmeticItem { id = "paint_cobalt_blue", displayName = "Cobalt Blue", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Common, hexColor = "#0066FF", primaryColor = new Color(0f, 0.4f, 1f), iconEmoji = "🎨", unlockLevel = 1 },
                new CosmeticItem { id = "paint_crimson_blaze", displayName = "Crimson Blaze", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Common, hexColor = "#FF1A35", primaryColor = new Color(1f, 0.1f, 0.2f), iconEmoji = "🎨", unlockLevel = 1 },
                new CosmeticItem { id = "paint_solar_gold", displayName = "Solar Gold", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Uncommon, hexColor = "#FFB300", primaryColor = new Color(1f, 0.7f, 0f), iconEmoji = "🎨", unlockLevel = 2, coinCost = 150 },
                new CosmeticItem { id = "paint_emerald_surge", displayName = "Emerald Surge", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Uncommon, hexColor = "#00E676", primaryColor = new Color(0f, 0.9f, 0.46f), iconEmoji = "🎨", unlockLevel = 2, coinCost = 150 },
                new CosmeticItem { id = "paint_obsidian_shadow", displayName = "Obsidian Shadow", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Rare, hexColor = "#16161A", primaryColor = new Color(0.09f, 0.09f, 0.1f), iconEmoji = "🎨", unlockLevel = 4, coinCost = 300 },
                new CosmeticItem { id = "paint_ultraviolet", displayName = "Ultraviolet", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Epic, hexColor = "#8E24AA", primaryColor = new Color(0.55f, 0.14f, 0.67f), iconEmoji = "🎨", unlockLevel = 6, coinCost = 450 },
                new CosmeticItem { id = "paint_cyber_teal", displayName = "Cyber Neon Teal", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Epic, hexColor = "#00E5FF", primaryColor = new Color(0f, 0.9f, 1f), iconEmoji = "🎨", unlockLevel = 6, coinCost = 450 },
                new CosmeticItem { id = "paint_pearl_white", displayName = "Pearl White", category = CosmeticCategory.PrimaryPaint, rarity = RarityTier.Legendary, hexColor = "#F5F5FA", primaryColor = new Color(0.96f, 0.96f, 0.98f), iconEmoji = "🎨", unlockLevel = 9, coinCost = 700 },

                // ==================== 3. SECONDARY PAINTS ====================
                new CosmeticItem { id = "paint_frost_white", displayName = "Frost White", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Common, hexColor = "#FFFFFF", secondaryColor = Color.white, iconEmoji = "🖌️", unlockLevel = 1 },
                new CosmeticItem { id = "paint_carbon_graphite", displayName = "Carbon Graphite", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Common, hexColor = "#2A2A2E", secondaryColor = new Color(0.16f, 0.16f, 0.18f), iconEmoji = "🖌️", unlockLevel = 1 },
                new CosmeticItem { id = "paint_electric_lime", displayName = "Electric Lime", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Uncommon, hexColor = "#76FF03", secondaryColor = new Color(0.46f, 1f, 0.01f), iconEmoji = "🖌️", unlockLevel = 2, coinCost = 150 },
                new CosmeticItem { id = "paint_flare_orange", displayName = "Flare Orange", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Uncommon, hexColor = "#FF6D00", secondaryColor = new Color(1f, 0.43f, 0f), iconEmoji = "🖌️", unlockLevel = 3, coinCost = 200 },
                new CosmeticItem { id = "paint_void_black", displayName = "Deep Void Black", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Rare, hexColor = "#0A0A0C", secondaryColor = new Color(0.04f, 0.04f, 0.05f), iconEmoji = "🖌️", unlockLevel = 4, coinCost = 250 },
                new CosmeticItem { id = "paint_silver_chrome", displayName = "Chrome Silver", category = CosmeticCategory.SecondaryPaint, rarity = RarityTier.Epic, hexColor = "#B0B4BC", secondaryColor = new Color(0.69f, 0.7f, 0.74f), iconEmoji = "🖌️", unlockLevel = 7, coinCost = 500 },

                // ==================== 4. WHEELS ====================
                new CosmeticItem { id = "tuner_aero", displayName = "Tuner Aero", category = CosmeticCategory.Wheels, rarity = RarityTier.Common, iconEmoji = "🔘", description = "Lightweight 5-spoke racing alloy rims.", unlockLevel = 1 },
                new CosmeticItem { id = "vortex_turbine", displayName = "Vortex Turbine", category = CosmeticCategory.Wheels, rarity = RarityTier.Uncommon, iconEmoji = "🌀", description = "Aerodynamic spiral turbine fan blades.", unlockLevel = 2, coinCost = 250 },
                new CosmeticItem { id = "cyber_blade", displayName = "Cyber Blade", category = CosmeticCategory.Wheels, rarity = RarityTier.Epic, iconEmoji = "💿", description = "High-luminance dual-ring neon illuminated rims.", unlockLevel = 5, coinCost = 650 },
                new CosmeticItem { id = "quantum_drift", displayName = "Quantum Drift", category = CosmeticCategory.Wheels, rarity = RarityTier.Legendary, iconEmoji = "🔮", description = "Levitating electromagnetic hubless mag-lev wheels.", unlockLevel = 10, coinCost = 1500 },
                new CosmeticItem { id = "titan_heavy", displayName = "Titan Heavy Duty", category = CosmeticCategory.Wheels, rarity = RarityTier.Rare, iconEmoji = "⚙️", description = "Reinforced 8-lug beadlock off-road wheels.", unlockLevel = 4, coinCost = 400 },

                // ==================== 5. BOOST EFFECTS ====================
                new CosmeticItem { id = "hyper_cyan", displayName = "Hyper Cyan", category = CosmeticCategory.BoostEffect, rarity = RarityTier.Common, hexColor = "#00F0FF", primaryColor = new Color(0f, 0.94f, 1f), iconEmoji = "🚀", description = "High-velocity ion plasma jet with electric cyan sparks.", unlockLevel = 1 },
                new CosmeticItem { id = "solar_flare", displayName = "Solar Flare", category = CosmeticCategory.BoostEffect, rarity = RarityTier.Rare, hexColor = "#FF6600", primaryColor = new Color(1f, 0.4f, 0f), iconEmoji = "🔥", description = "Thermonuclear rocket blast with searing orange embers.", unlockLevel = 3, coinCost = 450 },
                new CosmeticItem { id = "frost_glacier", displayName = "Frost Glacier", category = CosmeticCategory.BoostEffect, rarity = RarityTier.Uncommon, hexColor = "#80E5FF", primaryColor = new Color(0.5f, 0.9f, 1f), iconEmoji = "❄️", description = "Sub-zero cryogenic vapor with crystalline frost needles.", unlockLevel = 2, coinCost = 300 },
                new CosmeticItem { id = "dark_nebula", displayName = "Dark Nebula", category = CosmeticCategory.BoostEffect, rarity = RarityTier.Legendary, hexColor = "#9C27B0", primaryColor = new Color(0.61f, 0.15f, 0.69f), iconEmoji = "🌌", description = "Void rift exhaust with cosmic dark-matter particles.", unlockLevel = 8, coinCost = 1400 },
                new CosmeticItem { id = "emerald_laser", displayName = "Emerald Laser", category = CosmeticCategory.BoostEffect, rarity = RarityTier.Epic, hexColor = "#00FF66", primaryColor = new Color(0f, 1f, 0.4f), iconEmoji = "⚡", description = "High-frequency collimated green laser particle beam.", unlockLevel = 6, coinCost = 800 },

                // ==================== 6. TRAILS (SUPERSONIC RIBBONS) ====================
                new CosmeticItem { id = "laser_streak", displayName = "Laser Streak", category = CosmeticCategory.Trail, rarity = RarityTier.Common, hexColor = "#00E5FF", primaryColor = new Color(0f, 0.9f, 1f), iconEmoji = "✨", description = "Razor-sharp twin glowing laser lines.", unlockLevel = 1 },
                new CosmeticItem { id = "rainbow_aurora", displayName = "Rainbow Aurora", category = CosmeticCategory.Trail, rarity = RarityTier.Legendary, hexColor = "#FF00E5", primaryColor = new Color(1f, 0f, 0.9f), iconEmoji = "🌈", description = "Chromatic prism ribbon with shimmering spectrum wave.", unlockLevel = 9, coinCost = 1600 },
                new CosmeticItem { id = "electric_arc", displayName = "Electric Arc", category = CosmeticCategory.Trail, rarity = RarityTier.Rare, hexColor = "#3D5AFE", primaryColor = new Color(0.24f, 0.35f, 1f), iconEmoji = "⚡", description = "Crackling high-voltage lightning tendrils on turf.", unlockLevel = 4, coinCost = 500 },
                new CosmeticItem { id = "pixel_vapor", displayName = "Pixel Vapor", category = CosmeticCategory.Trail, rarity = RarityTier.Epic, hexColor = "#E040FB", primaryColor = new Color(0.88f, 0.25f, 0.98f), iconEmoji = "👾", description = "Retro 8-bit digital holographic square matrix.", unlockLevel = 7, coinCost = 900 },
                new CosmeticItem { id = "smoke_haze", displayName = "Smoke Haze", category = CosmeticCategory.Trail, rarity = RarityTier.Uncommon, hexColor = "#B0BEC5", primaryColor = new Color(0.7f, 0.75f, 0.77f), iconEmoji = "💨", description = "Dense billowing aerodynamic drift smoke ribbons.", unlockLevel = 2, coinCost = 250 },

                // ==================== 7. GOAL EXPLOSIONS ====================
                new CosmeticItem { id = "shockwave_burst", displayName = "Shockwave Burst", category = CosmeticCategory.GoalExplosion, rarity = RarityTier.Common, hexColor = "#0099FF", iconEmoji = "💥", description = "Kinetic stadium shockwave with radial soundwave rings.", unlockLevel = 1 },
                new CosmeticItem { id = "supernova_flare", displayName = "Supernova Flare", category = CosmeticCategory.GoalExplosion, rarity = RarityTier.Rare, hexColor = "#FF5500", iconEmoji = "✨", description = "Stellar thermonuclear flash with radiating plasma bursts.", unlockLevel = 3, coinCost = 500 },
                new CosmeticItem { id = "cryo_implosion", displayName = "Cryo Implosion", category = CosmeticCategory.GoalExplosion, rarity = RarityTier.Epic, hexColor = "#00FFFF", iconEmoji = "❄️", description = "Glacial flash-freeze crystal shattering shockwave.", unlockLevel = 6, coinCost = 950 },
                new CosmeticItem { id = "singularity_vortex", displayName = "Singularity Vortex", category = CosmeticCategory.GoalExplosion, rarity = RarityTier.Legendary, hexColor = "#7C4DFF", iconEmoji = "🌀", description = "Cosmic black hole vacuum followed by stellar ejection.", unlockLevel = 10, coinCost = 2200 },
                new CosmeticItem { id = "confetti_carnival", displayName = "Confetti Carnival", category = CosmeticCategory.GoalExplosion, rarity = RarityTier.Uncommon, hexColor = "#FFD700", iconEmoji = "🎉", description = "Explosion of stadium fireworks, sparkling ribbons & gold stars.", unlockLevel = 2, coinCost = 350 }
            };
        }

        public static List<CosmeticItem> GetItemsByCategory(CosmeticCategory category)
        {
            return GetAllItems().FindAll(i => i.category == category);
        }

        public static CosmeticItem FindItem(string id)
        {
            return GetAllItems().Find(i => i.id == id);
        }
    }
}
