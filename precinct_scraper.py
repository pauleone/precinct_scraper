import csv
import os
from typing import List, Dict, Any

import requests

GOOGLE_CIVIC_API_KEY = os.getenv("GOOGLE_CIVIC_API_KEY")
VOTEAMERICA_API_KEY = os.getenv("VOTEAMERICA_API_KEY")
CIVIC_API_KEY = os.getenv("CIVIC_API_KEY")


def fetch_voteamerica(state: str) -> List[Dict[str, Any]]:
    """Fetch election offices from VoteAmerica for a given state."""
    if not VOTEAMERICA_API_KEY:
        return []
    url = f"https://api.voteamerica.com/election-offices/{state}"
    headers = {"Authorization": f"Bearer {VOTEAMERICA_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("offices", [])


def fetch_google_civic(address: str) -> Dict[str, Any]:
    """Fetch officials using Google Civic Information API."""
    if not GOOGLE_CIVIC_API_KEY:
        return {}
    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    params = {"key": GOOGLE_CIVIC_API_KEY, "address": address}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_civicapi(state: str) -> List[Dict[str, Any]]:
    """Fetch officials from CivicAPI."""
    if not CIVIC_API_KEY:
        return []
    url = "https://api.civicapi.org/officials"
    headers = {"apikey": CIVIC_API_KEY}
    params = {"state": state, "format": "json"}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])


def compile_records(states: List[str]) -> List[Dict[str, Any]]:
    """Aggregate data from multiple sources."""
    records = []
    for state in states:
        for office in fetch_voteamerica(state):
            records.append(
                {
                    "state": state,
                    "county": office.get("county"),
                    "precinct_name": office.get("name"),
                    "address": office.get("address"),
                    "official_name": office.get("official"),
                    "role": office.get("role"),
                    "email": office.get("email"),
                    "website": office.get("website"),
                    "source": "VoteAmerica",
                }
            )
        for result in fetch_civicapi(state):
            records.append(
                {
                    "state": state,
                    "county": result.get("county"),
                    "precinct_name": result.get("office"),
                    "address": result.get("address"),
                    "official_name": result.get("name"),
                    "role": result.get("role"),
                    "email": result.get("email"),
                    "website": result.get("website"),
                    "source": "CivicAPI",
                }
            )
    return records


def save_to_csv(records: List[Dict[str, Any]], filename: str) -> None:
    fieldnames = [
        "state",
        "county",
        "precinct_name",
        "address",
        "official_name",
        "role",
        "email",
        "website",
        "source",
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow(row)


def main() -> None:
    # Example states; extend as needed
    states = ["AL", "AK"]
    records = compile_records(states)
    save_to_csv(records, "precincts.csv")


if __name__ == "__main__":
    main()
