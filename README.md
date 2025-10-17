🌍 Récapitulatif du projet EcoPulse-Sim
1. Objectif

EcoPulse-Sim est un simulateur de données énergétiques.
Il sert à générer des valeurs de consommation d’électricité, de gaz et de diesel pour plusieurs sites (paris, lyon, berlin, etc.), dans le but d’alimenter un futur pipeline temps réel (Kafka → Airflow → InfluxDB → Grafana).

2. Organisation du dépôt

Le dépôt ecopulse-sim est organisé comme ceci :

ecopulse-sim/
├─ generator/
│  ├─ simple_generator.py       → génère des messages JSON dans un fichier local
│  ├─ requirements.txt          → dépendances Python
├─ data/
│  ├─ site.csv                  → sites et cibles CO₂e
│  ├─ emission_factor.csv       → facteurs d’émission (élec, gaz, diesel)
├─ tools/
│  └─ analyze_jsonl.py          → script d’analyse du fichier JSON généré
├─ .gitignore
└─ README.md

3. Étapes réalisées
Étape 1 — Création du dépôt

Initialisation de Git (git init)

Ajout d’un .gitignore et d’un README.md

Premier commit et push sur GitHub

Étape 2 — Structure du projet

Création des dossiers :

generator pour les scripts Python

data pour les CSV

Ajout d’un commit pour enregistrer la structure

Étape 3 — Données de référence

Deux fichiers CSV ajoutés :

site.csv : contient les sites (paris, lyon, berlin) avec leurs coordonnées et objectif CO₂e.

emission_factor.csv : contient les facteurs d’émission par pays et type d’énergie.

Étape 4 — Générateur simple (sans Kafka)

Script : generator/simple_generator.py

Fonction : simule des consommations et les écrit dans outbox/raw.energy.jsonl.

Paramètres personnalisables via variables d’environnement :

MAX_MESSAGES → nombre de lignes à générer

FREQ_SECONDS → intervalle entre messages

SITES → liste de sites simulés

Exemple de lancement :

$env:MAX_MESSAGES="30"
$env:FREQ_SECONDS="0.5"
py generator\simple_generator.py


Résultat : un fichier JSONL avec 30 lignes (1 message par ligne).

Étape 5 — Analyse locale

Script : tools/analyze_jsonl.py

Fonction : lit le fichier raw.energy.jsonl et calcule des statistiques simples :

Nombre total de messages

Moyenne, min et max par site

Moyenne par couple (site, device)

Comptage par source (électricité, gaz, diesel)

Lancement :

py tools\analyze_jsonl.py

4. Fonctionnement général du simulateur

Chaque message JSON généré a la forme :

{
  "site_id": "paris",
  "device_id": "hvac",
  "source": "electricity",
  "value": 42.7,
  "unit": "kWh",
  "ts": "2025-10-17T12:03:00Z"
}


Les valeurs sont calculées à partir :

d’une valeur moyenne par appareil (baseline),

d’une variation journalière (sinusoïde sur 24h),

d’un effet week-end,

d’un bruit aléatoire,

et de pics aléatoires de surconsommation.

