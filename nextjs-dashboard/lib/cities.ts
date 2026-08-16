import type { CityMeta } from "./types";

// Reflète cities.py à la racine de meteo-marcq. Pensez à garder les deux
// synchronisés si vous ajoutez une ville.
export const CITIES: CityMeta[] = [
  { slug: "marcq-en-baroeul", name: "Marcq-en-Barœul (59700)" },
  { slug: "issy-les-moulineaux", name: "Issy-les-Moulineaux (92130)" },
  { slug: "ajaccio", name: "Ajaccio (20000)" },
  { slug: "bordeaux", name: "Bordeaux (33000)" },
  // Département du Nord (59)
  { slug: "lille", name: "Lille (59000)" },
  { slug: "roubaix", name: "Roubaix (59100)" },
  { slug: "tourcoing", name: "Tourcoing (59200)" },
  { slug: "villeneuve-d-ascq", name: "Villeneuve-d'Ascq (59650)" },
  { slug: "dunkerque", name: "Dunkerque (59140)" },
  { slug: "bergues", name: "Bergues (59380)" },
  { slug: "cassel", name: "Cassel (59670)" },
  { slug: "hazebrouck", name: "Hazebrouck (59190)" },
  { slug: "armentieres", name: "Armentières (59280)" },
  { slug: "bailleul", name: "Bailleul (59270)" },
  { slug: "douai", name: "Douai (59500)" },
  { slug: "cambrai", name: "Cambrai (59400)" },
  { slug: "le-cateau-cambresis", name: "Le Cateau-Cambrésis (59360)" },
  { slug: "valenciennes", name: "Valenciennes (59300)" },
  { slug: "denain", name: "Denain (59220)" },
  { slug: "conde-sur-l-escaut", name: "Condé-sur-l'Escaut (59163)" },
  { slug: "maubeuge", name: "Maubeuge (59600)" },
  { slug: "avesnes-sur-helpe", name: "Avesnes-sur-Helpe (59440)" },
  { slug: "fourmies", name: "Fourmies (59610)" },
  { slug: "le-quesnoy", name: "Le Quesnoy (59530)" },
  { slug: "solesmes", name: "Solesmes (59730)" },
];
