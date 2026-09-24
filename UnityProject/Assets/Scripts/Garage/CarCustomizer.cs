using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Modular vehicle customizer for Rocket League cars in Unity.
    /// Controls PBR automotive paint (primary/secondary colors, metallic, clearcoat),
    /// window tints, rim finishes, underglow neon, and boost flame particle colors.
    /// </summary>
    public class CarCustomizer : MonoBehaviour
    {
        [System.Serializable]
        public struct CustomizationPreset
        {
            public string presetName;
            public Color primaryColor;
            public Color secondaryColor;
            public Color windowTint;
            public Color rimColor;
            public Color underglowColor;
            public Color boostFlameColor;
            [Range(0f, 1f)] public float metallic;
            [Range(0f, 1f)] public float smoothness;
        }

        [Header("=== RENDERERS ===")]
        public MeshRenderer bodyRenderer;
        public MeshRenderer windowRenderer;
        public List<MeshRenderer> wheelRimRenderers = new List<MeshRenderer>();
        public Light underglowLight;
        public ParticleSystem boostParticles;

        [Header("=== ACTIVE CUSTOMIZATION ===")]
        public Color primaryColor = new Color(0.08f, 0.42f, 0.95f); // Classic Blue
        public Color secondaryColor = Color.white;
        public Color windowTint = new Color(0.05f, 0.08f, 0.12f, 0.85f);
        public Color rimColor = new Color(0.85f, 0.85f, 0.9f);
        public Color underglowColor = new Color(0f, 0.6f, 1f);
        public Color boostFlameColor = new Color(1f, 0.5f, 0.05f);

        [Range(0f, 1f)] public float metallic = 0.75f;
        [Range(0f, 1f)] public float smoothness = 0.88f;

        [Header("=== PRESETS ===")]
        public List<CustomizationPreset> presets = new List<CustomizationPreset>()
        {
            new CustomizationPreset {
                presetName = "Blue Striker",
                primaryColor = new Color(0.05f, 0.4f, 0.95f),
                secondaryColor = Color.white,
                windowTint = new Color(0.05f, 0.08f, 0.15f),
                rimColor = Color.white,
                underglowColor = new Color(0.1f, 0.6f, 1f),
                boostFlameColor = new Color(0f, 0.8f, 1f),
                metallic = 0.7f,
                smoothness = 0.85f
            },
            new CustomizationPreset {
                presetName = "Orange Velocity",
                primaryColor = new Color(0.95f, 0.35f, 0.05f),
                secondaryColor = new Color(1f, 0.85f, 0.1f),
                windowTint = new Color(0.1f, 0.05f, 0.02f),
                rimColor = new Color(0.9f, 0.7f, 0.2f),
                underglowColor = new Color(1f, 0.4f, 0f),
                boostFlameColor = new Color(1f, 0.45f, 0.05f),
                metallic = 0.8f,
                smoothness = 0.9f
            },
            new CustomizationPreset {
                presetName = "Cyber Neon",
                primaryColor = new Color(0.75f, 0.05f, 0.95f),
                secondaryColor = new Color(0.05f, 0.95f, 0.8f),
                windowTint = new Color(0.08f, 0.02f, 0.12f),
                rimColor = new Color(0.05f, 0.95f, 0.8f),
                underglowColor = new Color(0.9f, 0.1f, 1f),
                boostFlameColor = new Color(0.95f, 0.1f, 0.8f),
                metallic = 0.9f,
                smoothness = 0.95f
            }
        };

        private void Start()
        {
            ApplyCustomization();
        }

        [ContextMenu("Apply Customization")]
        public void ApplyCustomization()
        {
            MeshRenderer[] allRenderers = GetComponentsInChildren<MeshRenderer>();
            foreach (var mr in allRenderers)
            {
                if (mr == null || mr.material == null) continue;
                string n = mr.gameObject.name.ToLower();

                if (n.Contains("splitter") || n.Contains("spoiler") || n.Contains("sideskirt") || 
                    n.Contains("beadlock") || n.Contains("aeroblade") || n.Contains("tailfin") || 
                    n.Contains("rollbar") || n.Contains("canard") || n.Contains("diffuser") || 
                    n.Contains("bullbar") || n.Contains("wing") || n.Contains("scoop"))
                {
                    mr.material.color = secondaryColor;
                    if (mr.material.HasProperty("_Color")) mr.material.SetColor("_Color", secondaryColor);
                }
                else if (n.Contains("body") || n.Contains("chassis") || n.Contains("hood") || n.Contains("nose"))
                {
                    mr.material.color = primaryColor;
                    if (mr.material.HasProperty("_Color")) mr.material.SetColor("_Color", primaryColor);
                    if (mr.material.HasProperty("_Metallic")) mr.material.SetFloat("_Metallic", metallic);
                    if (mr.material.HasProperty("_Glossiness")) mr.material.SetFloat("_Glossiness", smoothness);
                }
                else if (n.Contains("rim"))
                {
                    mr.material.color = rimColor;
                }
                else if (n.Contains("window") || n.Contains("canopy") || n.Contains("bubble"))
                {
                    mr.material.color = windowTint;
                }
            }

            if (underglowLight != null) underglowLight.color = underglowColor;

            if (boostParticles != null)
            {
                var main = boostParticles.main;
                main.startColor = new ParticleSystem.MinMaxGradient(boostFlameColor);
            }

            Light bLight = transform.Find("VisualModel/ExhaustThrusters/BoostLight")?.GetComponent<Light>();
            if (bLight != null) bLight.color = boostFlameColor;
        }

        public void ApplyLoadout(EquippedLoadout loadout)
        {
            if (loadout == null) return;

            if (ColorUtility.TryParseHtmlString(loadout.primaryPaintColorHex, out Color pCol))
                primaryColor = pCol;
            if (ColorUtility.TryParseHtmlString(loadout.secondaryPaintColorHex, out Color sCol))
                secondaryColor = sCol;

            string bId = !string.IsNullOrEmpty(loadout.boostEffectId) ? loadout.boostEffectId : loadout.boostTrailId;
            CosmeticItem boostItem = CosmeticDatabase.FindItem(bId);
            if (boostItem != null)
            {
                boostFlameColor = boostItem.primaryColor;
            }

            CosmeticItem trailItem = CosmeticDatabase.FindItem(loadout.trailId);
            if (trailItem != null)
            {
                CarController car = GetComponent<CarController>();
                if (car != null && car.supersonicTrails != null)
                {
                    foreach (var tr in car.supersonicTrails)
                    {
                        if (tr != null)
                        {
                            tr.startColor = trailItem.primaryColor;
                            tr.endColor = new Color(trailItem.primaryColor.r, trailItem.primaryColor.g, trailItem.primaryColor.b, 0f);
                        }
                    }
                }
            }

            ApplyCustomization();
        }

        public void ApplyPreset(int index)
        {
            if (index < 0 || index >= presets.Count) return;

            var p = presets[index];
            primaryColor = p.primaryColor;
            secondaryColor = p.secondaryColor;
            windowTint = p.windowTint;
            rimColor = p.rimColor;
            underglowColor = p.underglowColor;
            boostFlameColor = p.boostFlameColor;
            metallic = p.metallic;
            smoothness = p.smoothness;

            ApplyCustomization();
        }
    }
}
