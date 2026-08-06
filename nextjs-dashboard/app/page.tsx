import { CITIES } from "@/lib/cities";
import { loadCityData } from "@/lib/data";
import Dashboard from "./dashboard";
import type { WeatherRow } from "@/lib/types";

export default function Home() {
  const citiesData: Record<string, WeatherRow[]> = Object.fromEntries(
    CITIES.map((c) => [c.slug, loadCityData(c.slug)]),
  );

  return <Dashboard citiesMeta={CITIES} citiesData={citiesData} />;
}
