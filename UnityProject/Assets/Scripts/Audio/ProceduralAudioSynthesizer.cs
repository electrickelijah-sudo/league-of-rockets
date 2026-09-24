using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Mathematically synthesizes authentic, high-fidelity procedural AudioClips at runtime
    /// with zero external asset dependencies: engine rumble, boost roar, impact thumps,
    /// stadium horns, referee whistles, countdown beeps, and UI clicks.
    /// </summary>
    public static class ProceduralAudioSynthesizer
    {
        public static AudioClip CreateEngineClip(string name = "Proc_Engine", float duration = 1.0f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                // Complex harmonic engine rumble (80Hz fundamental + 160Hz + 240Hz + subtle noise)
                float s1 = Mathf.Sin(2f * Mathf.PI * 80f * t);
                float s2 = Mathf.Sin(2f * Mathf.PI * 160f * t) * 0.5f;
                float s3 = Mathf.Sin(2f * Mathf.PI * 240f * t) * 0.25f;
                float noise = (Random.value * 2f - 1f) * 0.12f;
                samples[i] = (s1 + s2 + s3 + noise) * 0.4f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateBoostClip(string name = "Proc_Boost", float duration = 1.5f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            float lastNoise = 0f;
            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                // Filtered brown/pink noise simulation for roaring jet flame
                float white = Random.value * 2f - 1f;
                lastNoise = (lastNoise + (0.04f * white)) / 1.04f;
                float lowSine = Mathf.Sin(2f * Mathf.PI * 95f * t) * 0.35f;
                samples[i] = (lastNoise * 2.8f + lowSine) * 0.5f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateJumpClip(string name = "Proc_Jump", float duration = 0.35f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = 1f - (t / duration);
                float freq = Mathf.Lerp(180f, 620f, t / duration);
                samples[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * env * 0.65f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateDodgeClip(string name = "Proc_Dodge", float duration = 0.45f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Sin((t / duration) * Mathf.PI);
                float freq = Mathf.Lerp(340f, 120f, t / duration);
                float noise = (Random.value * 2f - 1f) * 0.2f;
                samples[i] = (Mathf.Sin(2f * Mathf.PI * freq * t) + noise) * env * 0.7f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateBallImpactClip(string name = "Proc_Impact", float duration = 0.38f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Exp(-14f * t);
                float sub = Mathf.Sin(2f * Mathf.PI * 70f * t) * 0.8f;
                float crack = (Random.value * 2f - 1f) * Mathf.Exp(-40f * t) * 0.6f;
                samples[i] = (sub + crack) * env;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateGoalHornClip(string name = "Proc_GoalHorn", float duration = 3.0f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Clamp01(t * 10f) * Mathf.Clamp01((duration - t) * 3f);
                float horn1 = Mathf.Sin(2f * Mathf.PI * 164.81f * t); // E3
                float horn2 = Mathf.Sin(2f * Mathf.PI * 220.00f * t) * 0.85f; // A3
                float horn3 = Mathf.Sin(2f * Mathf.PI * 329.63f * t) * 0.5f; // E4
                samples[i] = (horn1 + horn2 + horn3) * env * 0.4f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateCountdownBeepClip(bool isGoWhistle, string name = "Proc_Beep", float duration = 0.22f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];
            float freq = isGoWhistle ? 1760f : 880f;

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = 1f - (t / duration);
                samples[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * env * 0.5f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateUIClickClip(string name = "Proc_UIClick", float duration = 0.08f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Exp(-45f * t);
                samples[i] = Mathf.Sin(2f * Mathf.PI * 1200f * t) * env * 0.5f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateWhistleClip(string name = "Proc_Whistle", float duration = 0.6f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Sin((t / duration) * Mathf.PI);
                float trill = 1f + 0.08f * Mathf.Sin(2f * Mathf.PI * 28f * t);
                samples[i] = Mathf.Sin(2f * Mathf.PI * 2400f * trill * t) * env * 0.45f;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        public static AudioClip CreateBuzzerClip(string name = "Proc_Buzzer", float duration = 1.2f, int sampleRate = 44100)
        {
            int totalSamples = Mathf.FloorToInt(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Clamp01(t * 20f) * Mathf.Clamp01((duration - t) * 10f);
                float buzz = Mathf.Sign(Mathf.Sin(2f * Mathf.PI * 180f * t)) * 0.4f;
                samples[i] = buzz * env;
            }

            AudioClip clip = AudioClip.Create(name, totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
