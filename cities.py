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
]


def csv_path(script_dir, slug):
    import os
    return os.path.join(script_dir, f"weather_data_{slug}.csv")
