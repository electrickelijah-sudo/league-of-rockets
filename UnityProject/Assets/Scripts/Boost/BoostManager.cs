using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Coordinates all arena boost pickups, handles instant reset on kickoff,
    /// and generates standard tournament pad positions if none are pre-placed.
    /// </summary>
    public class BoostManager : MonoBehaviour
    {
        public static BoostManager Instance { get; private set; }

        [Header("=== BOOST PADS ===")]
        public List<BoostPad> allPads = new List<BoostPad>();

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);

            FindAllPadsInScene();
        }

        public void FindAllPadsInScene()
        {
            allPads.Clear();
            allPads.AddRange(FindObjectsByType<BoostPad>(FindObjectsSortMode.None));
        }

        public void RefreshPadList()
        {
            FindAllPadsInScene();
        }

        public void ResetAllPads()
        {
            foreach (var pad in allPads)
            {
                if (pad != null) pad.ResetPad();
            }
        }
    }
}
