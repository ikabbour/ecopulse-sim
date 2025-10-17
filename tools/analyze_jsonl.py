#!/usr/bin/env python3
"""
Analyse rapide du fichier outbox/raw.energy.jsonl :
- Compte de lignes
- Stats par site (min/avg/max)
- Stats par (site, device)
- Aperçu de 5 messages
"""
import json
from collections import defaultdict, Counter
from statistics import mean
from pathlib import Path

PATH = Path("outbox/raw.energy.jsonl")

def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def main():
    if not PATH.exists():
        print(f"[ERR] Fichier introuvable: {PATH}. Lance d'abord le générateur.")
        return

    rows = list(read_jsonl(PATH))
    print(f"Total messages: {len(rows)}")
    if not rows:
        return

    # Aperçu
    print("\nSample (5 lignes):")
    for r in rows[:5]:
        print(r)

    # Stats par site
    by_site = defaultdict(list)
    for r in rows:
        by_site[r["site_id"]].append(r["value"])

    print("\nStats par site (min/avg/max):")
    for site, vals in by_site.items():
        print(f"- {site:10s} min={min(vals):6.3f}  avg={mean(vals):6.3f}  max={max(vals):6.3f}")

    # Stats par (site, device)
    by_pair = defaultdict(list)
    for r in rows:
        by_pair[(r["site_id"], r["device_id"])].append(r["value"])

    print("\nTop 10 des (site, device) par avg:")
    top = sorted(((k, mean(v)) for k, v in by_pair.items()), key=lambda x: x[1], reverse=True)[:10]
    for (site, device), avgv in top:
        print(f"- {site:10s} / {device:12s} avg={avgv:6.3f}")

    # Comptage par source / unité
    src_count = Counter((r["source"], r["unit"]) for r in rows)
    print("\nComptage par (source, unit):")
    for (src, unit), c in src_count.items():
        print(f"- {src:12s} ({unit}): {c}")

if __name__ == "__main__":
    main()
