import cv2
import numpy as np
import random

def overlay_decision(frame, decision="OUT", confidence=87):
    """
    Draws a semi-transparent box with decision and confidence text on the video frame.
    """

    # Parameters
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 2
    color_out = (0, 0, 255)       # Red for OUT
    color_not_out = (0, 255, 0)   # Green for NOT OUT
    color = color_out if decision.upper() == "OUT" else color_not_out

    # Draw background box
    overlay = frame.copy()
    box_start = (50, 50)
    box_end = (600, 160)
    cv2.rectangle(overlay, box_start, box_end, (0, 0, 0), -1)  # black background box
    alpha = 0.6
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Put texts
    cv2.putText(frame, f"Decision: {decision}", (60, 100), font, font_scale, color, thickness, cv2.LINE_AA)
    cv2.putText(frame, f"Confidence: {confidence}%", (60, 145), font, font_scale * 0.9, color, thickness, cv2.LINE_AA)

    return frame

def get_random_decision():
    """
    Simulates a prediction from a model (stub).
    """
    decision = random.choice(["OUT", "NOT OUT"])
    confidence = random.randint(70, 99)
    return decision, confidence

def main():
    # Load video or webcam
    cap = cv2.VideoCapture(0)  # Use "your_video.mp4" instead of 0 for video file

    if not cap.isOpened():
        print("Error: Video source not found.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize for demo
        frame = cv2.resize(frame, (1280, 720))

        # Get mock decision
        decision, confidence = get_random_decision()

        # Overlay decision
        frame = overlay_decision(frame, decision, confidence)

        # Show frame
        cv2.imshow("DRS Decision System", frame)

        # Exit on 'q'
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
