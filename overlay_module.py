import cv2
import numpy as np
import json
import os
from datetime import datetime


class CricketDRSOverlay:
    def __init__(self, video_path, trajectory_data, output_path=None):
        """
        Initialize the Cricket DRS Overlay system with enhanced features
        """
        self.video_path = video_path
        self.trajectory_data = trajectory_data
        self.output_path = output_path or f"drs_overlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Extract data
        self.decision = trajectory_data.get("label", "UNKNOWN").upper()
        self.confidence = trajectory_data.get("confidence", 0.0)
        self.reviewing_team = trajectory_data.get("reviewing_team", "TEAM").upper()
        self.predicted_trajectory = trajectory_data.get("predicted_trajectory", [])
        self.impact_point = trajectory_data.get("impact_point", {})
        self.bat_coordinates = trajectory_data.get("bat_coordinates", [])
        self.stump_coordinates = trajectory_data.get("stump_coordinates", [])
        self.player_positions = trajectory_data.get("player_positions", [])

        # Decision elements
        self.decision_elements = trajectory_data.get("decision_elements", {
            "wickets": "HITTING",
            "impact": "IN-LINE",
            "pitching": "OUTSIDE OFF"
        })

        # Colors (BGR format)
        self.COLORS = {
            "trajectory": (0, 255, 0),  # Green
            "trajectory_dot": (0, 255, 255),  # Yellow
            "impact": (0, 0, 255),  # Red
            "stumps": (255, 255, 255),  # White
            "bat": (255, 165, 0),  # Blue
            "batsman": (0, 0, 255),  # Red for batsman
            "bowler": (0, 255, 0),  # Green for bowler
            "fielder": (0, 255, 0),  # Green for fielders
            "out": (0, 165, 255),  # Orange
            "not_out": (0, 255, 0),  # Green
            "text": (255, 255, 255),  # White
            "decision_box": (0, 0, 255),  # Red for OUT
            "decision_box_not_out": (0, 255, 0),  # Green for NOT OUT
            "info_box": (255, 255, 255),  # White
            "info_text": (255, 255, 255),  # White
            "info_label": (200, 200, 200),  # Light gray
            "confidence_bar": (100, 100, 255),  # Blue
        }

        # Video properties
        self.cap = cv2.VideoCapture(self.video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.original_fps = self.fps
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Slow down the video (but not the trajectory)
        self.slow_down_factor = 2  # Play at half speed
        self.fps = self.fps / self.slow_down_factor

        # Pitch dimensions
        self.PITCH_LENGTH_M = 20.12
        self.PITCH_WIDTH_M = 3.05
        self.scale_x = self.width / self.PITCH_LENGTH_M
        self.scale_y = self.height / self.PITCH_WIDTH_M

        # Output video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.output_path, self.fourcc, self.fps, (self.width, self.height))

        # Convert trajectory to pixel coordinates
        self.trajectory_pixels = self._convert_trajectory_to_pixels()

    def _convert_trajectory_to_pixels(self):
        """Convert trajectory points to pixel coordinates"""
        pixel_trajectory = []
        if not self.predicted_trajectory:
            return pixel_trajectory

        # Calculate time range
        timestamps = [p.get("t", 0) for p in self.predicted_trajectory]
        start_time, end_time = min(timestamps), max(timestamps)
        total_time = max(0.1, end_time - start_time)

        for point in self.predicted_trajectory:
            # Calculate frame index (without slow down for trajectory)
            time_frac = (point.get("t", 0) - start_time) / total_time
            frame_idx = int(self.frame_count * 0.2 + time_frac * self.frame_count * 0.6)
            frame_idx = max(0, min(self.frame_count - 1, frame_idx))

            # Convert coordinates
            x_px = int(point.get("x", 0) * self.scale_x)
            y_px = int(self.height - (point.get("y", 0) * self.scale_y))
            radius = max(3, min(12, int(3 + point.get("z", 0) * 10)))

            pixel_trajectory.append((frame_idx, x_px, y_px, radius))

        return sorted(pixel_trajectory, key=lambda x: x[0])

    def _draw_players(self, frame):
        """Draw players with uniform colors"""
        for player in self.player_positions:
            x_px = int(player.get("x", 0) * self.scale_x)
            y_px = int(self.height - (player.get("y", 0) * self.scale_y))
            player_type = player.get("type", "fielder").lower()

            color = self.COLORS["fielder"]  # Default to fielder color
            if player_type == "batsman":
                color = self.COLORS["batsman"]
            elif player_type == "bowler":
                color = self.COLORS["bowler"]

            # Draw player (simple circle for demonstration)
            cv2.circle(frame, (x_px, y_px), 15, color, -1)

    def _draw_trajectory_on_frame(self, frame, frame_idx):
        """Draw trajectory and players on frame"""
        overlay = frame.copy()

        # Draw players first (so trajectory appears on top)
        self._draw_players(overlay)

        # Draw trajectory
        prev_point = None
        for pos_frame, x, y, r in self.trajectory_pixels:
            if pos_frame > frame_idx:
                continue

            # Draw trajectory line
            if prev_point:
                cv2.line(overlay, prev_point[:2], (x, y), self.COLORS["trajectory"], 2)

            # Draw ball
            cv2.circle(overlay, (x, y), r, self.COLORS["impact"], 2)
            cv2.circle(overlay, (x, y), 2, self.COLORS["trajectory_dot"], -1)
            prev_point = (x, y, r)

        # Draw bat and stumps
        for coord in self.bat_coordinates:
            x_px = int(coord.get("x", 0) * self.scale_x)
            y_px = int(self.height - (coord.get("y", 0) * self.scale_y))
            cv2.rectangle(overlay, (x_px - 5, y_px - 5), (x_px + 5, y_px + 5), self.COLORS["bat"], -1)

        for coord in self.stump_coordinates:
            x_px = int(coord.get("x", 0) * self.scale_x)
            y_px = int(self.height - (coord.get("y", 0) * self.scale_y))
            cv2.circle(overlay, (x_px, y_px), 3, self.COLORS["stumps"], -1)

        return overlay

    def _add_decision_graphics(self, frame, frame_idx):
        """Add decision overlay graphics"""
        if frame_idx <= self.frame_count // 4:
            return frame

        margin = 20
        box_color = self.COLORS["decision_box"] if self.decision == "OUT" else self.COLORS["decision_box_not_out"]

        # Main decision box
        cv2.rectangle(frame, (margin, margin), (margin + 300, margin + 150), box_color, 2)
        cv2.putText(frame, "ORIGINAL DECISION", (margin + 10, margin + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS["text"], 2)
        cv2.putText(frame, self.decision, (margin + 10, margin + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, box_color, 3)

        # Confidence meter
        self._draw_confidence_bar(frame, margin + 10, margin + 90, 150, 15, self.confidence)
        cv2.putText(frame, "CONFIDENCE", (margin + 10, margin + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS["info_label"], 1)

        # Information boxes
        self._draw_info_box(frame, self.width - 300, margin, "WICKETS", self.decision_elements.get("wickets", "N/A"))
        self._draw_info_box(frame, self.width - 300, margin + 60, "IMPACT", self.decision_elements.get("impact", "N/A"))
        self._draw_info_box(frame, self.width - 300, margin + 120, "PITCHING",
                            self.decision_elements.get("pitching", "N/A"))

        # Review info
        review_y = self.height - 60


        return frame

    def _draw_info_box(self, frame, x, y, label, value):
        """Draw an information box"""
        cv2.rectangle(frame, (x, y), (x + 250, y + 40), self.COLORS["info_box"], 1)
        cv2.putText(frame, label, (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLORS["info_label"], 1)

        text_size = cv2.getTextSize(value, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.putText(frame, value, (x + 250 - text_size[0] - 10, y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS["info_text"], 2)

    def _draw_confidence_bar(self, frame, x, y, width, height, confidence):
        """Draw confidence bar"""
        cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
        fill_width = int(width * confidence)
        cv2.rectangle(frame, (x, y), (x + fill_width, y + height), self.COLORS["confidence_bar"], -1)

        percent_text = f"{confidence * 100:.1f}%"
        text_size = cv2.getTextSize(percent_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + height // 2 + text_size[1] // 2
        cv2.putText(frame, percent_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS["info_text"], 1)

    def process_video(self):
        """Process the video with all overlays"""
        frame_idx = 0
        frame_buffer = []

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Apply overlays
            frame = self._draw_trajectory_on_frame(frame, frame_idx)
            frame = self._add_decision_graphics(frame, frame_idx)

            # Write frame multiple times to slow down video
            for _ in range(self.slow_down_factor):
                self.out.write(frame)

            frame_idx += 1
            if frame_idx % 100 == 0:
                print(f"Processed {frame_idx}/{self.frame_count} frames")

        self.cap.release()
        self.out.release()
        print(f"Video processing complete. Output saved to: {self.output_path}")
        return self.output_path


def process_from_json_file(video_path, json_path, output_path=None):
    """Process video with trajectory data from JSON file"""
    with open(json_path, 'r') as f:
        trajectory_data = json.load(f)

    print("Loaded trajectory data:")
    print(f"- Decision: {trajectory_data.get('label', 'UNKNOWN')}")
    print(f"- Confidence: {trajectory_data.get('confidence', 0.0) * 100:.1f}%")
    print(f"- Trajectory points: {len(trajectory_data.get('predicted_trajectory', []))}")

    drs = CricketDRSOverlay(video_path, trajectory_data, output_path)
    return drs.process_video()


if __name__ == "__main__":
    # Example usage with hardcoded paths
    process_from_json_file("input_cricket_video.mp4", "trajectory_data.json", "output_drs_video.mp4")
