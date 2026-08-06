"""
Lit weather_data_<slug>.csv pour chaque ville de cities.py et génère un
graphique (température + ressenti + humidité) dans weather_chart_<slug>.png.
"""
import csv
import os
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from cities import CITIES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fenêtre de temps affichée sur le graphique
DAYS_DISPLAYED = 4


def csv_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_data_{slug}.csv")


def chart_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_chart_{slug}.png")


def load(path):
    timestamps, temps, hums, apparent = [], [], [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                timestamps.append(datetime.fromisoformat(row["timestamp"]))
                temps.append(float(row["temperature_2m"]))
                hums.append(float(row["relative_humidity_2m"]))
            except (ValueError, KeyError, TypeError):
                continue
            try:
                apparent.append(float(row["apparent_temperature"]))
            except (ValueError, KeyError, TypeError):
                apparent.append(float("nan"))
    order = sorted(range(len(timestamps)), key=lambda i: timestamps[i])
    timestamps = [timestamps[i] for i in order]
    temps = [temps[i] for i in order]
    hums = [hums[i] for i in order]
    apparent = [apparent[i] for i in order]

    # Ne garde que les DAYS_DISPLAYED derniers jours
    if timestamps:
        cutoff = timestamps[-1] - timedelta(days=DAYS_DISPLAYED)
        keep = [i for i, t in enumerate(timestamps) if t >= cutoff]
        timestamps = [timestamps[i] for i in keep]
        temps = [temps[i] for i in keep]
        hums = [hums[i] for i in keep]
        apparent = [apparent[i] for i in keep]

    return timestamps, temps, hums, apparent


def midnights(start, end):
    """Liste des instants minuit (changement de journée) entre start et end."""
    current = datetime(start.year, start.month, start.day)
    if current < start:
        current += timedelta(days=1)
    result = []
    while current <= end:
        result.append(current)
        current += timedelta(days=1)
    return result


def plot(path, out_path, title):
    ts, temps, hums, apparent = load(path)
    if not ts:
        print(f"  pas encore de données à tracer ({path}).")
        return

    fig, ax1 = plt.subplots(figsize=(11, 5))

    # Traits verticaux en fond, un par changement de journée (minuit)
    for midnight in midnights(ts[0], ts[-1]):
        ax1.axvline(midnight, color="gray", linewidth=0.7, alpha=0.35, zorder=0)

    ax1.plot(ts, temps, color="tab:red", linewidth=1.5, label="Température (°C)", zorder=3)
    ax1.plot(
        ts, apparent, color="goldenrod", linewidth=1.3, alpha=0.85,
        label="Température ressentie (°C)", zorder=3,
    )
    ax1.set_ylabel("Température (°C)", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %Hh"))
    fig.autofmt_xdate()
    # L'axe démarre à 0, sauf s'il y a des températures négatives
    valid_temps = [t for t in temps + apparent if t == t]  # exclut les NaN
    ax1.set_ylim(bottom=min(0, min(valid_temps)))

    ax2 = ax1.twinx()
    ax2.plot(ts, hums, color="tab:blue", linewidth=1.2, alpha=0.6, label="Humidité (%)", zorder=2)
    ax2.set_ylabel("Humidité (%)", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")
    # L'humidité (%) ne peut pas être négative, l'axe démarre toujours à 0
    ax2.set_ylim(bottom=0)

    # Quadrillage pour une meilleure lisibilité
    ax1.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.4)
    ax1.set_axisbelow(True)

    # Légende commune aux deux axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    plt.title(title)
    fig.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  graphique enregistré : {out_path}")


def main():
    for city in CITIES:
        print(f"{city['name']}:")
        plot(csv_path(city["slug"]), chart_path(city["slug"]), f"Météo — {city['name']}")


if __name__ == "__main__":
    main()
