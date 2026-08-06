"""
Génère un tableau de bord HTML interactif (weather_dashboard.html) pour
toutes les villes de cities.py : sélecteur de ville, graphiques zoomables
(Plotly) + tableau de données triable et filtrable. A ouvrir directement
dans un navigateur, à régénérer quand on veut une vue à jour (après un
fetch_weather.py par exemple).
"""
import csv
import json
import os

from cities import CITIES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "weather_dashboard.html")

NUMERIC_FIELDS = [
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


def csv_path(slug):
    return os.path.join(SCRIPT_DIR, f"weather_data_{slug}.csv")


def to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_rows(slug):
    path = csv_path(slug)
    if not os.path.isfile(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r["timestamp"])
    data = []
    for r in rows:
        item = {"timestamp": r["timestamp"]}
        for field in NUMERIC_FIELDS:
            item[field] = to_float(r.get(field))
        data.append(item)
    return data


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Météo</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root {
    --red: #c0392b;
    --gold: #b8860b;
    --blue: #2980b9;
    --green: #27ae60;
    --gray: #7f8c8d;
    --bg: #f7f7f5;
    --card: #ffffff;
    --border: #e0e0e0;
    --text: #2c2c2c;
    --thead-bg: #fafafa;
    --thead-bg-hover: #f0f0f0;
    --row-hover: #fafafa;
    --row-border: #f0f0f0;
    --input-bg: #ffffff;
  }
  body.dark {
    --bg: #14161a;
    --card: #1e2126;
    --border: #2f333b;
    --text: #e6e6e6;
    --gray: #9aa0a6;
    --thead-bg: #24272e;
    --thead-bg-hover: #2b2f37;
    --row-hover: #262a31;
    --row-border: #2a2e35;
    --input-bg: #1b1e23;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 24px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    transition: background-color 0.2s ease, color 0.2s ease;
  }
  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    flex-wrap: wrap;
  }
  .top-bar-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  h1 {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 4px 0;
  }
  #city-select {
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    cursor: pointer;
  }
  #theme-toggle {
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
  }
  #theme-toggle:hover { opacity: 0.8; }
  .subtitle {
    color: var(--gray);
    font-size: 13px;
    margin-bottom: 20px;
  }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 20px;
  }
  .card h2 {
    font-size: 14px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: var(--text);
  }
  .table-controls {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }
  .table-controls input {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13px;
    min-width: 220px;
    background: var(--input-bg);
    color: var(--text);
  }
  .table-controls .count {
    font-size: 12px;
    color: var(--gray);
  }
  .table-wrap {
    max-height: 480px;
    overflow: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 12.5px;
  }
  thead th {
    position: sticky;
    top: 0;
    background: var(--thead-bg);
    border-bottom: 1px solid var(--border);
    text-align: left;
    padding: 8px 10px;
    cursor: pointer;
    white-space: nowrap;
    user-select: none;
  }
  thead th:hover { background: var(--thead-bg-hover); }
  thead th.sorted-asc::after { content: " \\25B2"; font-size: 9px; }
  thead th.sorted-desc::after { content: " \\25BC"; font-size: 9px; }
  tbody td {
    padding: 6px 10px;
    border-bottom: 1px solid var(--row-border);
    white-space: nowrap;
  }
  tbody tr:hover { background: var(--row-hover); }
</style>
</head>
<body>

<div class="top-bar">
  <div>
    <h1 id="page-title">Météo</h1>
    <div class="subtitle" id="subtitle"></div>
  </div>
  <div class="top-bar-right">
    <select id="city-select"></select>
    <button id="theme-toggle">🌙 Mode nuit</button>
  </div>
</div>

<div class="card">
  <h2>Température & humidité</h2>
  <div id="chart-temp" style="height: 420px;"></div>
</div>

<div class="card">
  <h2>Vent & précipitation</h2>
  <div id="chart-wind" style="height: 380px;"></div>
</div>

<div class="card">
  <h2>Données brutes</h2>
  <div class="table-controls">
    <input type="text" id="search" placeholder="Filtrer (ex: 2026-08-05, ou 2026-08-05T20)">
    <span class="count" id="row-count"></span>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr id="table-head"></tr></thead>
      <tbody id="table-body"></tbody>
    </table>
  </div>
</div>

<script>
const CITIES_META = __CITIES_META_JSON__;
const CITIES_DATA = __CITIES_DATA_JSON__;

const CITY_KEY = "meteo-marcq-city";
const THEME_KEY = "meteo-marcq-theme";

// --- Ville sélectionnée ---
function initialCity() {
  const stored = localStorage.getItem(CITY_KEY);
  if (stored && CITIES_DATA[stored]) return stored;
  return CITIES_META[0] ? CITIES_META[0].slug : null;
}
let currentSlug = initialCity();

const citySelect = document.getElementById("city-select");
CITIES_META.forEach(c => {
  const opt = document.createElement("option");
  opt.value = c.slug;
  opt.textContent = c.name;
  citySelect.appendChild(opt);
});
citySelect.value = currentSlug;
citySelect.addEventListener("change", () => {
  currentSlug = citySelect.value;
  localStorage.setItem(CITY_KEY, currentSlug);
  renderAll();
});

function currentData() {
  return CITIES_DATA[currentSlug] || [];
}

function currentCityName() {
  const meta = CITIES_META.find(c => c.slug === currentSlug);
  return meta ? meta.name : currentSlug;
}

function series(data, key) {
  return data.map(d => d[key]);
}

// --- Thème clair / sombre ---
function getStoredTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "dark" || stored === "light") return stored;
  return (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
    ? "dark" : "light";
}

let isDark = getStoredTheme() === "dark";
document.body.classList.toggle("dark", isDark);

function themeColors(dark) {
  return dark
    ? {
        paper: "#1e2126", plot: "#1e2126", font: "#e6e6e6", grid: "#33373f",
        rsBg: "#2b2f37", rsActive: "#3a3f47",
      }
    : {
        paper: "#ffffff", plot: "#ffffff", font: "#2c2c2c", grid: "#eeeeee",
        rsBg: "#f0f0f0", rsActive: "#d8d8d8",
      };
}

function rangeButtons() {
  return [
    { count: 1, label: "1j", step: "day", stepmode: "backward" },
    { count: 7, label: "7j", step: "day", stepmode: "backward" },
    { count: 30, label: "30j", step: "day", stepmode: "backward" },
    { count: 90, label: "90j", step: "day", stepmode: "backward" },
    { step: "all", label: "Tout" },
  ];
}

function tempLayout(c) {
  return {
    margin: { t: 10, r: 60, b: 80, l: 50 },
    legend: { orientation: "h", y: -0.35, yanchor: "top", x: 0.5, xanchor: "center", font: { color: c.font } },
    paper_bgcolor: c.paper,
    plot_bgcolor: c.plot,
    font: { color: c.font },
    xaxis: {
      gridcolor: c.grid,
      zerolinecolor: c.grid,
      rangeslider: { visible: true, thickness: 0.08 },
      rangeselector: {
        bgcolor: c.rsBg,
        activecolor: c.rsActive,
        bordercolor: c.grid,
        font: { color: c.font },
        buttons: rangeButtons(),
      },
    },
    yaxis: { title: "Température (°C)", gridcolor: c.grid, zerolinecolor: c.grid },
    yaxis2: { title: "Humidité (%)", overlaying: "y", side: "right", range: [0, 100], gridcolor: c.grid },
  };
}

function windLayout(c) {
  return {
    margin: { t: 10, r: 60, b: 70, l: 50 },
    legend: { orientation: "h", y: -0.2, yanchor: "top", x: 0.5, xanchor: "center", font: { color: c.font } },
    paper_bgcolor: c.paper,
    plot_bgcolor: c.plot,
    font: { color: c.font },
    xaxis: {
      gridcolor: c.grid,
      zerolinecolor: c.grid,
      rangeselector: {
        bgcolor: c.rsBg,
        activecolor: c.rsActive,
        bordercolor: c.grid,
        font: { color: c.font },
        buttons: rangeButtons(),
      },
    },
    yaxis: { title: "Vent (km/h)", gridcolor: c.grid, zerolinecolor: c.grid },
    yaxis2: { title: "Précipitation (mm)", overlaying: "y", side: "right", gridcolor: c.grid },
  };
}

function buildTraces(data) {
  const timestamps = data.map(d => d.timestamp);
  const s = key => series(data, key);
  return {
    temp: [
      { x: timestamps, y: s("temperature_2m"), name: "Température (°C)", mode: "lines", line: { color: "#c0392b", width: 1.5 } },
      { x: timestamps, y: s("apparent_temperature"), name: "Ressenti (°C)", mode: "lines", line: { color: "#b8860b", width: 1.3 } },
      { x: timestamps, y: s("relative_humidity_2m"), name: "Humidité (%)", mode: "lines", line: { color: "#2980b9", width: 1.1 }, yaxis: "y2", opacity: 0.6 },
    ],
    wind: [
      { x: timestamps, y: s("wind_speed_10m"), name: "Vent (km/h)", mode: "lines", line: { color: "#27ae60", width: 1.3 } },
      { x: timestamps, y: s("wind_gusts_10m"), name: "Rafales (km/h)", mode: "lines", line: { color: "#7f8c8d", width: 1, dash: "dot" } },
      { x: timestamps, y: s("precipitation"), name: "Précipitation (mm)", type: "bar", marker: { color: "#2980b9" }, yaxis: "y2", opacity: 0.5 },
    ],
  };
}

function updateToggleLabel() {
  document.getElementById("theme-toggle").textContent =
    isDark ? "☀️ Mode jour" : "🌙 Mode nuit";
}

document.getElementById("theme-toggle").addEventListener("click", () => {
  isDark = !isDark;
  document.body.classList.toggle("dark", isDark);
  localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
  updateToggleLabel();
  renderCharts();
});

function renderCharts() {
  const data = currentData();
  const traces = buildTraces(data);
  const c = themeColors(isDark);
  Plotly.react("chart-temp", traces.temp, tempLayout(c), { responsive: true });
  Plotly.react("chart-wind", traces.wind, windLayout(c), { responsive: true });
}

// --- Tableau de données : entêtes ---
const COLUMNS = [
  "timestamp", "temperature_2m", "apparent_temperature", "relative_humidity_2m",
  "precipitation", "rain", "wind_speed_10m", "wind_gusts_10m",
  "wind_direction_10m", "surface_pressure", "weather_code",
];
const LABELS = {
  timestamp: "Horodatage", temperature_2m: "Temp. (°C)",
  apparent_temperature: "Ressenti (°C)", relative_humidity_2m: "Humidité (%)",
  precipitation: "Précip. (mm)", rain: "Pluie (mm)",
  wind_speed_10m: "Vent (km/h)", wind_gusts_10m: "Rafales (km/h)",
  wind_direction_10m: "Direction (°)", surface_pressure: "Pression (hPa)",
  weather_code: "Code météo",
};

const headRow = document.getElementById("table-head");
COLUMNS.forEach(col => {
  const th = document.createElement("th");
  th.textContent = LABELS[col];
  th.dataset.col = col;
  th.addEventListener("click", () => sortBy(col));
  headRow.appendChild(th);
});

let sortState = { col: "timestamp", dir: "desc" };
let filterText = "";

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "";
  return v;
}

function renderTable() {
  let rows = currentData();
  if (filterText) {
    rows = rows.filter(r => r.timestamp.includes(filterText));
  }
  rows = rows.slice().sort((a, b) => {
    const av = a[sortState.col], bv = b[sortState.col];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    if (av < bv) return sortState.dir === "asc" ? -1 : 1;
    if (av > bv) return sortState.dir === "asc" ? 1 : -1;
    return 0;
  });

  document.getElementById("row-count").textContent = rows.length + " ligne(s)";

  const body = document.getElementById("table-body");
  body.innerHTML = "";
  const frag = document.createDocumentFragment();
  rows.forEach(r => {
    const tr = document.createElement("tr");
    COLUMNS.forEach(col => {
      const td = document.createElement("td");
      td.textContent = fmt(r[col]);
      tr.appendChild(td);
    });
    frag.appendChild(tr);
  });
  body.appendChild(frag);

  document.querySelectorAll("thead th").forEach(th => {
    th.classList.remove("sorted-asc", "sorted-desc");
    if (th.dataset.col === sortState.col) {
      th.classList.add(sortState.dir === "asc" ? "sorted-asc" : "sorted-desc");
    }
  });
}

function sortBy(col) {
  if (sortState.col === col) {
    sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
  } else {
    sortState = { col, dir: "asc" };
  }
  renderTable();
}

document.getElementById("search").addEventListener("input", e => {
  filterText = e.target.value.trim();
  renderTable();
});

function renderSubtitle() {
  const data = currentData();
  document.getElementById("page-title").textContent = "Météo — " + currentCityName();
  document.getElementById("subtitle").textContent = data.length
    ? data.length + " relevés — du " + data[0].timestamp + " au " + data[data.length - 1].timestamp
    : "Pas encore de données pour cette ville.";
}

function renderAll() {
  renderSubtitle();
  renderCharts();
  renderTable();
}

updateToggleLabel();
renderAll();
</script>
</body>
</html>
"""


def build_html(cities_meta, cities_data):
    html = HTML_TEMPLATE.replace("__CITIES_META_JSON__", json.dumps(cities_meta))
    html = html.replace("__CITIES_DATA_JSON__", json.dumps(cities_data))
    return html


def main():
    cities_meta = [{"slug": c["slug"], "name": c["name"]} for c in CITIES]
    cities_data = {c["slug"]: load_rows(c["slug"]) for c in CITIES}

    html = build_html(cities_meta, cities_data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    total = sum(len(v) for v in cities_data.values())
    print(f"Tableau de bord généré : {OUT_PATH} ({len(CITIES)} villes, {total} relevés au total)")


if __name__ == "__main__":
    main()
