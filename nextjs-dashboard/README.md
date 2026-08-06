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

## Build + déploiement sur Netlify (site séparé)

Une seule fois :
```bash
netlify login
cd nextjs-dashboard && netlify init   # crée un nouveau site Netlify, distinct de mikemeteostation
```

Ensuite, à chaque publication :
```bash
./deploy.sh
```
(ou manuellement : `npm run build && netlify deploy --prod --dir=out`)

## Ajouter cette version à l'automatisation existante

Le cycle `launchd` actuel (`deploy.sh` à la racine, toutes les 10 min) ne
touche que le dashboard HTML. Pour publier aussi cette version Next.js
automatiquement, il suffirait d'ajouter un appel à
`nextjs-dashboard/deploy.sh` dans le `deploy.sh` racine — pas fait par
défaut car un build Next.js est plus long qu'une génération HTML et
ralentirait le cycle de 10 minutes. À faire sur demande.

## Structure

- `lib/cities.ts` — liste des villes (reflète `cities.py` à la racine)
- `lib/data.ts` — lecture/parsing des CSV au build
- `app/page.tsx` — composant serveur, charge les données
- `app/dashboard.tsx` — composant client, toute l'interactivité (Plotly, table, thème, sélecteur)
