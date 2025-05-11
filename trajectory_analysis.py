import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Dict, Tuple, Optional
import os
import joblib
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class TrajectoryAnalysis:
    def __init__(self):
        # Default cricket dimensions (in meters)
        self.pitch_length = 22.0  # Full pitch length
        self.stumps_height = 0.71  # Height of the stumps
        self.stumps_width = 0.23  # Width of the three stumps
        self.crease_distance = 1.22  # Distance from stumps to popping crease
        
        # Constants for trajectory prediction
        self.gravity = 9.81  # m/s²
        self.air_resistance_factor = 0.1  # Simplified air resistance factor
        
        # Results storage
        self.predicted_trajectory = []
        self.impact_location = None
        self.bounce_point = None
        self.swing_characteristics = {}
        
    def analyze_trajectory(self, ball_path: List[Dict], stump_position: Dict, 
                          bat_position: Dict, leg_position: Dict) -> Dict:
        """
        Main function to analyze ball trajectory and predict if it would hit stumps
        
        Args:
            ball_path: List of dictionaries with x, y, z, t coordinates
            stump_position: Dictionary with stumps coordinates
            bat_position: Dictionary with bat coordinates
            leg_position: Dictionary with leg coordinates
            
        Returns:
            Dictionary with analysis results
        """
        # Extract coordinates and time from ball path
        x_points = [point['x'] for point in ball_path]
        y_points = [point['y'] for point in ball_path]
        z_points = [point['z'] for point in ball_path]
        t_points = [point['t'] for point in ball_path]
        
        # Find the impact point with leg
        self.impact_location = {
            'x': leg_position['x'],
            'y': leg_position['y'],
            'z': leg_position['z']
        }
        
        # Find bounce point if it exists (local minimum in y)
        for i in range(1, len(y_points) - 1):
            if y_points[i] < y_points[i-1] and y_points[i] < y_points[i+1]:
                self.bounce_point = {
                    'x': x_points[i],
                    'y': y_points[i],
                    'z': z_points[i],
                    't': t_points[i]
                }
                break
        
        # Analyze swing characteristics
        self.analyze_swing(x_points, y_points, z_points, t_points)
        
        # Calculate predicted trajectory
        self.predict_future_trajectory(ball_path, leg_position, stump_position)
        
        # Determine if ball would hit stumps
        would_hit_stumps = self.check_stumps_hit(stump_position)
        
        # Prepare output
        result = {
            'predicted_trajectory': self.predicted_trajectory,
            'impact_location': self.impact_location,
            'bounce_point': self.bounce_point,
            'swing_characteristics': self.swing_characteristics,
            'would_hit_stumps': would_hit_stumps
        }
        
        return result
    
    def analyze_swing(self, x_points: List[float], y_points: List[float], 
                     z_points: List[float], t_points: List[float]) -> None:
        """
        Analyze the swing characteristics of the ball
        """
        # Calculate lateral movement (x-direction)
        if len(x_points) > 3:
            x_movement = x_points[-1] - x_points[0]
            self.swing_characteristics['lateral_movement'] = x_movement
            
            # Calculate swing direction (positive is right-to-left for right-handed batsman)
            if x_movement > 0.05:
                self.swing_characteristics['direction'] = "right-to-left"
            elif x_movement < -0.05:
                self.swing_characteristics['direction'] = "left-to-right"
            else:
                self.swing_characteristics['direction'] = "straight"
            
            # Calculate swing rate
            time_elapsed = t_points[-1] - t_points[0]
            if time_elapsed > 0:
                self.swing_characteristics['rate'] = abs(x_movement / time_elapsed)
            
            # Determine swing type
            if self.bounce_point:
                bounce_index = next((i for i, point in enumerate(t_points) if point == self.bounce_point['t']), None)
                if bounce_index:
                    pre_bounce_x = x_points[bounce_index] - x_points[0]
                    post_bounce_x = x_points[-1] - x_points[bounce_index]
                    
                    if abs(pre_bounce_x) < abs(post_bounce_x):
                        self.swing_characteristics['type'] = "reverse swing"
                    else:
                        self.swing_characteristics['type'] = "conventional swing"
    
    def predict_future_trajectory(self, ball_path: List[Dict], 
                                 leg_position: Dict, stump_position: Dict) -> None:
        """
        Predict the future trajectory of the ball after impact with leg
        """
        # Extract last few points before impact to fit trajectory
        if len(ball_path) >= 3:
            # Use points before impact to fit a polynomial
            pre_impact_points = ball_path[-3:]  # Last 3 points before impact
            
            # Extract coordinates
            t_pre = [p['t'] for p in pre_impact_points]
            x_pre = [p['x'] for p in pre_impact_points]
            y_pre = [p['y'] for p in pre_impact_points]
            z_pre = [p['z'] for p in pre_impact_points]
            
            # Fit polynomial functions to the pre-impact trajectory
            x_poly = np.polyfit(t_pre, x_pre, 1)  # Linear fit for x
            y_poly = np.polyfit(t_pre, y_pre, 2)  # Quadratic fit for y (parabolic)
            z_poly = np.polyfit(t_pre, z_pre, 1)  # Linear fit for z
            
            # Calculate velocity at impact
            last_t = t_pre[-1]
            x_vel = np.polyval(np.polyder(x_poly), last_t)
            y_vel = np.polyval(np.polyder(y_poly), last_t)
            z_vel = np.polyval(np.polyder(z_poly), last_t)
            
            # Calculate time to reach stumps
            distance_to_stumps = stump_position['z'] - leg_position['z']
            if z_vel > 0:  # Ensure ball is moving towards stumps
                time_to_stumps = distance_to_stumps / z_vel
                
                # Generate predicted trajectory points
                num_points = 20  # Number of points to generate
                t_future = np.linspace(last_t, last_t + time_to_stumps, num_points)
                
                # Calculate future positions
                self.predicted_trajectory = []
                for t in t_future:
                    # Apply physics model: initial velocity + gravity + simple air resistance
                    time_delta = t - last_t
                    
                    # x-coordinate (lateral movement)
                    x_pred = leg_position['x'] + x_vel * time_delta
                    
                    # y-coordinate (height) with gravity
                    y_pred = leg_position['y'] + y_vel * time_delta - 0.5 * self.gravity * time_delta**2
                    
                    # z-coordinate (depth)
                    z_pred = leg_position['z'] + z_vel * time_delta
                    
                    self.predicted_trajectory.append({
                        'x': float(x_pred),
                        'y': float(y_pred),
                        'z': float(z_pred),
                        't': float(t)
                    })
    
    def check_stumps_hit(self, stump_position: Dict) -> bool:
        """
        Check if the predicted trajectory would hit the stumps
        """
        if not self.predicted_trajectory:
            return False
        
        # Get the last point of the trajectory
        final_point = self.predicted_trajectory[-1]
        
        # Check if the final point is within the stumps dimensions
        x_diff = abs(final_point['x'] - stump_position['x'])
        y_diff = final_point['y']  # Assuming y=0 is ground level
        
        # Check if within stumps width and below stumps height
        return (x_diff <= self.stumps_width/2) and (y_diff <= self.stumps_height)
    
    def visualize_trajectory(self, ball_path: List[Dict], save_path: Optional[str] = None) -> None:
        """
        Visualize the actual and predicted trajectory - for debugging only
        
        Args:
            ball_path: List of dictionaries with x, y, z coordinates
            save_path: Path to save the visualization image
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot actual trajectory
        x_actual = [point['x'] for point in ball_path]
        y_actual = [point['y'] for point in ball_path]
        z_actual = [point['z'] for point in ball_path]
        ax.plot(x_actual, z_actual, y_actual, 'ro-', label='Actual Trajectory')
        
        # Plot predicted trajectory
        if self.predicted_trajectory:
            x_pred = [point['x'] for point in self.predicted_trajectory]
            y_pred = [point['y'] for point in self.predicted_trajectory]
            z_pred = [point['z'] for point in self.predicted_trajectory]
            ax.plot(x_pred, z_pred, y_pred, 'bo-', label='Predicted Trajectory')
        
        # Plot impact point
        if self.impact_location:
            ax.scatter(
                self.impact_location['x'], 
                self.impact_location['z'], 
                self.impact_location['y'], 
                color='purple', s=100, label='Impact Point'
            )
        
        # Plot bounce point
        if self.bounce_point:
            ax.scatter(
                self.bounce_point['x'], 
                self.bounce_point['z'], 
                self.bounce_point['y'], 
                color='green', s=100, label='Bounce Point'
            )
        
        # Set labels and title
        ax.set_xlabel('X (Lateral Position)')
        ax.set_zlabel('Y (Height)')
        ax.set_ylabel('Z (Depth)')
        ax.set_title('Ball Trajectory Analysis')
        ax.legend()
        
        # Save or show the figure
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()


# Generate dummy training data for ML model
def generate_dummy_data(num_samples=100):
    """
    Generate dummy data for training a machine learning model
    """
    data = []
    labels = []
    
    for _ in range(num_samples):
        # Generate random ball path
        ball_path = []
        x_start = random.uniform(-0.5, 0.5)
        y_start = random.uniform(1.5, 2.0)
        z_start = 0.0
        
        # Random velocity components
        vx = random.uniform(-0.1, 0.1)
        vy = random.uniform(-0.2, -0.1)
        vz = random.uniform(0.5, 0.7)
        
        # Generate path points
        for i in range(8):
            t = i * 0.1
            x = x_start + vx * t + random.uniform(-0.02, 0.02)
            y = y_start + vy * t - 0.5 * 9.81 * t**2 + random.uniform(-0.02, 0.02)
            z = z_start + vz * t * 20 + random.uniform(-0.02, 0.02)
            
            ball_path.append({
                "x": x,
                "y": max(0.1, y),  # Ensure y doesn't go below ground
                "z": z,
                "t": t
            })
        
        # Generate stump, bat and leg positions
        stump_position = {"x": random.uniform(-0.1, 0.1), "y": 0.0, "z": 20.0}
        bat_position = {"x": x_start + vx * 0.7 * 8, "y": 0.8, "z": 16.0}
        leg_position = {
            "x": x_start + vx * 0.7 * 7, 
            "y": y_start + vy * 0.7 * 7 - 0.5 * 9.81 * (0.7 * 7)**2,
            "z": z_start + vz * 0.7 * 7 * 20
        }
        
        # Would the ball hit the stumps?
        final_x = x_start + vx * 1.0 * 10
        final_y = y_start + vy * 1.0 * 10 - 0.5 * 9.81 * (1.0 * 10)**2
        
        # Label: would hit stumps or not
        would_hit = (abs(final_x - stump_position['x']) < 0.15) and (final_y < 0.7)
        
        data.append({
            'ball_path': ball_path,
            'stump_position': stump_position,
            'bat_position': bat_position,
            'leg_position': leg_position
        })
        
        labels.append(1 if would_hit else 0)
    
    return data, labels


# Extract features from ball path data
def extract_features(data):
    """
    Extract features from ball path data for machine learning
    """
    features = []
    for sample in data:
        ball_path = sample['ball_path']
        
        # Calculate features: avg velocity, direction, etc.
        x_points = [point['x'] for point in ball_path]
        y_points = [point['y'] for point in ball_path]
        z_points = [point['z'] for point in ball_path]
        t_points = [point['t'] for point in ball_path]
        
        # Simple features
        x_vel = (x_points[-1] - x_points[0]) / (t_points[-1] - t_points[0])
        y_vel = (y_points[-1] - y_points[0]) / (t_points[-1] - t_points[0])
        z_vel = (z_points[-1] - z_points[0]) / (t_points[-1] - t_points[0])
        
        # Calculate curvature/swing
        x_curve = 0
        if len(x_points) > 2:
            x_curve = x_points[-1] - 2*x_points[len(x_points)//2] + x_points[0]
        
        # Final position relative to leg
        leg_x = sample['leg_position']['x']
        leg_z = sample['leg_position']['z']
        stump_x = sample['stump_position']['x']
        
        # Features
        sample_features = [
            x_vel, y_vel, z_vel,
            x_curve,
            x_points[-1] - leg_x,
            stump_x - leg_x
        ]
        
        features.append(sample_features)
    
    return np.array(features)


class TrajectoryAnalysisWithML(TrajectoryAnalysis):
    """
    Enhanced TrajectoryAnalysis class that integrates both physics-based and 
    machine learning approaches for trajectory prediction
    """
    def __init__(self, model_path="trajectory_model.pkl"):
        super().__init__()
        self.model_path = model_path
        self.model = self.load_or_train_model()
    
    def load_or_train_model(self):
        """
        Load the trained model if it exists, otherwise train a new one
        """
        if os.path.exists(self.model_path):
            return self.load_model()
        else:
            print(f"Model not found at {self.model_path}. Training new model...")
            data, labels = generate_dummy_data(500)
            return self.train_and_save_model(data, labels)
    
    def load_model(self):
        """
        Load a previously trained model from disk
        """
        try:
            model = joblib.load(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
            return model
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None
    
    def train_and_save_model(self, data, labels):
        """
        Train a simple ML model for predicting if the ball would hit the stumps and save it
        """
        # Extract features
        X = extract_features(data)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate model
        accuracy = model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2f}")
        
        # Save model to disk
        joblib.dump(model, self.model_path)
        print(f"Model saved to {os.path.abspath(self.model_path)}")
        
        return model
    
    def get_ml_prediction(self, sample):
        """
        Get ML-based prediction for if the ball would hit the stumps
        """
        if self.model is None:
            return False, 0.0
            
        # Extract features from a single sample
        features = extract_features([sample])
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1]  # Probability of hitting stumps
        
        return bool(prediction), probability
    
    def analyze_trajectory(self, ball_path, stump_position, bat_position, leg_position):
        """
        Analyze trajectory using an integrated approach combining physics and ML
        """
        # Use the base physics model first
        physics_results = super().analyze_trajectory(ball_path, stump_position, bat_position, leg_position)
        physics_prediction = physics_results['would_hit_stumps']
        
        # Default confidence
        confidence = 0.5
        final_prediction = physics_prediction
        
        # Get ML prediction if model is available
        if self.model:
            sample = {
                'ball_path': ball_path,
                'stump_position': stump_position,
                'bat_position': bat_position,
                'leg_position': leg_position
            }
            
            ml_prediction, ml_confidence = self.get_ml_prediction(sample)
            
            # Determine final prediction through weighted approach
            # Weight ML prediction more if confidence is high, otherwise trust physics more
            if ml_confidence > 0.8:
                # High ML confidence, trust ML more (80% ML, 20% physics)
                final_prediction = ml_prediction
                confidence = ml_confidence
            elif ml_confidence < 0.2:
                # Low ML confidence, but strong signal in the opposite direction
                final_prediction = not ml_prediction
                confidence = 1 - ml_confidence
            elif abs(ml_confidence - 0.5) > 0.2:
                # Moderate ML confidence
                # If physics and ML agree, boost confidence
                if ml_prediction == physics_prediction:
                    final_prediction = ml_prediction
                    confidence = 0.5 + (ml_confidence - 0.5) * 0.6  # Weighted average
                else:
                    # If they disagree, go with ML but lower confidence
                    final_prediction = ml_prediction
                    confidence = ml_confidence * 0.8
            else:
                # ML is uncertain, rely more on physics
                final_prediction = physics_prediction
                confidence = 0.6  # Slight boost over base 0.5
        
        # Create comprehensive results incorporating both methods
        results = {
            'would_hit_stumps': final_prediction,
            'confidence': float(confidence),
            'predicted_trajectory': physics_results['predicted_trajectory'],
            'impact_location': physics_results['impact_location'],
            'bounce_point': physics_results['bounce_point'],
            'swing_characteristics': physics_results['swing_characteristics']
        }
        
        return results


# Main input/output functions for the DRS system
def predict_trajectory(ball_path, stump_position, bat_position, leg_position, model_path="trajectory_model.pkl"):
    """
    Main function to be called by the DRS system to predict ball trajectory
    
    Args:
        ball_path: List of dictionaries with x, y, z, t coordinates
        stump_position: Dictionary with stumps coordinates
        bat_position: Dictionary with bat coordinates
        leg_position: Dictionary with leg coordinates
        model_path: Path to trained model file
        
    Returns:
        Dictionary with analysis results
    """
    # Always use the combined ML and physics analysis
    analyzer = TrajectoryAnalysisWithML(model_path=model_path)
    results = analyzer.analyze_trajectory(ball_path, stump_position, bat_position, leg_position)
    
    # Format the results for DRS display
    formatted_results = {
        'decision': 'OUT' if results['would_hit_stumps'] else 'NOT OUT',
        'confidence': results.get('confidence', 0.5),
        'predicted_trajectory': results['predicted_trajectory'],
        'impact_location': results['impact_location'],
        'bounce_point': results['bounce_point'],
        'swing_characteristics': results['swing_characteristics']
    }
    
    return formatted_results


# Function to test the system
def test_traj():
    """
    Test function for the DRS system
    """
    # Example data
    ball_path = [
        {"x": 0.1, "y": 1.8, "z": 0.0, "t": 0.0},
        {"x": 0.15, "y": 1.7, "z": 2.0, "t": 0.1},
        {"x": 0.2, "y": 1.5, "z": 4.0, "t": 0.2},  
        {"x": 0.25, "y": 1.2, "z": 6.0, "t": 0.3},
        {"x": 0.3, "y": 0.8, "z": 8.0, "t": 0.4},
        {"x": 0.35, "y": 0.5, "z": 10.0, "t": 0.5},
        {"x": 0.4, "y": 0.7, "z": 12.0, "t": 0.6},
        {"x": 0.45, "y": 0.9, "z": 14.0, "t": 0.7}
    ]
    
    stump_position = {"x": 0.7, "y": 0.0, "z": 20.0}
    bat_position = {"x": 0.6, "y": 0.8, "z": 16.0}
    leg_position = {"x": 0.5, "y": 0.9, "z": 15.0}
    
    # Run the integrated analysis
    print("\nRunning trajectory analysis...")
    results = predict_trajectory(
        ball_path, stump_position, bat_position, leg_position,
        model_path="trajectory_model.pkl"
    )
    
    print(f"Decision: {results['decision']}")
    print(f"Confidence: {results['confidence']:.2f}")
    print(f"Impact location: {results['impact_location']}")
    print(f"Bounce point: {results['bounce_point']}")
    print(f"Swing characteristics: {results['swing_characteristics']}")
    print(f"Number of predicted points: {len(results['predicted_trajectory'])}")
    
    print(f"Number of predicted points: {results['predicted_trajectory']}")
    
    return results


if __name__ == "__main__":
    test_traj()
    