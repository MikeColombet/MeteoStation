#!/bin/bash
# Récupère les données, régénère le dashboard et le publie sur Netlify.
# Appelé automatiquement par com.mike.meteo.fetch.plist (launchd), toutes
# les 10 minutes.
#
# Pré-requis (une seule fois) :
#   npm install -g netlify-cli
#   netlify login
#   cd ~/meteo-marcq && netlify init   (ou "netlify link" si le site existe déjà)
set -e
cd "$(dirname "$0")"

echo "Récupération des données..."
python3 fetch_weather.py

echo "Comblement d'un éventuel trou (Mac éteint, etc.)..."
python3 seed_history.py

echo "Régénération du dashboard..."
python3 generate_dashboard.py
cp weather_dashboard.html site/index.html

echo "Déploiement sur Netlify..."
netlify deploy --prod --dir=site
