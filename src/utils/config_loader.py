import json
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from config.json and environment variables"""
    load_dotenv()
    
    config = {
        'app_name': 'Worker Tracker Management System',
        'version': '1.0.0',
        'database': {
            'host': os.getenv('DB_HOST', 'localhost'),
            'name': os.getenv('DB_NAME', 'worker_tracker'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '')
        },
        'ml_model': {
            'model_path': os.getenv('ML_MODEL_PATH', 'models/worker_prediction.pkl'),
            'features': ['age', 'experience', 'skills', 'performance']
        }
    }
    
    # Load additional config from config.json if it exists
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config.update(json.load(f))
            
    return config 