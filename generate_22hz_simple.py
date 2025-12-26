#!/usr/bin/env python3
"""
Generate 22 Hz binaural beat using only built-in Python libraries
Creates a WAV file that can be converted to MP3
"""

import math
import struct
import wave

def generate_binaural_beat_wav(filename="22hz_binaural_15min.wav", duration_minutes=15):
    """Generate 22 Hz binaural beat WAV file using only built-in libraries"""
    
    # Parameters
    sample_rate = 44100
    duration = duration_minutes * 60
    left_freq = 300.0  # Hz
    right_freq = 322.0  # Hz (22 Hz difference)
    
    print(f"Generating {duration_minutes}-minute 22 Hz binaural beat...")
    print(f"Left: {left_freq} Hz, Right: {right_freq} Hz")
    print(f"Binaural difference: {right_freq - left_freq} Hz")
    
    # Create WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate samples
        total_samples = int(sample_rate * duration)
        chunk_size = 1000  # Process in chunks to manage memory
        
        for chunk_start in range(0, total_samples, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_samples)
            chunk_samples = chunk_end - chunk_start
            
            # Generate audio data for this chunk
            audio_data = []
            
            for i in range(chunk_samples):
                t = (chunk_start + i) / sample_rate
                
                # Left and right channels
                left_val = math.sin(2 * math.pi * left_freq * t) * 0.5
                right_val = math.sin(2 * math.pi * right_freq * t) * 0.5
                
                # Convert to 16-bit integers
                left_int = int(left_val * 32767)
                right_int = int(right_val * 32767)
                
                # Pack as stereo 16-bit samples
                audio_data.append(struct.pack('<hh', left_int, right_int))
            
            # Write chunk to file
            wav_file.writeframes(b''.join(audio_data))
            
            # Progress indicator
            progress = (chunk_end / total_samples) * 100
            print(f"\rProgress: {progress:.1f}%", end="", flush=True)
    
    print(f"\nSaved: {filename}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Bit depth: 16-bit")
    print(f"Channels: Stereo")
    
    return filename

if __name__ == "__main__":
    # Generate the 15-minute 22 Hz tone
    output_file = generate_binaural_beat_wav("22hz_binaural_15min.wav", 15)
    
    print("\nTo convert to MP3 (if you have ffmpeg):")
    print(f"ffmpeg -i {output_file} 22hz_binaural_15min.mp3")
    print("\nOr use any online WAV to MP3 converter")
