import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_data():
    """Load all datasets from the data directory."""

    persons = pd.read_csv(DATA_DIR / "persons.csv")
    cdr = pd.read_csv(DATA_DIR / "cdr.csv")
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")
    vehicles = pd.read_csv(DATA_DIR / "vehicles.csv")
    sightings = pd.read_csv(DATA_DIR / "vehicle_sightings.csv")
    incidents = pd.read_csv(DATA_DIR / "incidents.csv")
    intelligence_reports = pd.read_csv(
        DATA_DIR / "intelligence_reports.csv"
    )
    locations = pd.read_csv(DATA_DIR / "locations.csv")
    organizations = pd.read_csv(DATA_DIR / "organizations.csv")

    return {
        "persons": persons,
        "cdr": cdr,
        "transactions": transactions,
        "vehicles": vehicles,
        "sightings": sightings,
        "incidents": incidents,
        "intelligence_reports": intelligence_reports,
        "locations": locations,
        "organizations": organizations,
    }


def print_data_summary(data):
    """Print the number of records loaded from each dataset."""

    print("\n========== DATA SUMMARY ==========\n")

    for name, df in data.items():
        print(f"{name:25} {len(df):>5} records")

    print("\n==================================\n")