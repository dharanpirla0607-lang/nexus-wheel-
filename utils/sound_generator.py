"""
Procedural Sci-Fi Sound Generator for Nexus Wheel.
Generates retro-futuristic, crisp sound effects using standard python (wave, struct, math).
Zero external binary assets required.
"""

import os
import math
import struct
import wave

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")

def generate_wave(filename: str, sample_rate: int, duration: float, generator_func):
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    filepath = os.path.join(SOUNDS_DIR, filename)
    num_samples = int(sample_rate * duration)
    
    with wave.open(filepath, "w") as wav_file:
        # 1 channel (mono), 2 bytes per sample (16-bit), sample_rate, num_samples
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = float(i) / num_samples
            sample = generator_func(t, progress, duration)
            # clamp to -1.0 to 1.0
            sample = max(-1.0, min(1.0, sample))
            int_val = int(sample * 32767.0)
            frames.extend(struct.pack("<h", int_val))
            
        wav_file.writeframes(frames)
    return filepath

def create_wheel_open_sound():
    def synth(t, p, d):
        # Rising sci-fi whoosh + resonant harmonic sweep
        freq = 180.0 + (520.0 * (p ** 1.8))
        env = math.sin(math.pi * p) ** 0.8
        sub = math.sin(2 * math.pi * (freq * 0.5) * t) * 0.4
        main = math.sin(2 * math.pi * freq * t) * 0.6
        harm = math.sin(2 * math.pi * (freq * 2.0) * t) * 0.15
        return (sub + main + harm) * env * 0.6
    return generate_wave("wheel_open.wav", 44100, 0.16, synth)

def create_wheel_close_sound():
    def synth(t, p, d):
        # Falling soft sweep
        freq = 460.0 * (1.0 - (p ** 1.2)) + 90.0
        env = math.sin(math.pi * p) ** 1.2
        tone = math.sin(2 * math.pi * freq * t) * 0.6
        return tone * env * 0.5
    return generate_wave("wheel_close.wav", 44100, 0.12, synth)

def create_segment_select_sound():
    def synth(t, p, d):
        # High-tech subtle mechanical tick / blip
        freq = 1400.0 - (600.0 * p)
        decay = math.exp(-28.0 * p)
        click = math.sin(2 * math.pi * freq * t) * decay
        pop = math.sin(2 * math.pi * 2200.0 * t) * (math.exp(-60.0 * p)) * 0.5
        return (click + pop) * 0.45
    return generate_wave("segment_select.wav", 44100, 0.045, synth)

def create_action_execute_sound():
    def synth(t, p, d):
        # Dual-frequency confirmation chime (Cyberpunk / GTA style)
        f1 = 880.0 # A5
        f2 = 1320.0 # E6
        f3 = 1760.0 # A6
        decay = math.exp(-7.5 * p)
        t1 = math.sin(2 * math.pi * f1 * t) * 0.4
        t2 = math.sin(2 * math.pi * f2 * t) * 0.4
        t3 = math.sin(2 * math.pi * f3 * t) * 0.25
        return (t1 + t2 + t3) * decay * 0.6
    return generate_wave("action_execute.wav", 44100, 0.28, synth)

def create_error_sound():
    def synth(t, p, d):
        # Damped warning buzz
        f = 160.0
        mod = 1.0 if int(t * 40) % 2 == 0 else -1.0
        decay = math.exp(-6.0 * p)
        return (math.sin(2 * math.pi * f * t) * 0.5 + mod * 0.2) * decay * 0.6
    return generate_wave("error.wav", 44100, 0.22, synth)

def generate_all_sounds():
    create_wheel_open_sound()
    create_wheel_close_sound()
    create_segment_select_sound()
    create_action_execute_sound()
    create_error_sound()
    return True

if __name__ == "__main__":
    generate_all_sounds()
    print("All audio assets successfully synthesized.")
