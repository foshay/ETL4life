import pandas as pd
from misc import performance_counter, runThousand

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


if __name__ == "__main__":
    runThousand(createDummyUsersA, 5)
    runThousand(createDummyUsersB, 5)
    runThousand(createDummyUsersC, 5)

    # Uncomment below to see the DataFrame
    # print(df)