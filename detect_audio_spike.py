import cv2
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import find_peaks
import os


def generateSampInput(video_path="sample_ball_video.mp4", audio_path="sample_audio.wav"):
    print("🎬 Generating test vid & audio")

    # sample audio with spike at 1 sec
    sr = 22050 
    duration = 2  
    y = np.zeros(int(sr * duration))  #silence at start
    spike_start = int(sr * 1)  
    y[spike_start:spike_start + 500] = 1.0  
    sf.write(audio_path, y, sr)  #save
    print(f"Sample audio: {audio_path}")

    fps = 30  
    width, height = 640, 480  #dimensions
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))  #]output

    for i in range(int(duration * fps)):
        frame = np.zeros((height, width, 3), dtype=np.uint8)  
        if 28 <= i <= 32:  
            cv2.circle(frame, (320, 240), 20, (255, 255, 255), -1)  #white ball in center
        out.write(frame) 

    out.release()  #release video
    print(f"Sample video saved: {video_path}")

def detect_audio_spike(audio_path, threshold=0.02):
    y, sr = librosa.load(audio_path)
    energy = librosa.feature.rms(y=y)[0]  # Root mean square
    times = librosa.times_like(energy, sr=sr)  

    print("Energy values (first 10):", energy[:10])  
    peaks, _ = find_peaks(energy, height=threshold)
    if peaks.size > 0:
        print(f"⚡ Audio spike detected at {times[peaks[0]]:.2f} seconds (energy={energy[peaks[0]]:.3f})")
        return times[peaks[0]]  #return spike time
    print("No spike found")
    return None 