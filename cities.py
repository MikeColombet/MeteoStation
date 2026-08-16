"""
Configuration centralisée des villes suivies. Tous les scripts
(fetch_weather.py, seed_history.py, seed_archive.py, plot_weather.py,
generate_dashboard.py) importent CITIES d'ici.

Pour ajouter une ville : géocoder son nom via
https://geocoding-api.open-meteo.com/v1/search?name=<ville>&country=FR
et ajouter une entrée ci-dessous (slug = identifiant de fichier, sans espace
ni accent).
"""

CITIES = [
    {
        "slug": "marcq-en-baroeul",
        "name": "Marcq-en-Barœul (59700)",
        "lat": 50.66667,
        "lon": 3.08333,
    },
    {
        "slug": "issy-les-moulineaux",
        "name": "Issy-les-Moulineaux (92130)",
        "lat": 48.82104,
        "lon": 2.27718,
    },
    {
        "slug": "ajaccio",
        "name": "Ajaccio (20000)",
        "lat": 41.91886,
        "lon": 8.73812,
    },
    {
        "slug": "bordeaux",
        "name": "Bordeaux (33000)",
        "lat": 44.84124,
        "lon": -0.58046,
    },
    # --- Département du Nord (59) : sous-ensemble représentatif de villes
    # réparties sur tout le territoire (métropole lilloise, Flandres,
    # Douaisis, Cambrésis, Valenciennois, Avesnois). ---
    {
        "slug": "lille",
        "name": "Lille (59000)",
        "lat": 50.63391,
        "lon": 3.05512,
    },
    {
        "slug": "roubaix",
        "name": "Roubaix (59100)",
        "lat": 50.69421,
        "lon": 3.17456,
    },
    {
        "slug": "tourcoing",
        "name": "Tourcoing (59200)",
        "lat": 50.72391,
        "lon": 3.16117,
    },
    {
        "slug": "villeneuve-d-ascq",
        "name": "Villeneuve-d'Ascq (59650)",
        "lat": 50.61669,
        "lon": 3.16664,
    },
    {
        "slug": "dunkerque",
        "name": "Dunkerque (59140)",
        "lat": 51.0344,
        "lon": 2.37681,
    },
    {
        "slug": "bergues",
        "name": "Bergues (59380)",
        "lat": 50.96882,
        "lon": 2.43242,
    },
    {
        "slug": "cassel",
        "name": "Cassel (59670)",
        "lat": 50.80109,
        "lon": 2.48527,
    },
    {
        "slug": "hazebrouck",
        "name": "Hazebrouck (59190)",
        "lat": 50.72374,
        "lon": 2.53729,
    },
    {
        "slug": "armentieres",
        "name": "Armentières (59280)",
        "lat": 50.68568,
        "lon": 2.88214,
    },
    {
        "slug": "bailleul",
        "name": "Bailleul (59270)",
        "lat": 50.73592,
        "lon": 2.73594,
    },
    {
        "slug": "douai",
        "name": "Douai (59500)",
        "lat": 50.37069,
        "lon": 3.07922,
    },
    {
        "slug": "cambrai",
        "name": "Cambrai (59400)",
        "lat": 50.17596,
        "lon": 3.23472,
    },
    {
        "slug": "le-cateau-cambresis",
        "name": "Le Cateau-Cambrésis (59360)",
        "lat": 50.1,
        "lon": 3.55,
    },
    {
        "slug": "valenciennes",
        "name": "Valenciennes (59300)",
        "lat": 50.35909,
        "lon": 3.52506,
    },
    {
        "slug": "denain",
        "name": "Denain (59220)",
        "lat": 50.3293,
        "lon": 3.3943,
    },
    {
        "slug": "conde-sur-l-escaut",
        "name": "Condé-sur-l'Escaut (59163)",
        "lat": 50.45436,
        "lon": 3.58884,
    },
    {
        "slug": "maubeuge",
        "name": "Maubeuge (59600)",
        "lat": 50.27875,
        "lon": 3.97267,
    },
    {
        "slug": "avesnes-sur-helpe",
        "name": "Avesnes-sur-Helpe (59440)",
        "lat": 50.12372,
        "lon": 3.9257,
    },
    {
        "slug": "fourmies",
        "name": "Fourmies (59610)",
        "lat": 50.01532,
        "lon": 4.04784,
    },
    {
        "slug": "le-quesnoy",
        "name": "Le Quesnoy (59530)",
        "lat": 50.24797,
        "lon": 3.63656,
    },
    {
        "slug": "solesmes",
        "name": "Solesmes (59730)",
        "lat": 50.18468,
        "lon": 3.49799,
    },
]


def csv_path(script_dir, slug):
    import os
    return os.path.join(script_dir, f"weather_data_{slug}.csv")
