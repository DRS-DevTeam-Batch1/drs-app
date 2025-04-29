import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Optional

class DataProcessor:
    """Processes cricket ball trajectory data for analysis and modeling."""
    
    def _init_(self, pitch_length: float = 20.12):
        # Set up with standard cricket pitch length (in meters)
        self.pitch_length = pitch_length
    
    def parse_tuple_str(self, s: str) -> Optional[List[float]]:
        # Converts string like '(x,y,z)' into a list of numbers, returns None if empty
        if not isinstance(s, str) or not s or s == '""':
            return None
        s = s.strip('"').strip('()')
        if not s:
            return None
        try:
            return list(map(float, s.split(',')))
        except ValueError:
            return None
    
    def load_csv_dataset(self, csv_path: str) -> List[List[Dict[str, float]]]:
        # Reads CSV file and converts it into usable trajectory data
        df = pd.read_csv(csv_path)
        time_cols = [col for col in df.columns if col.startswith('t')]
        
        deliveries = []
        for _, row in df.iterrows():
            delivery = []
            for col in sorted(time_cols, key=lambda x: float(x[1:])):
                point = self.parse_tuple_str(row[col])
                if point:
                    # Adjust coordinates to real-world measurements
                    delivery.append({
                        'x': point[0], 
                        'y': point[1], 
                        'z': self.pitch_length * (1 - point[2]),  # Convert to meters
                        't': float(col[1:])
                    })
            # Only keep deliveries with enough data points
            if len(delivery) >= 5:
                deliveries.append(delivery)
        
        return deliveries
    
    def convert_to_physical_space(self, input_trajectory: List[Dict[str, float]]) -> List[Dict[str, float]]:
        # Changes normalized coordinates to real-world physical measurements
        return [{
            'x': p['x'],
            'y': p['y'],
            'z': self.pitch_length * (1 - p['z']),  # Convert z to actual distance
            't': p['t']
        } for p in input_trajectory]
    
    def prepare_training_data(self, deliveries: List[List[Dict[str, float]]], 
                             input_points: int = 5, output_points: int = 3) -> tuple:
        # Formats data for machine learning training
        X, y = [], []
        
        for traj in deliveries:
            if len(traj) >= input_points + output_points:
                # First N points as input features
                input_data = np.array([[p['x'], p['y'], p['z']] for p in traj[:input_points]]).flatten()
                X.append(input_data)
                
                # Next M points as prediction targets
                output_data = np.array([[p['x'], p['y'], p['z']] for p in traj[input_points:input_points+output_points]]).flatten()
                y.append(output_data)
        
        return np.array(X), np.array(y)
    
    def save_dataset_json(self, deliveries: List[List[Dict[str, float]]], output_path: str):
        # Saves processed data to JSON file for later use
        with open(output_path, 'w') as f:
            json.dump(deliveries, f, indent=2)
        print(f"Saved data to {output_path}")
    
    def load_dataset_json(self, json_path: str) -> List[List[Dict[str, float]]]:
        # Loads previously saved data from JSON file
        with open(json_path, 'r') as f:
            return json.load(f)


# Example of how to use this class
if __name__ == "_main_":
    processor = DataProcessor()
    
    # Load and process raw data file
    deliveries = processor.load_csv_dataset("bowling_trajectories.csv")
    print(f"Found {len(deliveries)} good deliveries")
    
    # Save the cleaned-up data
    processor.save_dataset_json(deliveries, "processed_trajectories.json")
    
    # Get data ready for machine learning
    X, y = processor.prepare_training_data(deliveries)
    print(f"Training data ready - inputs: {X.shape}, targets: {y.shape}")