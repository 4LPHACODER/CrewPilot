import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import re
from decimal import Decimal
import logging
import os
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class DataConversionError(Exception):
    """Custom exception for data conversion errors"""
    pass

def validate_worker_data(data: Dict[str, Any]) -> bool:
    """
    Validate worker data before saving to database
    
    Args:
        data: Dictionary containing worker data
        
    Returns:
        bool: True if data is valid
        
    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ['name', 'position', 'salary', 'status', 'performance_score']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate name
    if not isinstance(data['name'], str) or len(data['name'].strip()) < 2:
        raise ValidationError("Name must be a string with at least 2 characters")
    
    # Validate position
    if not isinstance(data['position'], str) or len(data['position'].strip()) < 2:
        raise ValidationError("Position must be a string with at least 2 characters")
    
    # Validate salary
    try:
        salary = float(data['salary'])
        if salary < 0:
            raise ValidationError("Salary cannot be negative")
    except (ValueError, TypeError):
        raise ValidationError("Salary must be a valid number")
    
    # Validate status
    valid_statuses = ['active', 'inactive', 'on_leave']
    if data['status'] not in valid_statuses:
        raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
    
    # Validate performance score
    try:
        score = float(data['performance_score'])
        if not (0 <= score <= 10):
            raise ValidationError("Performance score must be between 0 and 10")
    except (ValueError, TypeError):
        raise ValidationError("Performance score must be a valid number")
    
    return True

def validate_prediction_data(data: Dict[str, Any]) -> bool:
    """
    Validate prediction data before saving to database
    
    Args:
        data: Dictionary containing prediction data
        
    Returns:
        bool: True if data is valid
        
    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ['worker_id', 'predicted_score', 'confidence_scores', 'features_used']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate worker_id
    if not isinstance(data['worker_id'], int) or data['worker_id'] <= 0:
        raise ValidationError("Worker ID must be a positive integer")
    
    # Validate predicted_score
    try:
        score = float(data['predicted_score'])
        if not (0 <= score <= 10):
            raise ValidationError("Predicted score must be between 0 and 10")
    except (ValueError, TypeError):
        raise ValidationError("Predicted score must be a valid number")
    
    # Validate confidence_scores
    if not isinstance(data['confidence_scores'], list) or len(data['confidence_scores']) != 2:
        raise ValidationError("Confidence scores must be a list of 2 values")
    
    # Validate features_used
    if not isinstance(data['features_used'], dict):
        raise ValidationError("Features used must be a dictionary")
    
    return True

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def to_json(data: Any) -> str:
    """
    Convert data to JSON string
    
    Args:
        data: Data to convert
        
    Returns:
        str: JSON string
        
    Raises:
        DataConversionError: If conversion fails
    """
    try:
        return json.dumps(data, cls=DateTimeEncoder)
    except Exception as e:
        raise DataConversionError(f"Error converting to JSON: {str(e)}")

def from_json(json_str: str) -> Any:
    """
    Convert JSON string to Python object
    
    Args:
        json_str: JSON string to convert
        
    Returns:
        Any: Python object
        
    Raises:
        DataConversionError: If conversion fails
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        raise DataConversionError(f"Error converting from JSON: {str(e)}")

def format_currency(amount: float) -> str:
    """Format a number as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format a number as percentage"""
    return f"{value:.1f}%"

def format_date(date: datetime) -> str:
    """Format a datetime object as a string"""
    return date.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for all operating systems
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

def ensure_directory(directory: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with context information"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
    }
    
    if context:
        if isinstance(context, dict):
            error_info.update(context)
        else:
            error_info["context"] = str(context)
    
    logging.error(json.dumps(error_info))

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator for retrying functions on failure
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        logger.warning(f"Retrying {func.__name__} (attempt {attempt + 1}/{max_attempts})")
            
            raise last_error
        return wrapper
    return decorator

def validate_email(email: str) -> bool:
    """Validate an email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate a phone number"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def get_file_extension(filename: str) -> str:
    """Get the extension of a file"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_valid_file_type(filename: str, allowed_extensions: list) -> bool:
    """Check if a file has an allowed extension"""
    return get_file_extension(filename) in allowed_extensions

def generate_unique_id() -> str:
    """Generate a unique ID"""
    import uuid
    return str(uuid.uuid4())

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length"""
    return text[:max_length] + '...' if len(text) > max_length else text

def format_file_size(size_in_bytes: int) -> str:
    """Format file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} PB"

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ) 