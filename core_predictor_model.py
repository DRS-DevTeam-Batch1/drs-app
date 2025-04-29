import numpy as np
import pickle
import os
from typing import List, Dict, Any
from physics_predictor import PhysicsPredictor
from data_preprocessing import DataProcessor

class TrajectoryPredictor:
    #trajectory predictor with model and physics module
    def __init__(self, 
                 model_file: str = "trajectory_regressor.pkl",
                 pitch_length: float = 20.12,
                 input_points: int = 5,
                 output_points: int = 10):
        self.model_file = model_file
        self.pitch_length = pitch_length
        self.input_points = input_points
        self.output_points = output_points
        self.model = None
        self.physics = PhysicsPredictor(pitch_length=pitch_length)
        self.processor = DataProcessor(pitch_length=pitch_length)
        self._load_model()
    
    def _load_model(self):
        if os.path.exists(self.model_file):
           
            with open(self.model_file, "rb") as f:
                self.model = pickle.load(f)
            print(f"Loaded  {self.model_file}")
        else:
            print(f"Model file {self.model_file} not found.")

    
    def validate_input(self, input_trajectory: List[Dict[str, float]]) -> bool:
        if not isinstance(input_trajectory, list) or len(input_trajectory) < self.input_points:
            print(f"Input trajectory must be a list with at least {self.input_points} points")
            return False
        
        required_keys = ['x', 'y', 'z', 't']
        for point in input_trajectory:
            if not all(key in point for key in required_keys):
                print(f"Each point must contain keys: {required_keys}")
                return False
        
        return True

    def predict_model_based(self, input_trajectory: List[Dict[str, float]]) -> List[Dict[str, float]]:
        if self.model is None:
            print("No model loaded.")
            return []
        
        input_points = input_trajectory[:self.input_points]
        features = np.array([[p['x'], p['y'], p['z']] for p in input_points]).flatten().reshape(1, -1)

        try:
            pred_flat = self.model.predict(features)
            pred_points = pred_flat.reshape(-1, 3)
            last_time = input_points[-1]['t']
            time_step = 0.05
            pred_times = np.array([last_time + (i + 1) * time_step for i in range(len(pred_points))])
            
            predicted_path = []
            for i in range(len(pred_points)):
                predicted_path.append({
                    'x': float(pred_points[i, 0]),
                    'y': float(pred_points[i, 1]),
                    'z': float(pred_points[i, 2]),
                    't': float(pred_times[i])
                })
            return predicted_path
        except Exception as e:
            print(f"Prediction error: {e}")
            return []

    def predict_hybrid(self, input_trajectory: List[Dict[str, float]]) -> List[Dict[str, float]]:
        if not self.validate_input(input_trajectory):
            return []
        
        phys_input = self.processor.convert_to_physical_space(input_trajectory)
        model_predictions = self.predict_model_based(phys_input) if self.model else []
        physics_predictions = self.physics.predict_physics_based(phys_input)
        
        if model_predictions and physics_predictions:
            hybrid_predictions = []
            for i in range(min(len(model_predictions), len(physics_predictions))):
                hybrid_predictions.append({
                    'x': model_predictions[i]['x'],
                    'y': model_predictions[i]['y'],
                    'z': physics_predictions[i]['z'],
                    't': physics_predictions[i]['t']
                })
            return hybrid_predictions
        else:
            return model_predictions if model_predictions else physics_predictions

    def analyze_trajectory(self, input_trajectory: List[Dict[str, float]]) -> Dict[str, Any]:
        if not self.validate_input(input_trajectory):
            return {
                "error": "Invalid input trajectory",
                "predicted_path": [],
                "impact_location": None,
                "bounce_point": None,
                "swing_type": "unknown"
            }
        
        phys_input = self.processor.convert_to_physical_space(input_trajectory)
        predicted_path = self.predict_hybrid(input_trajectory)
        bounce_point = self.physics.calculate_bounce_point(phys_input, predicted_path)
        swing_type = self.physics.determine_swing_type(phys_input, predicted_path)
        impact_location = self.physics.calculate_impact_location(predicted_path)
        
        return {
            "predicted_path": predicted_path,
            "impact_location": impact_location,
            "bounce_point": bounce_point,
            "swing_type": swing_type
        }

# Sample test execution || just for demonstration.
if __name__ == "__main__":
    predictor = TrajectoryPredictor()
    sample_input = [
        {"x": 0.9, "y": 1.8, "z": 1, "t": 0.0},
        {"x": 0.85, "y": 1.75, "z": 2, "t": 0.05},
        {"x": 0.8, "y": 1.7, "z": 3, "t": 0.1},
        {"x": 0.75, "y": 1.6, "z": 4, "t": 0.15},
        {"x": 0.67, "y": 1.2, "z": 5, "t": 0.2},
        {"x": 0.65, "y": 1.0, "z": 5.8, "t": 0.25},
        {"x": 0.63, "y": 0.8, "z": 6.5, "t": 0.3},
        {"x": 0.6, "y": 0.5, "z": 7.3, "t": 0.35}
    ]
    result = predictor.analyze_trajectory(sample_input)
    
    print("Trajectory Analysis Results:")
    print(f"Predicted points: {len(result['predicted_path'])}")
    print(f"Impact location: {result['impact_location']}")
    print(f"Bounce point: {result['bounce_point']}")
    print(f"Swing type: {result['swing_type']}")
