"""
Pré-remplit weather_data_<slug>.csv avec les 7 derniers jours de relevés
toutes les 15 minutes (Open-Meteo, résolution "minutely_15") pour chaque
ville de cities.py. A lancer une fois par ville pour démarrer avec un
historique, avant de faire tourner fetch_weather.py en continu (ou pour
combler un trou après une extinction de l'ordinateur).
"""
import csv
import os
from datetime import datetime

import requests

from cities import CITIES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Colonnes du CSV : identiques à fetch_weather.py pour rester compatibles.
# weather_code et surface_pressure ne sont pas fournis en résolution 15 min
# par Open-Meteo : ces colonnes resteront vides pour les lignes de ce script.
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
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&minutely_15=temperature_2m,relative_humidity_2m,apparent_temperature,"
        "precipitation,rain,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
        "&past_days=7&forecast_days=1&timezone=Europe%2FParis"
    )


def fetch(lat, lon):
    resp = requests.get(build_url(lat, lon), timeout=20)
    resp.raise_for_status()
    return resp.json()["minutely_15"]


def csv_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_data_{slug}.csv")


def existing_timestamps(path):
    if not os.path.isfile(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["timestamp"] for row in csv.DictReader(f)}


def store(path, quarters):
    known = existing_timestamps(path)
    file_exists = os.path.isfile(path)
    now = datetime.now()
    added = 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        for i, ts in enumerate(quarters["time"]):
            if ts in known:
                continue
            # sécurité supplémentaire : on n'ajoute jamais un horodatage futur
            if datetime.fromisoformat(ts) > now:
                continue
            row = {"timestamp": ts}
            for key in FIELDS[1:]:
                values = quarters.get(key)
                row[key] = values[i] if values else None
            writer.writerow(row)
            added += 1
    print(f"  {added} relevés (15 min) ajoutés à {path}")


def main():
    for city in CITIES:
        print(f"{city['name']}:")
        try:
            quarters = fetch(city["lat"], city["lon"])
            store(csv_path(city["slug"]), quarters)
        except Exception as exc:
            print(f"  erreur : {exc}")


if __name__ == "__main__":
    main()
