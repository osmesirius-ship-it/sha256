#!/usr/bin/env python3
"""
Generate 22 Hz binaural beat MP3 (15 minutes)
Uses 300 Hz left, 322 Hz right for optimal 22 Hz difference
"""

import numpy as np
import soundfile as sf
import os

def generate_binaural_beat(duration_minutes=15, sample_rate=44100):
    """Generate 22 Hz binaural beat MP3"""
    
    # Parameters
    duration = duration_minutes * 60  # Convert to seconds
    left_freq = 300.0  # Hz
    right_freq = 322.0  # Hz (22 Hz difference)
    
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate stereo binaural beats
    left_channel = np.sin(2 * np.pi * left_freq * t)
    right_channel = np.sin(2 * np.pi * right_freq * t)
    
    # Combine into stereo array
    stereo = np.column_stack((left_channel, right_channel))
    
    # Normalize to prevent clipping
    stereo = stereo * 0.5
    
    return stereo, sample_rate

def save_tone(filename="22hz_binaural_15min.wav", duration_minutes=15):
    """Save the binaural beat as WAV file"""
    
    print(f"Generating {duration_minutes}-minute 22 Hz binaural beat...")
    
    # Generate the tone
    audio, sample_rate = generate_binaural_beat(duration_minutes)
    
    # Save as WAV (can be converted to MP3 later)
    sf.write(filename, audio, sample_rate)
    
    print(f"Saved: {filename}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Frequencies: 300 Hz (L) / 322 Hz (R) = 22 Hz binaural beat")
    
    return filename

if __name__ == "__main__":
    # Generate the 15-minute 22 Hz tone
    output_file = save_tone("22hz_binaural_15min.wav", 15)
    
    # Instructions for MP3 conversion
    print("\nTo convert to MP3, use:")
    print(f"ffmpeg -i {output_file} 22hz_binaural_15min.mp3")
    print("\nOr install pydub and modify script to save directly as MP3")
