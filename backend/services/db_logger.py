import logging
import os
from datetime import datetime
from functools import wraps

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up database logger
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.DEBUG)

# Create file handler
db_log_file = os.path.join(log_dir, 'database.log')
file_handler = logging.FileHandler(db_log_file)
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handler to logger
db_logger.addHandler(file_handler)

def log_db_error(error, operation=None, details=None):
    """Log database errors with detailed information"""
    error_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'operation': operation,
        'details': details
    }
    
    error_message = f"Database Error:\n"
    error_message += f"Operation: {operation}\n" if operation else ""
    error_message += f"Error Type: {error_info['error_type']}\n"
    error_message += f"Error Message: {error_info['error_message']}\n"
    error_message += f"Details: {details}\n" if details else ""
    
    db_logger.error(error_message)
    return error_info

def log_db_operation(func):
    """Decorator to log database operations and catch errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        operation = func.__name__
        try:
            result = await func(*args, **kwargs)
            db_logger.debug(f"Successfully executed {operation}")
            return result
        except Exception as e:
            error_info = log_db_error(
                error=e,
                operation=operation,
                details=f"Args: {args}, Kwargs: {kwargs}"
            )
            raise
    return wrapper