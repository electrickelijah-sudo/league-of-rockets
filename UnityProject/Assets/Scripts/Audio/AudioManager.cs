using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Coordinates audio channels (Master, Music, SFX, Crowd), handles sound clips,
    /// dynamic engine RPM pitching, and procedural sound generation.
    /// </summary>
    public class AudioManager : MonoBehaviour
    {
        public static AudioManager Instance { get; private set; }

        [Header("=== AUDIO SOURCES ===")]
        public AudioSource musicSource;
        public AudioSource sfxSource;
        public AudioSource crowdSource;
        public AudioSource announcerSource;

        [Header("=== PROCEDURAL CLIPS ===")]
        public AudioClip engineClip;
        public AudioClip boostClip;
        public AudioClip jumpClip;
        public AudioClip dodgeClip;
        public AudioClip impactClip;
        public AudioClip goalHornClip;
        public AudioClip countdownBeepClip;
        public AudioClip goBeepClip;
        public AudioClip uiClickClip;

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else if (Instance != this) Destroy(gameObject);

            InitializeAudioClips();
        }

        public void InitializeAudioClips()
        {
            if (engineClip == null) engineClip = ProceduralAudioSynthesizer.CreateEngineClip();
            if (boostClip == null) boostClip = ProceduralAudioSynthesizer.CreateBoostClip();
            if (jumpClip == null) jumpClip = ProceduralAudioSynthesizer.CreateJumpClip();
            if (dodgeClip == null) dodgeClip = ProceduralAudioSynthesizer.CreateDodgeClip();
            if (impactClip == null) impactClip = ProceduralAudioSynthesizer.CreateBallImpactClip();
            if (goalHornClip == null) goalHornClip = ProceduralAudioSynthesizer.CreateGoalHornClip();
            if (countdownBeepClip == null) countdownBeepClip = ProceduralAudioSynthesizer.CreateCountdownBeepClip(false);
            if (goBeepClip == null) goBeepClip = ProceduralAudioSynthesizer.CreateCountdownBeepClip(true);
            if (uiClickClip == null) uiClickClip = ProceduralAudioSynthesizer.CreateUIClickClip();
        }

        public void PlaySFX(AudioClip clip, float volume = 1f)
        {
            if (sfxSource != null && clip != null)
            {
                sfxSource.PlayOneShot(clip, volume * SaveSystem.CurrentData.settings.sfxVolume);
            }
        }

        public void PlayGoalHorn()
        {
            PlaySFX(goalHornClip, 1.0f);
        }

        public void PlayCountdownBeep(bool isGo)
        {
            PlaySFX(isGo ? goBeepClip : countdownBeepClip, 0.85f);
        }

        public void PlayUIClick()
        {
            PlaySFX(uiClickClip, 0.6f);
        }
    }
}
