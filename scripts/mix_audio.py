import subprocess
import os

FFMPEG_PATH = r"D:\HyperFrames_Demo\bin\ffmpeg.exe"

# Define the exact start timestamps for each speech segment in milliseconds
# seg1: 0.5s
# seg2: 14.2s
# seg3: 26.0s
# seg4: 38.5s
# seg5: 50.5s
# seg6: 62.0s
# seg7: 71.3s
TIMESTAMPS = [
    ("recordings/audio/seg1.mp3", 500),
    ("recordings/audio/seg2.mp3", 14200),
    ("recordings/audio/seg3.mp3", 26000),
    ("recordings/audio/seg4.mp3", 38500),
    ("recordings/audio/seg5.mp3", 50500),
    ("recordings/audio/seg6.mp3", 62000),
    ("recordings/audio/seg7.mp3", 71300),
]

def mix():
    print("🎵 Mixing narration voiceover with background music...")
    
    # Build ffmpeg input arguments
    inputs = []
    filter_complex = []
    
    # 7 voiceover inputs
    for idx, (fpath, delay_ms) in enumerate(TIMESTAMPS):
        inputs.extend(["-i", fpath])
        filter_complex.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[v{idx}];")
    
    # Merge all voice streams
    voice_inputs = "".join([f"[v{i}]" for i in range(len(TIMESTAMPS))])
    filter_complex.append(f"{voice_inputs}amix=inputs={len(TIMESTAMPS)}:dropout_transition=0:normalize=0[voice];")
    
    # Add background music as 8th input
    inputs.extend(["-i", "recordings/audio/bg_music.wav"])
    bg_idx = len(TIMESTAMPS)
    # Filter bg music: soft volume, fade out at end
    filter_complex.append(f"[{bg_idx}:a]volume=0.35,afade=t=out:st=81:d=3[bg];")
    
    # Mix voice (priority/clear) with background music
    filter_complex.append("[voice]volume=1.4[voice_loud];[voice_loud][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]")
    
    full_filter = "".join(filter_complex)
    output_audio = "recordings/audio/full_voiceover_master.mp3"
    
    cmd = [
        FFMPEG_PATH, "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[aout]",
        "-t", "84",
        "-b:a", "192k",
        output_audio
    ]
    
    print("Running FFmpeg audio mix...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError("Audio mix failed")
    
    print(f"✅ Master audio created: {output_audio}")

if __name__ == "__main__":
    mix()
