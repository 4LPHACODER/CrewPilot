import pickle
import os
import numpy as np
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from database.db_connection import DatabaseConnection
import logging
from utils.utils import log_error
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd

class WorkerPredictor:
    def __init__(self, db: DatabaseConnection, model_path: str = "models/worker_model.pkl"):
        """
        Initialize the predictor with database connection and model path
        
        Args:
            db: Database connection instance
            model_path: Path to save/load the model
        """
        self.db = db
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.logger = logging.getLogger(__name__)
        self._load_model()
        
    def _load_model(self):
        """
        Load the model from disk. If no model exists, initialize a new one.
        """
        try:
            # Create models directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            if os.path.exists(self.model_path):
                # Load existing model
                self.logger.info(f"Loading model from {self.model_path}")
                self.model = joblib.load(self.model_path)
                self.logger.info("Model loaded successfully")
            else:
                # Initialize new model
                self.logger.info("No existing model found. Initializing new model.")
                self._initialize_model()
                
        except Exception as e:
            log_error(e, {'action': 'load_model', 'model_path': self.model_path})
            self.logger.error(f"Error loading model: {str(e)}")
            self._initialize_model()

    def _initialize_model(self) -> None:
        """
        Initialize a new model with default parameters
        """
        try:
            # Create a pipeline with preprocessing and model
            self.model = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                ))
            ])
            
            # Save the initialized model
            self.save_model()
            self.logger.info("New model initialized and saved")
            
        except Exception as e:
            log_error(e, {'action': 'initialize_model'})
            self.logger.error(f"Error initializing model: {str(e)}")
            raise

    def save_model(self) -> None:
        """
        Save the current model to disk
        """
        try:
            # Create models directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Save model using joblib
            joblib.dump(self.model, self.model_path)
            self.logger.info(f"Model saved successfully to {self.model_path}")
            
        except Exception as e:
            log_error(e, {'action': 'save_model', 'model_path': self.model_path})
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Train the model with new data
        
        Args:
            X: Feature matrix
            y: Target values
            
        Returns:
            Dict containing training metrics
        """
        try:
            # Split data into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Calculate metrics
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            # Save the trained model
            self.save_model()
            
            metrics = {
                'train_score': train_score,
                'test_score': test_score,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model trained successfully. Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            log_error(e, {'action': 'train_model'})
            self.logger.error(f"Error training model: {str(e)}")
            raise

    def _get_worker_features(self, worker_id: int) -> np.ndarray:
        """
        Extract features for a worker from the database
        
        Args:
            worker_id: ID of the worker
            
        Returns:
            numpy array of features
        """
        try:
            # Get worker's tasks from the last 30 days
            query = """
                SELECT 
                    SUM(pp.hours_worked) as total_hours,
                    COUNT(t.id) as tasks_completed,
                    AVG(pp.efficiency_rate) as avg_efficiency,
                    AVG(CASE WHEN t.is_completed = 1 THEN 1 ELSE 0 END) as avg_completion
                FROM workers w
                LEFT JOIN performance_predictions pp ON w.id = pp.worker_id
                LEFT JOIN tasks t ON w.id = t.worker_id
                WHERE w.id = %s
                AND pp.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY w.id
            """
            result = self.db.fetch_one(query, (worker_id,))
            
            if not result:
                # Return default values if no data
                return np.array([[0, 0, 0.5, 0.5]])
            
            # Convert to numpy array
            features = np.array([[
                result['total_hours'] or 0,
                result['tasks_completed'] or 0,
                result['avg_efficiency'] or 0.5,
                result['avg_completion'] or 0.5
            ]])
            
            return features
            
        except Exception as e:
            log_error(e, {'action': 'get_worker_features', 'worker_id': worker_id})
            self.logger.error(f"Error getting worker features: {str(e)}")
            return np.array([[0, 0, 0.5, 0.5]])

    def predict_performance(self, worker_id: int) -> Dict[str, Union[float, List[float]]]:
        """
        Predict worker's performance score
        
        Args:
            worker_id: ID of the worker
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Get worker features
            features = self._get_worker_features(worker_id)
            
            # Make prediction
            if self.model is not None:
                predicted_score = float(self.model.predict(features)[0])
                # Get feature importances if available
                if hasattr(self.model.named_steps['regressor'], 'feature_importances_'):
                    importances = self.model.named_steps['regressor'].feature_importances_
                else:
                    importances = None
            else:
                # Fallback to default prediction
                predicted_score = self._default_prediction(features)
                importances = None
            
            # Ensure score is between 0 and 10
            predicted_score = max(0, min(10, predicted_score))
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(features, predicted_score)
            
            # Prepare features used
            features_used = {
                'hours_worked': float(features[0][0]),
                'tasks_completed': float(features[0][1]),
                'efficiency_rate': float(features[0][2]),
                'completion_rate': float(features[0][3])
            }
            
            # Save prediction to database
            self._save_prediction(worker_id, predicted_score, confidence_scores, features_used)
            
            return {
                'predicted_score': predicted_score,
                'confidence_scores': confidence_scores,
                'features_used': features_used,
                'feature_importances': importances.tolist() if importances is not None else None
            }
            
        except Exception as e:
            log_error(e, {'action': 'predict_performance', 'worker_id': worker_id})
            self.logger.error(f"Error predicting performance: {str(e)}")
            return self._default_prediction_result(worker_id)

    def _default_prediction(self, features: np.ndarray) -> float:
        """
        Fallback prediction logic using weighted average of features
        
        Args:
            features: numpy array of features
            
        Returns:
            float: Predicted score
        """
        weights = np.array([0.3, 0.3, 0.2, 0.2])  # Weights for each feature
        return float(np.sum(features * weights) * 10)  # Scale to 0-10

    def _calculate_confidence_scores(self, features: np.ndarray, predicted_score: float) -> List[float]:
        """
        Calculate confidence scores for the prediction
        
        Args:
            features: numpy array of features
            predicted_score: Predicted performance score
            
        Returns:
            List of confidence scores
        """
        # Simple confidence calculation based on feature completeness
        feature_completeness = np.mean(features > 0)
        prediction_stability = 1.0 - (np.std(features) / 10)
        
        return [float(feature_completeness), float(prediction_stability)]

    def _save_prediction(self, worker_id: int, predicted_score: float, 
                        confidence_scores: List[float], features_used: Dict[str, float]) -> None:
        """
        Save prediction result to database
        
        Args:
            worker_id: ID of the worker
            predicted_score: Predicted performance score
            confidence_scores: List of confidence scores
            features_used: Dictionary of features used
        """
        try:
            query = """
                INSERT INTO performance_predictions 
                (worker_id, predicted_score, confidence_score, features_used, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            self.db.execute_query(query, (
                worker_id,
                predicted_score,
                confidence_scores[0],  # Use the first confidence score
                str(features_used)
            ))
            
        except Exception as e:
            log_error(e, {
                'action': 'save_prediction',
                'worker_id': worker_id,
                'predicted_score': predicted_score
            })
            self.logger.error(f"Error saving prediction: {str(e)}")

    def get_prediction_history(self, worker_id: int, limit: int = 5) -> List[Dict]:
        """
        Get historical predictions for a worker
        
        Args:
            worker_id: ID of the worker
            limit: Maximum number of predictions to return
            
        Returns:
            List of prediction records
        """
        try:
            query = """
                SELECT * FROM performance_predictions
                WHERE worker_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.db.fetch_all(query, (worker_id, limit))
            
        except Exception as e:
            log_error(e, {'action': 'get_prediction_history', 'worker_id': worker_id})
            self.logger.error(f"Error getting prediction history: {str(e)}")
            return []

    def _default_prediction_result(self, worker_id: int) -> Dict[str, Any]:
        """
        Generate default prediction result when model fails
        
        Args:
            worker_id: ID of the worker
            
        Returns:
            Dictionary with default prediction
        """
        return {
            'predicted_score': 5.0,
            'confidence_scores': [0.5, 0.5],
            'features_used': {
                'hours_worked': 0,
                'tasks_completed': 0,
                'efficiency_rate': 0.5,
                'completion_rate': 0.5
            },
            'feature_importances': None
        } 