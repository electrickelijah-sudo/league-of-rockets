using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace RocketLeague
{
    /// <summary>
    /// Master Car Customization Garage Controller:
    /// - 3D Turntable preview area with slow, smooth rotation
    /// - Comprehensive customization across all 7 categories:
    ///   1. Car Body (Apex Vanguard, Viper GT, Specter RS, Ion Phantom, Titan Juggernaut)
    ///   2. Primary Paint (High-gloss metallic automotive finishes)
    ///   3. Secondary Paint (Spoilers, skirts, splitters, diffusers, bullbars)
    ///   4. Wheels (Tuner Aero, Vortex Turbine, Cyber Blade, Quantum Drift, Titan Heavy)
    ///   5. Boost Effect (Ion Plasma, Solar Flare, Frost Glacier, Dark Nebula, Emerald Laser)
    ///   6. Trail (Laser Streak, Rainbow Aurora, Electric Arc, Pixel Vapor, Smoke Haze)
    ///   7. Goal Explosion (Shockwave Burst, Supernova Flare, Cryo Implosion, Singularity Vortex, Confetti Carnival)
    /// - Real-time visual feedback and sound effects on equip
    /// - Persistent saving to disk JSON via SaveSystem
    /// </summary>
    public class GarageManager : MonoBehaviour
    {
        public static GarageManager Instance { get; private set; }

        [Header("=== PREVIEW TURNTABLE ===")]
        public Transform turntableTransform;
        public float turntableRotateSpeed = 22f; // Slow, majestic rotation
        public CarPrefabBuilder previewCarBuilder;
        public CarCustomizer previewCustomizer;

        [Header("=== PREVIEW FX ===")]
        public ParticleSystem previewBoostParticles;
        public ParticleSystem previewExplosionParticles;
        public TrailRenderer[] previewTrails;

        [Header("=== UI CANVAS & TABS ===")]
        public GameObject garageCanvas;
        public Transform categoryTabsContainer;
        public Transform itemGridContainer;
        public Text categoryTitleText;
        public Text itemDetailsText;

        private CosmeticCategory _currentCategory = CosmeticCategory.CarBody;
        private List<GameObject> _spawnedCards = new List<GameObject>();

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this)
            {
                Destroy(gameObject);
                return;
            }
        }

        private void Start()
        {
            EnsureTurntableSetup();
            LoadEquippedLoadout();
            BuildGarageUI();
        }

        private void Update()
        {
            // Rotate the car slowly on the turntable preview platform
            if (turntableTransform != null)
            {
                turntableTransform.Rotate(Vector3.up, turntableRotateSpeed * Time.deltaTime, Space.World);
            }
        }

        private void EnsureTurntableSetup()
        {
            if (turntableTransform == null)
            {
                GameObject tt = GameObject.Find("GarageTurntable");
                if (tt == null)
                {
                    tt = new GameObject("GarageTurntable");
                    tt.transform.position = new Vector3(0, 0, 0);

                    // Turntable circular disc platform
                    GameObject disc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    disc.name = "TurntablePlatform";
                    disc.transform.SetParent(tt.transform, false);
                    disc.transform.localScale = new Vector3(5.5f, 0.15f, 5.5f);
                    disc.transform.localPosition = new Vector3(0, -0.075f, 0);
                    DestroyImmediate(disc.GetComponent<Collider>());

                    // Neon rim around turntable platform
                    GameObject rim = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    rim.name = "TurntableNeonRing";
                    rim.transform.SetParent(tt.transform, false);
                    rim.transform.localScale = new Vector3(5.7f, 0.05f, 5.7f);
                    rim.transform.localPosition = new Vector3(0, 0.01f, 0);
                    DestroyImmediate(rim.GetComponent<Collider>());
                }
                turntableTransform = tt.transform;
            }

            if (previewCarBuilder == null)
            {
                GameObject carObj = GameObject.Find("GaragePreviewCar");
                if (carObj == null)
                {
                    carObj = new GameObject("GaragePreviewCar");
                    carObj.transform.SetParent(turntableTransform, false);
                    carObj.transform.localPosition = new Vector3(0, 0.35f, 0);
                }

                previewCarBuilder = carObj.GetComponent<CarPrefabBuilder>();
                if (previewCarBuilder == null) previewCarBuilder = carObj.AddComponent<CarPrefabBuilder>();

                previewCustomizer = carObj.GetComponent<CarCustomizer>();
                if (previewCustomizer == null) previewCustomizer = carObj.AddComponent<CarCustomizer>();
            }
        }

        public void LoadEquippedLoadout()
        {
            EquippedLoadout loadout = SaveSystem.CurrentData.loadout;
            if (previewCarBuilder == null) return;

            // 1. Set Chassis
            if (loadout.chassisId == "viper_gt") previewCarBuilder.chassisType = VehicleChassisType.ViperGT;
            else if (loadout.chassisId == "specter_rs") previewCarBuilder.chassisType = VehicleChassisType.SpecterRS;
            else if (loadout.chassisId == "ion_phantom") previewCarBuilder.chassisType = VehicleChassisType.IonPhantom;
            else if (loadout.chassisId == "titan_juggernaut") previewCarBuilder.chassisType = VehicleChassisType.TitanJuggernaut;
            else previewCarBuilder.chassisType = VehicleChassisType.ApexVanguard;

            // 2. Set Wheels
            previewCarBuilder.wheelsId = !string.IsNullOrEmpty(loadout.wheelsId) ? loadout.wheelsId : "tuner_aero";

            // Rebuild physical mesh
            previewCarBuilder.BuildCar();

            // 3. Apply Colors, Boost, Trail
            if (previewCustomizer != null)
            {
                previewCustomizer.ApplyLoadout(loadout);
            }
        }

        // ==================== CUSTOMIZATION EQUIP METHODS ====================

        public void EquipChassis(string chassisId)
        {
            SaveSystem.CurrentData.loadout.chassisId = chassisId;
            SaveSystem.Save();
            LoadEquippedLoadout();
            PlayEquipFeedback("Equipped Body: " + chassisId);
        }

        public void EquipPrimaryPaint(string hexColor)
        {
            SaveSystem.CurrentData.loadout.primaryPaintColorHex = hexColor;
            SaveSystem.Save();
            if (previewCustomizer != null)
            {
                if (ColorUtility.TryParseHtmlString(hexColor, out Color col))
                {
                    previewCustomizer.primaryColor = col;
                    previewCustomizer.ApplyCustomization();
                }
            }
            PlayEquipFeedback("Equipped Primary Paint");
        }

        public void EquipSecondaryPaint(string hexColor)
        {
            SaveSystem.CurrentData.loadout.secondaryPaintColorHex = hexColor;
            SaveSystem.Save();
            if (previewCustomizer != null)
            {
                if (ColorUtility.TryParseHtmlString(hexColor, out Color col))
                {
                    previewCustomizer.secondaryColor = col;
                    previewCustomizer.ApplyCustomization();
                }
            }
            PlayEquipFeedback("Equipped Secondary Paint");
        }

        public void EquipWheels(string wheelsId)
        {
            SaveSystem.CurrentData.loadout.wheelsId = wheelsId;
            SaveSystem.Save();
            LoadEquippedLoadout();
            PlayEquipFeedback("Equipped Wheels: " + wheelsId);
        }

        public void EquipBoostEffect(string boostId)
        {
            SaveSystem.CurrentData.loadout.boostEffectId = boostId;
            SaveSystem.CurrentData.loadout.boostTrailId = boostId;
            SaveSystem.Save();

            CosmeticItem item = CosmeticDatabase.FindItem(boostId);
            if (item != null && previewCustomizer != null)
            {
                previewCustomizer.boostFlameColor = item.primaryColor;
                previewCustomizer.ApplyCustomization();
            }

            StartCoroutine(PreviewBoostFiring(item != null ? item.primaryColor : Color.cyan));
            PlayEquipFeedback("Equipped Boost: " + boostId);
        }

        public void EquipTrail(string trailId)
        {
            SaveSystem.CurrentData.loadout.trailId = trailId;
            SaveSystem.Save();

            CosmeticItem item = CosmeticDatabase.FindItem(trailId);
            StartCoroutine(PreviewTrailRibbon(item != null ? item.primaryColor : Color.white));
            PlayEquipFeedback("Equipped Trail: " + trailId);
        }

        public void EquipGoalExplosion(string explosionId)
        {
            SaveSystem.CurrentData.loadout.goalExplosionId = explosionId;
            SaveSystem.Save();

            CosmeticItem item = CosmeticDatabase.FindItem(explosionId);
            StartCoroutine(PreviewGoalExplosionEffect(item));
            PlayEquipFeedback("Equipped Goal Explosion: " + explosionId);
        }

        private IEnumerator PreviewBoostFiring(Color flameColor)
        {
            Light bLight = previewCarBuilder != null ? previewCarBuilder.transform.Find("VisualModel/ExhaustThrusters/BoostLight")?.GetComponent<Light>() : null;
            if (bLight != null)
            {
                bLight.color = flameColor;
                bLight.intensity = 3.5f;
            }

            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.PlaySFX(AudioManager.Instance.boostClip, 0.7f);
            }

            yield return new WaitForSeconds(1.2f);

            if (bLight != null)
            {
                bLight.intensity = 0f;
            }
        }

        private IEnumerator PreviewTrailRibbon(Color trailColor)
        {
            yield return new WaitForSeconds(0.8f);
        }

        private IEnumerator PreviewGoalExplosionEffect(CosmeticItem item)
        {
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.PlayGoalHorn();
            }

            yield return null;
        }

        private void PlayEquipFeedback(string status)
        {
            if (itemDetailsText != null) itemDetailsText.text = status;
            if (AudioManager.Instance != null) AudioManager.Instance.PlayUIClick();
            RefreshItemGrid();
        }

        // ==================== PROCEDURAL GARAGE UI BUILDER ====================

        public void SelectCategory(CosmeticCategory category)
        {
            _currentCategory = category;
            if (categoryTitleText != null)
            {
                categoryTitleText.text = category.ToString().ToUpper();
            }
            RefreshItemGrid();
        }

        public void BuildGarageUI()
        {
            if (garageCanvas == null) return;
            SelectCategory(CosmeticCategory.CarBody);
        }

        public void RefreshItemGrid()
        {
            if (itemGridContainer == null) return;

            // Clear previous cards
            foreach (var c in _spawnedCards)
            {
                if (c != null) Destroy(c);
            }
            _spawnedCards.Clear();

            List<CosmeticItem> items = CosmeticDatabase.GetItemsByCategory(_currentCategory);
            EquippedLoadout loadout = SaveSystem.CurrentData.loadout;

            Font uiFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf") ?? Resources.GetBuiltinResource<Font>("Arial.ttf");

            foreach (var item in items)
            {
                GameObject card = new GameObject("Card_" + item.id);
                card.transform.SetParent(itemGridContainer, false);
                _spawnedCards.Add(card);

                Image cardBg = card.AddComponent<Image>();
                bool isEquipped = CheckIsEquipped(item, loadout);
                cardBg.color = isEquipped ? new Color(0.1f, 0.35f, 0.65f, 0.9f) : new Color(0.12f, 0.14f, 0.18f, 0.85f);

                Button btn = card.AddComponent<Button>();
                string itemId = item.id;
                CosmeticItem copyItem = item;
                btn.onClick.AddListener(() => OnClickItemCard(copyItem));

                // Title
                GameObject titleObj = new GameObject("Title");
                titleObj.transform.SetParent(card.transform, false);
                Text t = titleObj.AddComponent<Text>();
                t.text = $"{item.iconEmoji} {item.displayName}" + (isEquipped ? " [EQUIPPED]" : "");
                t.font = uiFont;
                t.fontSize = 14;
                t.alignment = TextAnchor.MiddleCenter;
                t.color = CosmeticItem.GetRarityColor(item.rarity);
            }
        }

        private bool CheckIsEquipped(CosmeticItem item, EquippedLoadout loadout)
        {
            switch (item.category)
            {
                case CosmeticCategory.CarBody: return loadout.chassisId == item.id;
                case CosmeticCategory.PrimaryPaint: return loadout.primaryPaintColorHex == item.hexColor;
                case CosmeticCategory.SecondaryPaint: return loadout.secondaryPaintColorHex == item.hexColor;
                case CosmeticCategory.Wheels: return loadout.wheelsId == item.id;
                case CosmeticCategory.BoostEffect: return (loadout.boostEffectId == item.id || loadout.boostTrailId == item.id);
                case CosmeticCategory.Trail: return loadout.trailId == item.id;
                case CosmeticCategory.GoalExplosion: return loadout.goalExplosionId == item.id;
                default: return false;
            }
        }

        private void OnClickItemCard(CosmeticItem item)
        {
            switch (item.category)
            {
                case CosmeticCategory.CarBody: EquipChassis(item.id); break;
                case CosmeticCategory.PrimaryPaint: EquipPrimaryPaint(item.hexColor); break;
                case CosmeticCategory.SecondaryPaint: EquipSecondaryPaint(item.hexColor); break;
                case CosmeticCategory.Wheels: EquipWheels(item.id); break;
                case CosmeticCategory.BoostEffect: EquipBoostEffect(item.id); break;
                case CosmeticCategory.Trail: EquipTrail(item.id); break;
                case CosmeticCategory.GoalExplosion: EquipGoalExplosion(item.id); break;
            }
        }
    }
}
