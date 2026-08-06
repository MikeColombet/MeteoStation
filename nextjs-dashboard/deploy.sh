#!/bin/bash
# Build puis publie le dashboard Next.js sur Netlify (site séparé du
# dashboard HTML principal).
# Pré-requis (une fois) : npm install ; netlify login ; netlify init (ici)
set -e
cd "$(dirname "$0")"
npm run build
netlify deploy --prod --dir=out
