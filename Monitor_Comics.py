#!/usr/bin/env python3
"""
Monitor que comprova si han sortit:
  - Saga Integral nº 04 → planetadelibros.com (Planeta Cómic)
  - Monstress Edición de Lujo nº 03 → normaeditorial.com (Norma Editorial)

Monitoritza les pàgines de sèrie reals que ja existeixen.
Quan apareix un nou número, avisa.

INSTAL·LACIÓ:  pip install requests beautifulsoup4
ÚS:
    python monitor_comics.py              # comprova una vegada
    python monitor_comics.py --debug      # mostra els números actuals
    python monitor_comics.py --loop       # comprova cada hora
    python monitor_comics.py --loop --interval 30
"""

import requests, argparse, time, re
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

PRODUCTES = [
    {
        "nom":         "SAGA Integral nº 04 (Planeta Cómic)",
        "web":         "planetadelibros.com",
        "url_serie":   "https://www.planetadelibros.com/serie-saga/18097",
        "paraula":     "saga integral",   # ha d'aparèixer al títol de cada item
        "num_esperat": 4,
    },
    {
        "nom":         "MONSTRESS. Edición de Lujo nº 03 (Norma Editorial)",
        "web":         "normaeditorial.com",
        "url_serie":   "https://www.normaeditorial.com/catalogo/comic-americano/monstress/monstress-edicion-de-lujo/albumes",
        "paraula":     "monstress",
        "num_esperat": 3,
    },
]


def obtenir_items(url, paraula):
    """
    Llegeix la pàgina i retorna llista de (num, titol) dels items
    que contenen la paraula clau.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return None, str(e)

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    # Buscar tots els textos de la pàgina que continguin la paraula
    for tag in soup.find_all(["h2", "h3", "a", "span", "div"]):
        text = tag.get_text(strip=True)
        if not text or len(text) > 100:
            continue
        if paraula.lower() not in text.lower():
            continue

        # Extreure números de 1-2 dígits (no anys)
        nums = [int(n) for n in re.findall(r'\b(\d{1,2})\b', text)]
        if not nums:
            continue

        for num in nums:
            if not any(i["num"] == num and i["titol"] == text for i in items):
                items.append({"num": num, "titol": text})

    return items, None


def comprovar_producte(p, debug=False):
    items, error = obtenir_items(p["url_serie"], p["paraula"])

    if error:
        print(f"     ⚠️  Error: {error}")
        return False

    if debug:
        unics = {i["num"]: i["titol"] for i in items}
        print(f"     → Web    : {p['url_serie']}")
        print(f"     → Trobat : {list(unics.values())[:6]}")
        print(f"     → Nums   : {sorted(unics.keys())}")
        print(f"     → Buscant núm. {p['num_esperat']}...")

    for item in items:
        if item["num"] == p["num_esperat"]:
            print(f"\n{'🚨'*20}")
            print(f"  ✅ TROBAT: {p['nom']}")
            print(f"     Títol : {item['titol']}")
            print(f"     URL   : {p['url_serie']}")
            print(f"{'🚨'*20}")
            print("\a", end="", flush=True)
            return True

    nums_actuals = sorted(set(i["num"] for i in items))
    print(f"     ❌ Encara no. Números publicats: {nums_actuals}")
    return False


def comprovar_tot(debug=False):
    ara = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n[{ara}] Comprovant...")
    print("─" * 60)

    trobats = set()
    for p in PRODUCTES:
        print(f"\n  🔎 {p['nom']}")
        if comprovar_producte(p, debug=debug):
            trobats.add(p["nom"])

    return trobats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true",
                        help="Comprova periòdicament fins trobar-ho tot")
    parser.add_argument("--interval", type=int, default=60,
                        help="Minuts entre comprovacions (default: 60)")
    parser.add_argument("--debug", action="store_true",
                        help="Mostra els números actuals de cada sèrie")
    args = parser.parse_args()

    objectius = {p["nom"] for p in PRODUCTES}

    if not args.loop:
        comprovar_tot(debug=args.debug)
        return

    trobats_total = set()
    print(f"🔍 Mode monitor actiu. Comprovant cada {args.interval} minuts.")
    for p in PRODUCTES:
        print(f"   • {p['nom']}")
    print("   (Ctrl+C per aturar)\n")

    while trobats_total != objectius:
        trobats = comprovar_tot(debug=args.debug)
        trobats_total.update(trobats)

        if trobats_total == objectius:
            print("\n🎉 Tots els productes trobats! Monitor aturat.")
            break

        restants = objectius - trobats_total
        print(f"\n   Esperant: {' | '.join(restants)}")
        print(f"   Propera comprovació en {args.interval} minuts...")
        time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()