"""
Récupère le relevé météo actuel (Open-Meteo) pour chaque ville de cities.py
et l'ajoute dans weather_data_<slug>.csv.

A lancer périodiquement (ex: toutes les 10 min) pour construire un historique.
"""
import csv
import os
import requests

from cities import CITIES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        "precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m,"
        "wind_gusts_10m,surface_pressure"
        "&timezone=Europe%2FParis"
    )


def fetch(lat, lon):
    resp = requests.get(build_url(lat, lon), timeout=15)
    resp.raise_for_status()
    return resp.json()["current"]


def csv_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_data_{slug}.csv")


def existing_timestamps(path):
    if not os.path.isfile(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["timestamp"] for row in csv.DictReader(f)}


def store(path, data):
    ts = data.get("time")
    if ts in existing_timestamps(path):
        print(f"  déjà présent ({ts}), rien à faire.")
        return

    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        row = {"timestamp": ts}
        for key in FIELDS[1:]:
            row[key] = data.get(key)
        writer.writerow(row)
    print(f"  relevé enregistré ({ts}) : {data.get('temperature_2m')}°C")


def main():
    for city in CITIES:
        print(f"{city['name']}:")
        try:
            data = fetch(city["lat"], city["lon"])
            store(csv_path(city["slug"]), data)
        except Exception as exc:
            print(f"  erreur : {exc}")


if __name__ == "__main__":
    main()
