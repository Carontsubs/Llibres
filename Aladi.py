#!/usr/bin/env python3
"""
Flux:
  1. Cerca TÍTOL al MASNOU + comprova que coincideix
  2. Si no → cerca TÍTOL a TOTA LA XARXA + comprova que coincideix
  3. Si no → cerca AUTOR a tota la xarxa i llista tots els seus títols

FORMAT CSV:
    titol,autor
    Mating in Captivity,Esther Perel
    1984,Orwell

ÚS:
    python comprova_biblioteca.py llibres.csv
    python comprova_biblioteca.py llibres.csv --visible
"""

import csv, argparse, re, time, unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASE_URL     = "https://aladi.diba.cat"
SCOPE_MASNOU = "97"
SCOPE_XARXA  = "171"


def norm(text):
    if not text: return ""
    t = unicodedata.normalize('NFD', text).encode('ascii','ignore').decode('utf-8')
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', t).lower()).strip()


def coincideix(buscat, trobat):
    """Les paraules principals del títol buscat han d'estar al trobat."""
    nb, nt = norm(buscat), norm(trobat)
    if nb in nt or nt in nb:
        return True
    paraules = [p for p in nb.split() if len(p) > 3]
    if not paraules:
        return False
    return sum(1 for p in paraules if p in nt) / len(paraules) >= 0.75


def iniciar_driver(visible=False):
    opts = Options()
    if not visible: opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)


def fer_cerca(driver, query, searchtype, scope):
    driver.get(f"{BASE_URL}/search*cat/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searcharg")))
    Select(driver.find_element(By.NAME, "searchtype")).select_by_value(searchtype)
    camp = driver.find_element(By.ID, "searcharg")
    camp.clear()
    camp.send_keys(query)
    Select(driver.find_element(By.NAME, "searchscope")).select_by_value(scope)
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)


def links_frameset(soup):
    vistos, links = set(), []
    for a in soup.find_all("a", href=re.compile(r"/frameset")):
        titol = a.get_text(strip=True)
        href  = a.get("href", "")
        if titol and titol != "+ info" and href and href not in vistos:
            vistos.add(href)
            links.append((titol, BASE_URL + href))
    return links


def exemplars_de_soup(soup):
    resultats = []
    taula = soup.find("table", class_="bibItems")
    if not taula: return resultats
    for row in taula.find_all("tr", class_="bibItemsEntry"):
        tds = row.find_all("td")
        if len(tds) < 3: continue
        resultats.append({
            "localitzacio": tds[0].get_text(strip=True),
            "signatura":    tds[1].get_text(strip=True),
            "estat":        tds[2].get_text(strip=True),
            "notes":        tds[3].get_text(strip=True) if len(tds) > 3 else "",
        })
    return resultats


def cerca_titol(driver, titol_buscat, scope):
    """
    Cerca el títol en el scope donat.
    Comprova que el títol trobat coincideix amb el buscat.
    Retorna (titol_trobat, [exemplars]) o None.
    """
    fer_cerca(driver, titol_buscat, searchtype="t", scope=scope)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Fitxa única directa
    if soup.find("table", class_="bibItems"):
        td = soup.find("td", class_="bibInfoData")
        titol_t = td.get_text(strip=True).split(" / ")[0] if td else ""
        if coincideix(titol_buscat, titol_t):
            return titol_t, exemplars_de_soup(soup)
        return None

    # Llista → buscar el primer que coincideix
    for titol_t, url in links_frameset(soup):
        if not coincideix(titol_buscat, titol_t):
            continue
        driver.get(url)
        time.sleep(1.2)
        fitxa = BeautifulSoup(driver.page_source, "html.parser")
        exemplars = exemplars_de_soup(fitxa)
        if exemplars:
            return titol_t, exemplars

    return None


def bibliografia_autor(driver, autor):
    """Retorna tots els títols de l'autor a tota la xarxa."""
    parts = autor.strip().split()
    variants = [autor]
    if len(parts) >= 2:
        variants = [f"{parts[-1]}, {' '.join(parts[:-1])}", autor]

    for variant in variants:
        fer_cerca(driver, variant, searchtype="a", scope=SCOPE_XARXA)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        if soup.find("table", class_="bibItems"):
            td = soup.find("td", class_="bibInfoData")
            if td:
                return [td.get_text(strip=True).split(" / ")[0]]

        links = links_frameset(soup)
        if links:
            return [t for t, _ in links]

    return []


def icona_estat(estat):
    e = estat.lower()
    if "disponible" in e: return "✅", "Sí"
    if any(x in e for x in ["reservat","prestat","venç","reserva"]): return "🔴", "No"
    return "❓", "?"


def llegir_csv(path):
    llibres = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        mostra = f.read(1024); f.seek(0)
        delim = ';' if mostra.count(';') > mostra.count(',') else ','
        for fila in csv.DictReader(f, delimiter=delim):
            fila  = {k.lower().strip(): v.strip() for k, v in fila.items()}
            titol = fila.get("titol") or fila.get("titulo") or fila.get("title") or ""
            autor = fila.get("autor") or fila.get("author") or ""
            if titol: llibres.append((titol, autor))
    return llibres


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fitxer")
    parser.add_argument("--visible", action="store_true")
    parser.add_argument("--sortida", default="resultat.csv")
    args = parser.parse_args()

    llibres = llegir_csv(args.fitxer)
    print(f"\n📚 {len(llibres)} llibre(s) a comprovar\n{'─'*60}")

    driver     = iniciar_driver(args.visible)
    files_csv  = []
    no_trobats = []

    try:
        for i, (titol, autor) in enumerate(llibres, 1):
            print(f"\n[{i}/{len(llibres)}] «{titol}»  ({autor})")

            # ── PAS 1: títol al MASNOU ─────────────────────────────────
            resultat = cerca_titol(driver, titol, SCOPE_MASNOU)
            if resultat:
                titol_t, exemplars = resultat
                print(f"  📍 Trobat al Masnou: «{titol_t}»")
                for ex in exemplars:
                    ico, disp = icona_estat(ex["estat"])
                    print(f"  {ico} {ex['signatura']}  |  {ex['estat']}"
                          + (f"  [{ex['notes']}]" if ex["notes"] else ""))
                    files_csv.append({
                        "titol_buscat": titol, "autor_buscat": autor,
                        "titol_trobat": titol_t, "on": "Masnou",
                        "localitzacio": ex["localitzacio"],
                        "signatura": ex["signatura"],
                        "estat": ex["estat"], "notes": ex["notes"],
                        "disponible": disp,
                    })
                continue

            # ── PAS 2: títol a TOTA LA XARXA ──────────────────────────
            print(f"  ↳ No al Masnou, cercant a tota la xarxa...")
            resultat = cerca_titol(driver, titol, SCOPE_XARXA)
            if resultat:
                titol_t, exemplars = resultat
                print(f"  🌐 Trobat a la xarxa: «{titol_t}»")
                for ex in exemplars[:5]:
                    ico, disp = icona_estat(ex["estat"])
                    print(f"  {ico} {ex['localitzacio']}  |  {ex['signatura']}  |  {ex['estat']}")
                    files_csv.append({
                        "titol_buscat": titol, "autor_buscat": autor,
                        "titol_trobat": titol_t, "on": "Xarxa (no Masnou)",
                        "localitzacio": ex["localitzacio"],
                        "signatura": ex["signatura"],
                        "estat": ex["estat"], "notes": ex["notes"],
                        "disponible": disp,
                    })
                continue

            # ── PAS 3: bibliografia de l'autor ─────────────────────────
            print(f"  ↳ No trobat, cercant bibliografia de «{autor}»...")
            titols_autor = bibliografia_autor(driver, autor) if autor else []
            print(f"  ❌ No trobat. {len(titols_autor)} títols de l'autor a la xarxa.")
            no_trobats.append((titol, autor, titols_autor))
            files_csv.append({
                "titol_buscat": titol, "autor_buscat": autor,
                "titol_trobat": "", "on": "No trobat",
                "localitzacio": "", "signatura": "",
                "estat": "No trobat", "notes": "", "disponible": "No",
            })

    finally:
        driver.quit()

    # ── CSV ────────────────────────────────────────────────────────────
    camps = ["titol_buscat","autor_buscat","titol_trobat","on",
             "localitzacio","signatura","estat","notes","disponible"]
    with open(args.sortida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=camps)
        w.writeheader()
        w.writerows(files_csv)

    # ── TXT no trobats ─────────────────────────────────────────────────
    if no_trobats:
        with open("no_trobats.txt", "w", encoding="utf-8") as f:
            f.write("LLIBRES NO TROBATS\n" + "="*50 + "\n\n")
            for titol_b, autor_b, tots in no_trobats:
                f.write(f"BUSCAT : «{titol_b}»\nAUTOR  : {autor_b}\n" + "-"*40 + "\n")
                if tots:
                    f.write(f"Títols de «{autor_b}» a la xarxa:\n")
                    for t in tots: f.write(f"  • {t}\n")
                else:
                    f.write("  Cap títol trobat a la xarxa.\n")
                f.write("\n")

    # ── Resum ──────────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print(f"  Al Masnou       : {sum(1 for r in files_csv if r['on']=='Masnou')}")
    print(f"  A la xarxa      : {sum(1 for r in files_csv if 'Xarxa' in r['on'])}")
    print(f"  No trobats      : {sum(1 for r in files_csv if r['on']=='No trobat')}")
    print(f"  Disponibles ara : {sum(1 for r in files_csv if r['disponible']=='Sí')}")
    print(f"  CSV             : {args.sortida}")
    if no_trobats: print(f"  No trobats TXT  : no_trobats.txt")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()