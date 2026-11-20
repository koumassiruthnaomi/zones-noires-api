from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

app = FastAPI(
    title="API Zones Noires - S2R",
    description="Détection et alerte des zones accidentogènes à Fès",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SEUIL_ZONE_NOIRE = 5
RAYON_CLUSTER_M  = 50
RAYON_ALERTE_M   = 300

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def calculer_zones_noires():
    df = pd.read_csv("accidents_fes.csv")
    coords = np.radians(df[["latitude", "longitude"]].values)

    db = DBSCAN(
        eps=RAYON_CLUSTER_M / 111000,
        min_samples=SEUIL_ZONE_NOIRE,
        metric="haversine"
    ).fit(coords)

    df["cluster"] = db.labels_
    zones = []

    for label in set(db.labels_):
        if label == -1:
            continue
        cluster = df[df["cluster"] == label]
        zones.append({
            "id":           int(label),
            "zone_nom":     cluster["zone_nom"].mode()[0],
            "latitude":     round(float(cluster["latitude"].mean()), 6),
            "longitude":    round(float(cluster["longitude"].mean()), 6),
            "nb_accidents": int(len(cluster)),
            "gravite_predominante": cluster["gravite"].mode()[0],
        })

    return sorted(zones, key=lambda x: x["nb_accidents"], reverse=True)

ZONES_NOIRES = calculer_zones_noires()

@app.get("/", response_class=HTMLResponse)
def accueil():
    rows = ""
    for zone in ZONES_NOIRES:
        rows += f"""
        <tr>
            <td>{zone['id']}</td>
            <td>{zone['zone_nom']}</td>
            <td>{zone['latitude']}</td>
            <td>{zone['longitude']}</td>
            <td><span class="badge bg-danger">{zone['nb_accidents']}</span></td>
            <td>{zone['gravite_predominante']}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>API Zones Noires S2R</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="text-center text-danger mb-4">🚦 Zones Noires détectées : {len(ZONES_NOIRES)}</h1>
            <table class="table table-striped table-hover shadow">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Zone</th>
                        <th>Latitude</th>
                        <th>Longitude</th>
                        <th>Accidents</th>
                        <th>Gravité dominante</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p class="text-center text-muted mt-3">
                Dernière mise à jour : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>
            <div class="text-center">
                <a href="/docs" class="btn btn-primary">📖 Tester l’API (Swagger)</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/zones-noires")
def toutes_les_zones():
    return JSONResponse({"total": len(ZONES_NOIRES), "zones": ZONES_NOIRES})

    
