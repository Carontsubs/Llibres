```
╔══════════════════════════════════════════════════════════════╗
║         EINES DE BIBLIOTEQUES I COMICS  v1.0                 ║
║                    by Claude & User                          ║
╚══════════════════════════════════════════════════════════════╝

  C:\> dir

  ALADI.PY    Comprova disponibilitat al Masnou
  MONITOR_COMICS.PY         Monitora novetats editorials
  LLIBRES.CSV               Llista de llibres a comprovar
  README.TXT                Aquest fitxer

══════════════════════════════════════════════════════════════════

  C:\> type ALADI.TXT

  ┌─────────────────────────────────────────────────────────┐
  │  ALADI.PY                                 │
  │  Comprova disponibilitat al catàleg Aladí               │
  │  (aladi.diba.cat) - Xarxa Biblioteques Municipals BCN   │
  └─────────────────────────────────────────────────────────┘

  COM FUNCIONA:
  ┌────────────────────────────────────────────────────────────┐
  │  PAS 1 ──► Cerca TITOL a la biblioteca del MASNOU          │
  │      │                                                     │
  │      └─► Si no troba ──► PAS 2                            │
  │                                                            │
  │  PAS 2 ──► Cerca TITOL a TOTA LA XARXA                    │
  │      │                                                     │
  │      └─► Si no troba ──► PAS 3                            │
  │                                                            │
  │  PAS 3 ──► Cerca AUTOR i guarda bibliografia              │
  │            a NO_TROBATS.TXT                                │
  └────────────────────────────────────────────────────────────┘

  INSTAL·LACIO:
    C:\> pip install selenium webdriver-manager beautifulsoup4

  FORMAT LLIBRES.CSV:
    titol,autor
    El nom de la rosa,Umberto Eco
    Dune,Frank Herbert

  US:
    C:\> python ALADI.py llibres.csv
    C:\> python ALADI.py llibres.csv --visible
    C:\> python ALADI.py llibres.csv --sortida out.csv

  FITXERS GENERATS:
    RESULTAT.CSV      ── Localitzacio, signatura i estat
    NO_TROBATS.TXT    ── Bibliografia dels autors no trobats

  ESTAT EXEMPLARS:
    [OK]  Disponible
    [--]  Reservat / Prestat / Venç el DD-MM-AA
    [??]  Estat desconegut

══════════════════════════════════════════════════════════════════

  C:\> type MONITOR_COMICS.TXT

  ┌─────────────────────────────────────────────────────────┐
  │  MONITOR_COMICS.PY                                      │
  │  Monitora novetats editorials de còmic                  │
  └─────────────────────────────────────────────────────────┘

  SERIES MONITORITZADES:
  ┌────────────────────────────────┬──────────────┬─────────┐
  │ SERIE                          │ EDITORIAL    │ NUM.ESP.│
  ├────────────────────────────────┼──────────────┼─────────┤
  │ Saga Integral                  │ Planeta Comic│   04    │
  │ Monstress Edicion de Lujo      │ Norma Ed.    │   03    │
  └────────────────────────────────┴──────────────┴─────────┘

  INSTAL·LACIO:
    C:\> pip install requests beautifulsoup4

  US:
    C:\> python monitor_comics.py
    C:\> python monitor_comics.py --debug
    C:\> python monitor_comics.py --loop
    C:\> python monitor_comics.py --loop --interval 30

  QUAN ES DETECTA UN NOU VOLUM:
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    !!!!!!!!!!! ALERTA !!!!!!!!!!!!!!!!!!!!!!!!
    !!!   NOU VOLUM DETECTAT A LA VENDA     !!!
    !!!!!!!!!!! ALERTA !!!!!!!!!!!!!!!!!!!!!!!!
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

══════════════════════════════════════════════════════════════════

  C:\> _
```