import pandas as pd
import time
import tracemalloc
import time
from functools import wraps


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

#@performance_counter
def createDummyUsersA(userCount: int) -> pd.DataFrame:
    data = []
    for i in range(userCount):
        user_data = _genDummyUserData(user_id=i+1)
        data.append(user_data)
    return pd.DataFrame(data)

#@performance_counter
def createDummyUsersB(userCount: int) -> pd.DataFrame:
    data = {
        'EmployeeId': [],
        'FirstName': [],
        'LastName': [],
        'Email': []
    }
    for i in range(userCount):
        user_data = _genDummyUserData(user_id=i+1)
        data['EmployeeId'].append(user_data['UserId'])
        data['FirstName'].append(user_data['FirstName'])
        data['LastName'].append(user_data['LastName'])
        data['Email'].append(user_data['Email'])
    return pd.DataFrame(data)

#@performance_counter
def createDummyUsersC(userCount: int) -> pd.DataFrame:
    """Creates a dummy user DataFrame for testing purposes."""
    data = {
        'UserId': [],
        'FirstName': [],
        'LastName': [],
        'Email': []
    }
    for i in range(userCount):
        user_data = _genDummyUserData(user_id=i+1)
        for key, value in user_data.items():
            data[key].append(value)
    return pd.DataFrame(data)

def _genDummyUserData(user_id: int) -> dict:
    return {
        'UserId': user_id,
        'FirstName': 'Edward',
        'LastName': 'Elric',
        'Email': 'Elric.Edward@example.com'
    }

def runThousand(func):
    total_time = 0
    total_mem = 0
    for i in range(1000):
        tracemalloc.start()
        start = time.perf_counter()
        func(5)
        end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        total_time += (end - start)
        total_mem += peak
    avg_time_microseconds = (total_time / 1000) * 1e6
    avg_peak_mem_kb = (total_mem / 1000) / 1024
    print(f"Average run time for {func.__name__} over 1000 runs: {avg_time_microseconds:.0f} microseconds")
    print(f"Average peak memory for {func.__name__} over 1000 runs: {avg_peak_mem_kb:.2f} KB")

if __name__ == "__main__":
    runThousand(createDummyUsersA)
    runThousand(createDummyUsersB)
    runThousand(createDummyUsersC)

    # Uncomment below to see the DataFrame
    # print(df)