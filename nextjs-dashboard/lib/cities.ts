import type { CityMeta } from "./types";

// Reflète cities.py à la racine de meteo-marcq. Pensez à garder les deux
// synchronisés si vous ajoutez une ville.
export const CITIES: CityMeta[] = [
  { slug: "marcq-en-baroeul", name: "Marcq-en-Barœul (59700)" },
  { slug: "issy-les-moulineaux", name: "Issy-les-Moulineaux (92130)" },
  { slug: "ajaccio", name: "Ajaccio (20000)" },
  { slug: "bordeaux", name: "Bordeaux (33000)" },
];
