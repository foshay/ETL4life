
import json

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

if __name__ == "__main__":
    #runThousand(parseLocationsV1)
    #runThousand(parseLocationsV1_dict)
    runThousand(parseLocationsV2)
    runThousand(parseLocationsV2_dict)
