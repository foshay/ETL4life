from functools import wraps
import time
import tracemalloc


def performance_counter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time * 1e6:.0f} microseconds")
        return result

    return wrapper

def runThousand(func, *args, **kwargs):
    total_time = 0
    total_mem = 0
    for i in range(1000):
        tracemalloc.start()
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        total_time += (end - start)
        total_mem += peak
    avg_time_microseconds = (total_time / 1000) * 1e6
    avg_peak_mem_kb = (total_mem / 1000) / 1024
    print(f"Average run time for {func.__name__} over 1000 runs: {avg_time_microseconds:.0f} microseconds")
    print(f"Average peak memory for {func.__name__} over 1000 runs: {avg_peak_mem_kb:.2f} KB")
