"""
Enrichit weather_data_<slug>.csv avec un historique plus ancien (jusqu'à
1 mois) via l'API Archive d'Open-Meteo (données réelles ERA5), pour chaque
ville de cities.py. Résolution horaire uniquement (le 15 minutes n'est
disponible que sur les derniers jours, voir seed_history.py). A lancer une
fois pour compléter l'historique.
"""
import csv
import os
from datetime import date, timedelta

import requests

from cities import CITIES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# L'API Archive (ERA5) a un délai d'environ 5 jours avant d'avoir des
# données consolidées : on s'arrête 6 jours avant aujourd'hui pour éviter
# les trous récents (déjà couverts par seed_history.py / fetch_weather.py).
END_DATE = date.today() - timedelta(days=6)
START_DATE = date.today() - timedelta(days=30)

FIELDS = [
    "timestamp",
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "weather_code",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
]


def build_url(lat, lon):
    return (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START_DATE.isoformat()}&end_date={END_DATE.isoformat()}"
        "&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,"
        "precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m,"
        "wind_gusts_10m,surface_pressure"
        "&timezone=Europe%2FParis"
    )


def fetch(lat, lon):
    resp = requests.get(build_url(lat, lon), timeout=30)
    resp.raise_for_status()
    return resp.json()["hourly"]


def csv_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_data_{slug}.csv")


def existing_timestamps(path):
    if not os.path.isfile(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["timestamp"] for row in csv.DictReader(f)}


def sort_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    rows.sort(key=lambda r: r["timestamp"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def store(path, hourly):
    known = existing_timestamps(path)
    file_exists = os.path.isfile(path)
    added = 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        for i, ts in enumerate(hourly["time"]):
            if ts in known:
                continue
            row = {"timestamp": ts}
            for key in FIELDS[1:]:
                values = hourly.get(key)
                row[key] = values[i] if values else None
            writer.writerow(row)
            added += 1

    if added:
        sort_csv(path)

    print(
        f"  {added} relevés archive (horaire, {START_DATE} → {END_DATE}) "
        f"ajoutés à {path}"
    )


def main():
    for city in CITIES:
        print(f"{city['name']}:")
        try:
            hourly = fetch(city["lat"], city["lon"])
            store(csv_path(city["slug"]), hourly)
        except Exception as exc:
            print(f"  erreur : {exc}")


if __name__ == "__main__":
    main()
