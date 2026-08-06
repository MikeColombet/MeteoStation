export type WeatherRow = {
  timestamp: string;
  temperature_2m: number | null;
  relative_humidity_2m: number | null;
  apparent_temperature: number | null;
  precipitation: number | null;
  rain: number | null;
  weather_code: number | null;
  wind_speed_10m: number | null;
  wind_direction_10m: number | null;
  wind_gusts_10m: number | null;
  surface_pressure: number | null;
};

export type CityMeta = { slug: string; name: string };
