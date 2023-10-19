import time
import json
import os

def timer(get_logger): 
    """Decorator that reports the execution time."""
    def timer_wrap(func):
        def wrapper(*args, **kwargs):
            start_time = time.time() 
            result = func(*args, **kwargs) 
            end_time = time.time()
            msg = f'{func.__name__} finished executing after {end_time-start_time} seconds'
            print(msg)
            get_logger().info(msg)
            return result 
        return wrapper
    return timer_wrap 

def get_app_config_value(key):
    config_file_path = os.path.join(os.getcwd(), os.path.join('data', 'config.json'))
    with open(config_file_path, 'r') as config_file:
        config = json.loads(config_file.read())
        return config[key]
    
def update_app_config_value(key, value):
    config_file_path = os.path.join(os.getcwd(), os.path.join('data', 'config.json'))
    config = None
    with open(config_file_path, 'r') as config_file:
        config = json.loads(config_file.read())
        config[key] = value
    if config is not None:
        with open(config_file_path, 'w') as config_file:
            config_file.write(json.dumps(config))