import time

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