def analyze_bat_edge(video_path, audio_path):
    print("\nanalyzing audio")
    spike_time = detect_audio_spike(audio_path)  #detect audio spike
    if spike_time is not None:
        print("checking video around that timestamp")
        if detect_bat_contact_frame(video_path, spike_time): 
            print("\nbat edge detected")
        else:
            print("\nno visuall confirmation")
    else:
        print("\n nooo spike detected in audio")  

if __name__ == "__main__":
    generateSampInput() 
    analyze_bat_edge("sample_ball_video.mp4", "sample_audio.wav")