import fs from "node:fs";
import path from "node:path";
import type { WeatherRow } from "./types";

const NUMERIC_FIELDS = [
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
] as const;

// Par défaut, les CSV sont lus dans le dossier parent (meteo-marcq/), car ce
// projet Next.js vit dans meteo-marcq/nextjs-dashboard/. Surchargeable via
// WEATHER_DATA_DIR (utile pour les tests).
const DATA_DIR = process.env.WEATHER_DATA_DIR
  ? path.resolve(process.env.WEATHER_DATA_DIR)
  : path.join(process.cwd(), "..");

function parseCsv(text: string): Record<string, string>[] {
  const lines = text.trim().split("\n");
  if (lines.length === 0) return [];
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row: Record<string, string> = {};
    headers.forEach((h, i) => {
      row[h] = values[i] ?? "";
    });
    return row;
  });
}

function toNumber(v: string | undefined): number | null {
  if (v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isNaN(n) ? null : n;
}

export function loadCityData(slug: string): WeatherRow[] {
  const filePath = path.join(DATA_DIR, `weather_data_${slug}.csv`);
  if (!fs.existsSync(filePath)) return [];

  const text = fs.readFileSync(filePath, "utf-8");
  const rows = parseCsv(text);

  const data: WeatherRow[] = rows
    .filter((r) => r.timestamp)
    .map((r) => {
      const row = { timestamp: r.timestamp } as WeatherRow;
      for (const field of NUMERIC_FIELDS) {
        row[field] = toNumber(r[field]);
      }
      return row;
    });

  data.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  return data;
}
