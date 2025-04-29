import numpy as np
import pickle
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import os

from data_preprocessing import DataProcessor

class TrajectoryModelTrainer:
    def __init__(self, model_file: str = "trajectory_regressor.pkl", input_points: int = 5, output_points: int = 10):
        self.model_file = model_file
        self.input_points = input_points
        self.output_points = output_points
        self.model = None
        self.processor = DataProcessor()
    
    def train_model(self, dataset_path: str, polynomial_degree: int = 2, test_size: float = 0.2):
        if dataset_path.endswith('.csv'):
            deliveries = self.processor.load_csv_dataset(dataset_path)
        elif dataset_path.endswith('.json'):
            deliveries = self.processor.load_dataset_json(dataset_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")
        
        X, y = self.processor.prepare_training_data(
            deliveries, 
            input_points=self.input_points, 
            output_points=self.output_points
        )
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        self.model = make_pipeline(
            PolynomialFeatures(degree=polynomial_degree),
            LinearRegression()
        )
        
        self.model.fit(X_train, y_train)
        
        train_preds = self.model.predict(X_train)
        test_preds = self.model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_preds)
        test_mse = mean_squared_error(y_test, test_preds)
        
        results = {
            "train_mse": train_mse,
            "test_mse": test_mse,
            "input_shape": X.shape,
            "output_shape": y.shape,
            "polynomial_degree": polynomial_degree
        }
        
        self.save_model()
        return results
    
    def save_model(self):
        if self.model is None:
            raise ValueError("No model has been trained yet")
        
        os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
        with open(self.model_file, "wb") as f:
            pickle.dump(self.model, f)
    
    def load_model(self):
        if not os.path.exists(self.model_file):
            raise FileNotFoundError(f"Model file {self.model_file} not found")
        
        with open(self.model_file, "rb") as f:
            self.model = pickle.load(f)
        
        return self.model

if __name__ == "__main__":
    trainer = TrajectoryModelTrainer(output_points=10)
    results = trainer.train_model("bowling_trajectories.csv", polynomial_degree=2)
