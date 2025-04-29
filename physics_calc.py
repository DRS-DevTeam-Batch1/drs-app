import numpy as np
from typing import List, Dict, Tuple
from scipy.optimize import curve_fit

class SimplePhysicsPredictor:
    def __init__(self):
        self.gravity = 9.8  
    
    def quadratic(self, t: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        return a * t**2 + b * t + c

    def fit_trajectory(self, points: List[Dict[str, float]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        t = np.array([p['t'] for p in points])
        x = np.array([p['x'] for p in points])
        y = np.array([p['y'] for p in points])
        z = np.array([p['z'] for p in points])

        popt_x, _ = curve_fit(self.quadratic, t, x)
        popt_y, _ = curve_fit(self.quadratic, t, y)
        popt_z, _ = curve_fit(self.quadratic, t, z)

        t_future = np.linspace(t[-1], t[-1] + 0.5, 10)
        x_pred = self.quadratic(t_future, *popt_x)
        y_pred = self.quadratic(t_future, *popt_y)
        z_pred = self.quadratic(t_future, *popt_z)

        return x_pred, y_pred, z_pred, t_future

    def predict(self, points: List[Dict[str, float]]) -> List[Dict[str, float]]:
        x, y, z, t = self.fit_trajectory(points)
        return [{'x': float(x[i]), 'y': float(y[i]), 'z': float(z[i]), 't': float(t[i])} for i in range(len(t))]

    def find_bounce(self, points: List[Dict[str, float]]) -> Dict[str, float]:
        all_y = [p['y'] for p in points]
        for i in range(1, len(all_y)):
            if all_y[i-1] > 0 and all_y[i] <= 0:
                return points[i]
        return None

    def swing_type(self, points: List[Dict[str, float]]) -> str:
        x_start = points[0]['x']
        x_end = points[-1]['x']
        delta = x_end - x_start

        if abs(delta) < 0.05:
            return "none"
        return "In-swing" if delta < 0 else "Out-swing"

    def impact_point(self, points: List[Dict[str, float]]) -> Dict[str, float]:
        closest = min(points, key=lambda p: abs(p['z']))
        return {'x': float(closest['x']), 'y': float(closest['y']), 'z': 0.0}


if __name__ == "__main__":
    data = [
        {"x": 0.0, "y": 2.0, "z": 18.0, "t": 0.0},
        {"x": 0.1, "y": 1.95, "z": 16.0, "t": 0.05},
        {"x": 0.2, "y": 1.85, "z": 14.0, "t": 0.1},
        {"x": 0.3, "y": 1.7, "z": 12.0, "t": 0.15},
        {"x": 0.35, "y": 1.5, "z": 10.0, "t": 0.2}
    ]

    predictor = SimplePhysicsPredictor()
    predicted = predictor.predict(data)
    bounce = predictor.find_bounce(predicted)
    swing = predictor.swing_type(predicted)
    impact = predictor.impact_point(predicted)

    print("Predicted Points:", predicted[:2])
    print("Bounce Point:", bounce)
    print("Swing Type:", swing)
    print("Impact Location:", impact)
