import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ── Zones accidentogènes réelles de Fès ──────────────────────────────────────
ZONES_DANGEREUSES = [
    {"nom": "Rond-point Bensouda",     "lat": 34.0131, "lng": -5.0078, "poids": 8},
    {"nom": "Avenue Hassan II",         "lat": 34.0333, "lng": -5.0003, "poids": 7},
    {"nom": "Carrefour Sidi Brahim",   "lat": 34.0412, "lng": -4.9998, "poids": 9},
    {"nom": "Route de Meknès (N6)",    "lat": 34.0550, "lng": -5.0300, "poids": 6},
    {"nom": "Bd Mohammed V centre",    "lat": 34.0650, "lng": -4.9900, "poids": 7},
    {"nom": "Aéroport Fès-Saïss",      "lat": 33.9272, "lng": -4.9778, "poids": 5},
    {"nom": "Route de Sefrou",         "lat": 33.9900, "lng": -4.9700, "poids": 6},
    {"nom": "Quartier Narjiss",        "lat": 34.0200, "lng": -5.0150, "poids": 5},
    {"nom": "Rond-point Atlas",        "lat": 34.0450, "lng": -5.0050, "poids": 8},
    {"nom": "Route d'Immouzer",        "lat": 34.0750, "lng": -4.9600, "poids": 4},
]

# ── Zones normales (peu ou pas d'accidents) ───────────────────────────────────
ZONES_NORMALES = [
    {"nom": "Quartier Agdal",          "lat": 34.0100, "lng": -5.0400, "poids": 1},
    {"nom": "Mellah Fès el-Bali",      "lat": 34.0620, "lng": -4.9750, "poids": 1},
    {"nom": "Université USMBA",        "lat": 34.0230, "lng": -5.0280, "poids": 1},
    {"nom": "Quartier Saada",          "lat": 34.0050, "lng": -5.0100, "poids": 1},
    {"nom": "Zone industrielle Nord",  "lat": 34.0800, "lng": -5.0200, "poids": 1},
]

TOUTES_ZONES = ZONES_DANGEREUSES + ZONES_NORMALES
poids_total  = [z["poids"] for z in TOUTES_ZONES]

# ── Génération des accidents ───────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

accidents = []
date_debut = datetime(2023, 1, 1)

for i in range(500):
    # Choisir une zone (les dangereuses sont tirées plus souvent)
    zone = random.choices(TOUTES_ZONES, weights=poids_total, k=1)[0]

    # Disperser légèrement autour du centre (±100m ≈ 0.0009°)
    lat = zone["lat"] + np.random.normal(0, 0.0009)
    lng = zone["lng"] + np.random.normal(0, 0.0009)

    # Date/heure aléatoire sur 18 mois
    timestamp = date_debut + timedelta(
        days=random.randint(0, 540),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    # Gravité de l'accident
    gravite = random.choices(
        ["léger", "modéré", "grave"],
        weights=[60, 30, 10]
    )[0]

    accidents.append({
        "id":            i + 1,
        "latitude":      round(lat, 6),
        "longitude":     round(lng, 6),
        "zone_nom":      zone["nom"],
        "timestamp":     timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "gravite":       gravite,
        "vitesse_kmh":   random.randint(30, 120),
        "meteo":         random.choice(["ensoleillé", "nuageux", "pluie", "brouillard"]),
    })

# ── Sauvegarder ───────────────────────────────────────────────────────────────
df = pd.DataFrame(accidents)
df.to_csv("accidents_fes.csv", index=False, encoding="utf-8-sig")

print(f"✅ {len(df)} accidents générés → accidents_fes.csv")
print(f"\n📊 Répartition par zone :")
print(df["zone_nom"].value_counts().to_string())
print(f"\n🔴 Gravité :")
print(df["gravite"].value_counts().to_string())