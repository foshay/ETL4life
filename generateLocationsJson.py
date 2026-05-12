import argparse
import json
from datetime import date


def _open_date_for(index: int) -> str:
	year = 2002 + index
	return f"01/02/{year}"


def _build_v1_locations(count: int) -> list[dict]:
	locations = []
	for i in range(1, count + 1):
		locations.append(
			{
				"location_id": i,
				"name": f"location_{i}",
				"address": f"2245 Easy Street Apt {i}, Portland OR, 97201",
				"open_date": _open_date_for(i),
			}
		)
	return locations


def _build_v2_locations(count: int) -> list[dict]:
	locations = []
	for i in range(1, count + 1):
		locations.append(
			{
				"location_id": i,
				"name": f"location_{i}",
				"address": {
					"street": f"2245 Easy Street Apt {i}",
					"city": "Portland",
					"state": "OR",
					"zip_code": "97201",
				},
				"operating_dates": {
					"open_date": _open_date_for(i),
					"close_date": None,
				},
			}
		)
	return locations


def generateLocationsJson(version: str, count: int) -> str:
	if count < 1:
		raise ValueError("count must be at least 1")

	version_normalized = version.lower()
	if version_normalized == "v1":
		payload = _build_v1_locations(count)
		output_path = "json/locations.json"
	elif version_normalized == "v2":
		payload = _build_v2_locations(count)
		output_path = "json/locations_2.json"
	else:
		raise ValueError("version must be 'v1' or 'v2'")

	with open(output_path, "w", encoding="utf-8") as file:
		json.dump(payload, file, indent=4)

	return output_path


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Generate location JSON for v1 or v2 schemas."
	)
	parser.add_argument("--version", required=True, choices=["v1", "v2"])
	parser.add_argument("--count", required=True, type=int)
	return parser.parse_args()


if __name__ == "__main__":
	args = _parse_args()
	file_path = generateLocationsJson(args.version, args.count)
	print(f"Generated {args.count} {args.version} locations in {file_path}")
