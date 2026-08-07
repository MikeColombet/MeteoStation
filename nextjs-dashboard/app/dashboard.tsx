"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import type { CityMeta, WeatherRow } from "@/lib/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

type Props = {
  citiesMeta: CityMeta[];
  citiesData: Record<string, WeatherRow[]>;
};

const THEME_KEY = "meteo-nextjs-theme";
const CITY_KEY = "meteo-nextjs-city";

const COLUMNS: { key: keyof WeatherRow; label: string }[] = [
  { key: "timestamp", label: "Horodatage" },
  { key: "temperature_2m", label: "Temp. (°C)" },
  { key: "apparent_temperature", label: "Ressenti (°C)" },
  { key: "relative_humidity_2m", label: "Humidité (%)" },
  { key: "precipitation", label: "Précip. (mm)" },
  { key: "rain", label: "Pluie (mm)" },
  { key: "wind_speed_10m", label: "Vent (km/h)" },
  { key: "wind_gusts_10m", label: "Rafales (km/h)" },
  { key: "wind_direction_10m", label: "Direction (°)" },
  { key: "surface_pressure", label: "Pression (hPa)" },
  { key: "weather_code", label: "Code météo" },
];

// Horodatage "YYYY-MM-DDTHH:MM" → ms, traité comme UTC pour être
// indépendant du fuseau du visiteur (on ne calcule que des durées
// relatives, jamais une heure absolue affichée).
function parseTs(ts: string): number {
  const [datePart, timePart] = ts.split("T");
  const [y, mo, d] = datePart.split("-").map(Number);
  const [h, mi] = timePart.split(":").map(Number);
  return Date.UTC(y, mo - 1, d, h, mi);
}

// Moyenne mobile sur une fenêtre glissante de 24h (en temps réel, pas en
// nombre de points, pour rester correcte même avec un échantillonnage
// irrégulier : historique horaire, relevés 15 min, etc.)
function movingAverage24h(
  data: WeatherRow[],
  key: keyof WeatherRow,
): (number | null)[] {
  const WINDOW_MS = 24 * 60 * 60 * 1000;
  const times = data.map((d) => parseTs(d.timestamp));
  const result: (number | null)[] = new Array(data.length).fill(null);
  let sum = 0;
  let count = 0;
  let left = 0;
  for (let i = 0; i < data.length; i++) {
    const v = data[i][key];
    if (typeof v === "number") {
      sum += v;
      count++;
    }
    while (times[left] < times[i] - WINDOW_MS) {
      const lv = data[left][key];
      if (typeof lv === "number") {
        sum -= lv;
        count--;
      }
      left++;
    }
    result[i] = count > 0 ? sum / count : null;
  }
  return result;
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

function themeColors(dark: boolean) {
  return dark
    ? {
        paper: "#1e2126",
        plot: "#1e2126",
        font: "#e6e6e6",
        grid: "#33373f",
        rsBg: "#2b2f37",
        rsActive: "#3a3f47",
      }
    : {
        paper: "#ffffff",
        plot: "#ffffff",
        font: "#2c2c2c",
        grid: "#eeeeee",
        rsBg: "#f0f0f0",
        rsActive: "#d8d8d8",
      };
}

export default function Dashboard({ citiesMeta, citiesData }: Props) {
  const [currentSlug, setCurrentSlug] = useState<string>(
    citiesMeta[0]?.slug ?? "",
  );
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [filterText, setFilterText] = useState("");
  const [sortKey, setSortKey] = useState<keyof WeatherRow>("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // Lecture des préférences stockées, une fois côté client seulement
  // (évite tout flash de mauvais thème/ville au premier rendu).
  useEffect(() => {
    const storedCity = localStorage.getItem(CITY_KEY);
    if (storedCity && citiesData[storedCity]) setCurrentSlug(storedCity);

    const storedTheme = localStorage.getItem(THEME_KEY);
    const dark = storedTheme
      ? storedTheme === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    setIsDark(dark);
    setMounted(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!mounted) return;
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
  }, [isDark, mounted]);

  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem(CITY_KEY, currentSlug);
  }, [currentSlug, mounted]);

  const data = citiesData[currentSlug] ?? [];
  const cityName =
    citiesMeta.find((c) => c.slug === currentSlug)?.name ?? currentSlug;
  const colors = themeColors(isDark);

  const timestamps = useMemo(() => data.map((d) => d.timestamp), [data]);
  const series = (key: keyof WeatherRow) => data.map((d) => d[key]);

  const tempTraces = useMemo(
    () => [
      {
        x: timestamps,
        y: series("temperature_2m"),
        name: "Température (°C)",
        mode: "lines",
        line: { color: "#c0392b", width: 1.5 },
      },
      {
        x: timestamps,
        y: series("apparent_temperature"),
        name: "Ressenti (°C)",
        mode: "lines",
        line: { color: "#b8860b", width: 1.3 },
      },
      {
        x: timestamps,
        y: movingAverage24h(data, "temperature_2m"),
        name: "Moyenne mobile 24h (°C)",
        mode: "lines",
        line: { color: "#34495e", width: 2, dash: "dash" },
      },
      {
        x: timestamps,
        y: series("relative_humidity_2m"),
        name: "Humidité (%)",
        mode: "lines",
        line: { color: "#2980b9", width: 1.1 },
        yaxis: "y2",
        opacity: 0.6,
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [data],
  );

  const windTraces = useMemo(
    () => [
      {
        x: timestamps,
        y: series("wind_speed_10m"),
        name: "Vent (km/h)",
        mode: "lines",
        line: { color: "#27ae60", width: 1.3 },
      },
      {
        x: timestamps,
        y: series("wind_gusts_10m"),
        name: "Rafales (km/h)",
        mode: "lines",
        line: { color: "#7f8c8d", width: 1, dash: "dot" },
      },
      {
        x: timestamps,
        y: series("precipitation"),
        name: "Précipitation (mm)",
        type: "bar",
        marker: { color: "#2980b9" },
        yaxis: "y2",
        opacity: 0.5,
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [data],
  );

  const tempLayout = {
    margin: { t: 10, r: 60, b: 80, l: 50 },
    legend: {
      orientation: "h",
      y: -0.35,
      yanchor: "top",
      x: 0.5,
      xanchor: "center",
      font: { color: colors.font },
    },
    paper_bgcolor: colors.paper,
    plot_bgcolor: colors.plot,
    font: { color: colors.font },
    xaxis: {
      gridcolor: colors.grid,
      zerolinecolor: colors.grid,
      rangeslider: { visible: true, thickness: 0.08 },
      rangeselector: {
        bgcolor: colors.rsBg,
        activecolor: colors.rsActive,
        bordercolor: colors.grid,
        font: { color: colors.font },
        buttons: rangeButtons(),
      },
    },
    yaxis: {
      title: { text: "Température (°C)" },
      gridcolor: colors.grid,
      zerolinecolor: colors.grid,
    },
    yaxis2: {
      title: { text: "Humidité (%)" },
      overlaying: "y",
      side: "right",
      range: [0, 100],
      gridcolor: colors.grid,
    },
  };

  const windLayout = {
    margin: { t: 10, r: 60, b: 70, l: 50 },
    legend: {
      orientation: "h",
      y: -0.2,
      yanchor: "top",
      x: 0.5,
      xanchor: "center",
      font: { color: colors.font },
    },
    paper_bgcolor: colors.paper,
    plot_bgcolor: colors.plot,
    font: { color: colors.font },
    xaxis: {
      gridcolor: colors.grid,
      zerolinecolor: colors.grid,
      rangeselector: {
        bgcolor: colors.rsBg,
        activecolor: colors.rsActive,
        bordercolor: colors.grid,
        font: { color: colors.font },
        buttons: rangeButtons(),
      },
    },
    yaxis: {
      title: { text: "Vent (km/h)" },
      gridcolor: colors.grid,
      zerolinecolor: colors.grid,
    },
    yaxis2: {
      title: { text: "Précipitation (mm)" },
      overlaying: "y",
      side: "right",
      gridcolor: colors.grid,
    },
  };

  const filteredSorted = useMemo(() => {
    let rows = data;
    if (filterText) {
      rows = rows.filter((r) => r.timestamp.includes(filterText));
    }
    return [...rows].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (av === null || av === undefined) return 1;
      if (bv === null || bv === undefined) return -1;
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
  }, [data, filterText, sortKey, sortDir]);

  function sortBy(key: keyof WeatherRow) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-1">
        <div>
          <h1 className="text-xl font-semibold">Météo — {cityName}</h1>
          <p className="text-sm text-muted">
            {data.length
              ? `${data.length} relevés — du ${data[0].timestamp} au ${
                  data[data.length - 1].timestamp
                }`
              : "Pas encore de données pour cette ville."}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={currentSlug}
            onChange={(e) => setCurrentSlug(e.target.value)}
            className="border border-border bg-card text-foreground rounded-lg px-3 py-1.5 text-sm cursor-pointer"
          >
            {citiesMeta.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => setIsDark((d) => !d)}
            className="border border-border bg-card text-foreground rounded-full px-4 py-1.5 text-sm cursor-pointer hover:opacity-80"
          >
            {isDark ? "☀️ Mode jour" : "🌙 Mode nuit"}
          </button>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 mt-5 mb-5">
        <h2 className="text-sm font-semibold mb-2">Température & humidité</h2>
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        <Plot
          data={tempTraces as any}
          layout={tempLayout as any}
          style={{ width: "100%", height: "420px" }}
          useResizeHandler
          config={{ responsive: true }}
        />
      </div>

      <div className="bg-card border border-border rounded-xl p-4 mb-5">
        <h2 className="text-sm font-semibold mb-2">Vent & précipitation</h2>
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        <Plot
          data={windTraces as any}
          layout={windLayout as any}
          style={{ width: "100%", height: "380px" }}
          useResizeHandler
          config={{ responsive: true }}
        />
      </div>

      <div className="bg-card border border-border rounded-xl p-4">
        <h2 className="text-sm font-semibold mb-2">Données brutes</h2>
        <div className="flex flex-wrap items-center gap-3 mb-2.5">
          <input
            type="text"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Filtrer (ex: 2026-08-05, ou 2026-08-05T20)"
            className="border border-border bg-background text-foreground rounded-md px-2.5 py-1.5 text-sm min-w-[220px]"
          />
          <span className="text-xs text-muted">
            {filteredSorted.length} ligne(s)
          </span>
        </div>
        <div className="max-h-[480px] overflow-auto border border-border rounded-lg">
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                {COLUMNS.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => sortBy(col.key)}
                    className="sticky top-0 bg-thead border-b border-border text-left px-2.5 py-2 cursor-pointer select-none whitespace-nowrap hover:bg-thead-hover"
                  >
                    {col.label}
                    {sortKey === col.key ? (sortDir === "asc" ? " ▲" : " ▼") : ""}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredSorted.map((row, i) => (
                <tr key={row.timestamp + i} className="hover:bg-row-hover">
                  {COLUMNS.map((col) => (
                    <td
                      key={col.key}
                      className="px-2.5 py-1.5 border-b border-row-border whitespace-nowrap"
                    >
                      {row[col.key] ?? ""}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
