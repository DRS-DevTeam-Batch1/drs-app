def detect_bat_contact_frame(video_path, timestamp, buffer_time=0.5):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  
    target_frame = int((timestamp - buffer_time) * fps)  
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(target_frame, 0))  # Set frame

    print(f"Checking frames around timestamp {timestamp}s (target frame: {target_frame})")

    ret, prev = cap.read()
    if not ret:
        print("Error: Failed to read first frame")
        return False
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)  
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)  #reduce noise

    for i in range(30): 
        ret, curr = cap.read()
        if not ret:
            print("Error: Failed to read frame")
            break
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.GaussianBlur(curr_gray, (21, 21), 0)
        diff = cv2.absdiff(prev_gray, curr_gray)
        _, diff = cv2.threshold(diff, 2, 255, cv2.THRESH_BINARY) 
        motion = np.count_nonzero(diff)
        print(f"🔍 Frame {i+1} motion: {motion}")  #show motion detecction
        diff_image_path = f"frame_{i+1}_diff.png"
        cv2.imwrite(diff_image_path, diff)
        if motion > 1000:  # Threshold
            print("Motion detected near bat")
            motion_image_path = f"frame_{i+1}_motion.png"
            cv2.imwrite(motion_image_path, diff)  #save image
            cap.release()
            os.remove(diff_image_path)
            os.remove(motion_image_path)
            return True
        os.remove(diff_image_path)

        prev_gray = curr_gray

    cap.release()  #close file
    return False