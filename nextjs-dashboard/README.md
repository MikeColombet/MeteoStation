# Dashboard météo — version Next.js

Version alternative du dashboard météo (voir `weather_dashboard.html` à la
racine de `meteo-marcq/`), construite avec Next.js (App Router) + Tailwind
CSS + Plotly. Mêmes fonctionnalités : sélecteur de ville, graphiques
température/humidité et vent/précipitation avec zoom et curseur de plage,
mode nuit persistant, tableau de données triable et filtrable.

Ce projet vit à côté du dashboard HTML existant — les deux fonctionnent
indépendamment, sans rien changer au pipeline actuel.

## Comment ça marche

Les données sont lues directement depuis les fichiers `weather_data_<slug>.csv`
du dossier parent (`meteo-marcq/`) **au moment du build** (`next build`),
via un composant serveur (`app/page.tsx` + `lib/data.ts`). Le résultat est
un export 100 % statique (`output: "export"` dans `next.config.ts`) : pas
de serveur Node à héberger, juste des fichiers HTML/JS/CSS à publier.

Concrètement : pour voir des données à jour, il faut relancer un build
(`npm run build`) après chaque mise à jour des CSV, puis redéployer.

## Développement local

```bash
npm install
npm run dev
```
Ouvre http://localhost:3000

## Build

```bash
npm run build
```
Génère l'export statique dans `out/` (`output: "export"` dans
`next.config.ts`). Aucune plateforme de déploiement n'est configurée pour
l'instant — ce dossier `out/` est à publier manuellement où on le souhaite
si besoin.

## Structure

- `lib/cities.ts` — liste des villes (reflète `cities.py` à la racine)
- `lib/data.ts` — lecture/parsing des CSV au build
- `app/page.tsx` — composant serveur, charge les données
- `app/dashboard.tsx` — composant client, toute l'interactivité (Plotly, table, thème, sélecteur)
