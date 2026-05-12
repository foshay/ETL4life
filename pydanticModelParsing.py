
import json

from models.employees1 import Employee as Employee1
from models.employees2 import Employee as Employee2
from models.employees3 import Employee as Employee3
from models.locations import Location
from models.locations2 import Location as Location2
from misc import runThousand

def parseLocationsV1():
    locations = []
    with open("json/locations.json") as file:
        raw_locations = json.load(file)
        locations = [Location.model_validate(location) for location in raw_locations]
    return locations

def parseLocationsV1_dict():
    locations = []
    with open("json/locations.json") as file:
        raw_locations = json.load(file)
        locations = [location for location in raw_locations]
    return locations

def parseLocationsV2():
    locations = []
    with open("json/locations_2.json") as file:
        raw_locations = json.load(file)
        locations = [Location2.model_validate(location) for location in raw_locations]
    
    operating_dates = [location.operating_dates for location in locations]

    return (locations, operating_dates)

def parseLocationsV2_dict():
    locations = []
    with open("json/locations_2.json") as file:
        raw_locations = json.load(file)
        locations = [location for location in raw_locations]
    operating_dates = [location["operating_dates"] for location in locations]
    return (locations, operating_dates)

def parseEmployees_1():
    employees = []
    with open("json/employees_1.json") as file:
        raw_employees = json.load(file)
        employees = [Employee1.model_validate(employee) for employee in raw_employees]
    return employees

def parseEmployees_2():
    employees = []
    with open("json/employees_2.json") as file:
        raw_employees = json.load(file)
        employees = [Employee2.model_validate(employee) for employee in raw_employees]
    return employees

def parseEmployees_3() -> list[Employee3]:
    employees = []
    with open("json/employees_3.json") as file:
        raw_employees = json.load(file)
        employees = [Employee3.model_validate(employee) for employee in raw_employees]
    return employees

if __name__ == "__main__":
    #runThousand(parseLocationsV1)
    #runThousand(parseLocationsV1_dict)
    #runThousand(parseLocationsV2)
    #runThousand(parseLocationsV2_dict)
    runThousand(parseEmployees_1)
    runThousand(parseEmployees_2)
    runThousand(parseEmployees_3)