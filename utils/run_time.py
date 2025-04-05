import multiprocessing
import time
import functools
from typing import Any, Callable
"""
這東西廢了，別用
"""
def target_function(queue, func, args, kwargs):
    try:
        queue.put(func(*args, **kwargs))
    except Exception as e:
        queue.put(e)

def limit_runtime(timeout:float=5.0):
    """
    Limit the runtime of a function.
    :param timeout: timeout in seconds
    :return: Decorated function
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result_queue = multiprocessing.Queue()

           

            process = multiprocessing.Process(target=target_function, args=(result_queue,func, args, kwargs))
            process.start()
            process.join(timeout)

            if process.is_alive():
                process.terminate()  # 強制終止子進程
                process.join()
                raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout} seconds")

            result = result_queue.get()
            if isinstance(result, Exception):
                raise result
            return result

        return wrapper
    return decorator
    
if __name__ == "__main__":
    # Example usage
    @limit_runtime(timeout=2.0)
    def long_running_function():
        time.sleep(10)  # Simulate a long-running task
        return "Finished"

    try:
        print(long_running_function())
        print("Function completed successfully")
    except TimeoutError as e:
        print(e)