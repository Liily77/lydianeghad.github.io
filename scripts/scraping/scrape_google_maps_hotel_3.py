# scripts/scraping/scrape_google_maps_hotel_3.py
# --- Hôtel Littéraire Marcel Aymé (BW Premier Collection) ---
# Scraping Google Reviews en mode DELTA + TOP-UP récent
# Ajouts : journal d’ingestion CSV (+ JSONL optionnel) et récapitulatif de fin de run

import csv, os, re, time, random, json
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import suppress
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---- Delta state (nécessite scripts/scraping/ingestion_state.py) ----
from scripts.scraping.ingestion_state import get_prev_total, set_prev_total

# --------- CONFIG ----------
HOTEL_KEY  = "BW_Litteraire_Marcel_Ayme"
HOTEL_NAME = "Hôtel Littéraire Marcel Aymé, BW Premier Collection"
URL = ("https://www.google.com/maps/place/H%C3%B4tel+Litt%C3%A9raire+Marcel+Aym%C3%A9,+BW+Premier+Collection/@48.8864947,2.3330798,470m/"
       "data=!3m1!1e3!4m12!3m11!1s0x47e66e5aaa9c27e7:0x4041da69c3028e9a!5m3!1s2025-08-19!4m1!1i2!8m2!3d48.8864912!4d2.3356547!9m1!1b1!"
       "16s%2Fg%2F1tfzg1sp?entry=ttu")

# Fichier de sortie (aligné avec le pipeline)
OUT_PATH = Path("data/raw/avis_google_BW_Litteraire_Marcel_Ayme.csv")

# Journal d’ingestion
STATE_DIR       = Path("data/state")
INGESTION_CSV   = STATE_DIR / "ingestion_runs.csv"
INGESTION_JSONL = STATE_DIR / "ingestion_runs.jsonl"
WRITE_JSONL     = True  # passe à False si tu ne veux pas le miroir JSONL

# Paramètres scraping
HEADLESS = True
IDLE_ROUNDS_LIMIT = 10
SCROLLS_PER_ROUND = 10
SCROLL_STEP_PX    = 3000
SCROLL_PAUSE      = (0.08, 0.16)  # secondes

# Nombre d'avis récents à prendre même si delta=0 (anti-trou)
RECENT_TOPUP = 60

def human_sleep(a,b): time.sleep(random.uniform(a,b))

def clean_date(s:str)->str:
    if not s: return ""
    return re.sub(r"\s*sur\s+(Google|Tripadvisor).*", "", s, flags=re.I).strip()

def accept_google_consent(page):
    with suppress(Exception):
        page.wait_for_timeout(350)
        for text in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
            btn = page.locator(f'button:has-text("{text}")')
            if btn.count():
                btn.first.click(timeout=1200)
                page.wait_for_timeout(250)
                return
        for fr in page.frames:
            with suppress(Exception):
                for text in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
                    el = fr.locator(f'button:has-text("{text}")')
                    if el.count():
                        el.first.click(timeout=1200)
                        page.wait_for_timeout(250)
                        return

def get_hotel_summary(page):
    """Renvoie (note_moyenne:str, nb_avis_total:int|None)."""
    note_moyenne, nb_avis_total = "", ""

    # Note moyenne
    with suppress(Exception):
        el = page.locator('[aria-label*="étoiles sur 5"]').first
        raw = el.get_attribute("aria-label") or ""
        m = re.search(r'(\d+[.,]?\d*)', raw)
        if m: note_moyenne = m.group(1).replace(',', '.')

    # Nombre d'avis
    with suppress(Exception):
        txt = page.locator('div[role="main"]').inner_text()
        m2 = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', txt, flags=re.I)
        if m2:
            nb_avis_total = re.sub(r'\D','', m2.group(1))

    if not nb_avis_total:
        nodes = page.locator(':text("avis")')
        with suppress(Exception):
            for i in range(nodes.count()):
                t = nodes.nth(i).inner_text()
                m = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', t, flags=re.I)
                if m:
                    nb_avis_total = re.sub(r'\D','', m.group(1))
                    break

    # Fallback note si vide
    if not note_moyenne:
        with suppress(Exception):
            t2 = page.locator('div[role="main"]').inner_text()
            m = re.search(r'([0-4](?:[.,]\d)?)\s*(?:\n| )+\d[\d\s\u00A0]*\s+avis', t2, flags=re.I)
            if m: note_moyenne = m.group(1).replace(',', '.')

    nb_total_int: Optional[int] = None
    with suppress(Exception):
        nb_total_int = int(nb_avis_total) if nb_avis_total else None

    return note_moyenne, nb_total_int

def sort_by_recent(page):
    """Essaie d'appliquer 'Les plus récents' (FR/EN)."""
    try:
        opened = False
        for sel in [
            "button:has-text('Trier')",
            "button[aria-label*='Trier']",
            "div[role='button']:has-text('Trier')",
            "button[aria-label*='Sort']",
        ]:
            loc = page.locator(sel)
            if loc.count():
                loc.first.click(timeout=2000)
                opened = True
                break
        if not opened:
            print("[WARN] Bouton 'Trier' introuvable"); return False

        with suppress(Exception):
            page.wait_for_selector("div[role='menu'], div[role='listbox']", timeout=2000)

        for opt in [
            "div[role='menuitem']:has-text('Les plus récents')",
            "div[role='menuitem']:has-text('Plus récents')",
            "div[role='menuitem']:has-text('Most recent')",
            "div[role='option']:has-text('Les plus récents')",
            "div[role='option']:has-text('Plus récents')",
            "div[role='option']:has-text('Most recent')",
            "text=Les plus récents",
            "text=Plus récents",
            "text=Most recent",
        ]:
            loc = page.locator(opt)
            if loc.count():
                loc.first.click(timeout=2000)
                print("↕️ Tri appliqué : Les plus récents")
                return True

        print("[WARN] Option 'Les plus récents' non trouvée")
        return False
    except Exception:
        print("[WARN] Tri récent non appliqué")
        return False

def open_and_prepare_page(context, url):
    page = context.new_page()
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    accept_google_consent(page)
    with suppress(PWTimeout):
        page.wait_for_load_state("networkidle", timeout=6000)

    # Onglet Avis
    with suppress(Exception):
        page.get_by_role("tab", name=re.compile("Avis", re.IGNORECASE)).click(timeout=6000)
    with suppress(Exception):
        page.locator('div[role="tab"]:has-text("Avis")').first.click(timeout=6000)

    page.wait_for_selector('div[data-review-id]', timeout=15000)

    # Tri "Les plus récents"
    sort_by_recent(page)

    # Zoom-out pour afficher plus d’éléments par écran
    with suppress(Exception):
        page.evaluate("document.body.style.zoom='0.9'")

    return page

def existing_rows_count(path: Path) -> int:
    """Compte les *lignes CSV* (gère les sauts de ligne dans les cellules)."""
    if not path.exists():
        return 0
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            next(r, None)  # header
            return sum(1 for _ in r)
    except Exception:
        return 0

def append_rows(path: Path, rows):
    """Append des nouvelles lignes, header auto si fichier n'existe pas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["note_moyenne","nb_avis_total","auteur","contributions","note","date","avis"])
        for r in rows:
            w.writerow(r)

def load_existing_keys(path: Path):
    """Clé anti-doublon pour le raw: (auteur,note,date,avis)."""
    keys = set()
    if path.exists():
        with open(path, "r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                keys.add((row.get("auteur",""), row.get("note",""), row.get("date",""), row.get("avis","")))
    return keys

# ---------- Journal d’ingestion ----------
def ensure_ingestion_csv_header():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not INGESTION_CSV.exists():
        with open(INGESTION_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp","hotel_key","file","before","added","after","nb_avis_total_google","note_moyenne","mode"])

def log_ingestion_run(hotel_key: str, file_path: Path, before: int, added: int, after: int,
                      nb_avis_total_google: Optional[int], note_moyenne: str, mode: str):
    ensure_ingestion_csv_header()
    ts = datetime.now().isoformat(timespec="seconds")
    row = [ts, hotel_key, str(file_path), before, added, after, nb_avis_total_google, note_moyenne, mode]
    # CSV
    with open(INGESTION_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    # JSONL optionnel
    if WRITE_JSONL:
        with open(INGESTION_JSONL, "a", encoding="utf-8") as jf:
            jf.write(json.dumps({
                "timestamp": ts,
                "hotel_key": hotel_key,
                "file": str(file_path),
                "before": before,
                "added": added,
                "after": after,
                "nb_avis_total_google": nb_avis_total_google,
                "note_moyenne": note_moyenne,
                "mode": mode
            }, ensure_ascii=False) + "\n")

def print_run_summary(hotel_key: str, note_moyenne: str, nb_avis_total_google: Optional[int],
                      before: int, added: int, after: int, mode: str, file_path: Path):
    total_google = nb_avis_total_google if nb_avis_total_google is not None else "?"
    block = f"""
──────────────── Ingestion résumé ────────────────
Hôtel            : {hotel_key}
Note moyenne     : {note_moyenne}
Total Google     : {total_google}
Avant (fichier)  : {before}
Nouveaux ajoutés : {added}
Après (fichier)  : {after}
Mode             : {mode}
Fichier          : {file_path}
──────────────────────────────────────────────────
"""
    print(block.strip())

# ----------------------------------------

def scrape_google_maps_delta():
    with sync_playwright() as p:
        # Headless = plus rapide
        browser = p.chromium.launch(headless=HEADLESS, args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ])
        context = browser.new_context(
            viewport={"width": 1700, "height": 2400},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )

        # Bloquer ressources lourdes (accélère sans casser l’UI des avis)
        def route_handler(route):
            try:
                rt = route.request.resource_type
                if rt in {"image", "media", "font"}:
                    return route.abort()
            except Exception:
                pass
            return route.continue_()
        context.route("**/*", route_handler)

        print("🧭 Ouverture de la page Google Maps…")
        # 1 retry si besoin
        for attempt in range(2):
            try:
                page = open_and_prepare_page(context, URL)
                break
            except Exception as e:
                if attempt == 0:
                    with suppress(Exception): context.close()
                    context = browser.new_context(
                        viewport={"width": 1700, "height": 2400},
                        locale="fr-FR",
                        timezone_id="Europe/Paris",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                    )
                    context.route("**/*", route_handler)
                    continue
                else:
                    print(f"⛔ Ouverture impossible : {e}")
                    with suppress(Exception): browser.close()
                    return
        print("✅ Onglet Avis ouvert.")

        note_moyenne, nb_avis_total = get_hotel_summary(page)
        print(f"📊 Résumé hôtel → note_moyenne={note_moyenne} | nb_avis_total={nb_avis_total}")

        # ---- DELTA : combien d'avis faut-il récupérer ? ----
        prev_total_state = get_prev_total(HOTEL_KEY)
        before_count_file = existing_rows_count(OUT_PATH)

        if nb_avis_total is not None:
            # S'aligne sur ce qu'on a réellement en fichier (rattrape si incomplet)
            prev_total = min(before_count_file, nb_avis_total)
            # Synchronise l'état pour les prochains runs
            set_prev_total(HOTEL_KEY, prev_total)
        else:
            # Sans total fiable côté Google, on s'appuie sur le fichier & l'état
            prev_total = max(prev_total_state, before_count_file)

        target_new = None if nb_avis_total is None else max(nb_avis_total - prev_total, 0)
        print(f"[DELTA] prev_total={prev_total}  ->  target_new={target_new}")

        # TOP-UP récent si pas de delta
        force_topup = False
        if target_new == 0:
            print(f"[TOPUP] Pas de delta. On prend quand même les {RECENT_TOPUP} avis les plus récents (anti-trou).")
            target_new = RECENT_TOPUP
            force_topup = True

        # vrai conteneur scrollable (parent overflow)
        first_review = page.locator('div[data-review-id]').first
        scroller = first_review.element_handle().evaluate_handle("""
            (el) => {
              let p = el.parentElement;
              while (p && p.scrollHeight <= p.clientHeight) p = p.parentElement;
              return p;
            }
        """)
        print("🧭 Conteneur scrollable détecté.")
        print("🔽 Défilement + collecte …")

        seen_ids, rows = set(), []
        idle_rounds, round_idx = 0, 0
        last_count = 0

        def extract_new_only():
            nonlocal last_count, rows, seen_ids
            gained = 0
            loc = page.locator('div[data-review-id]')
            cur = loc.count()

            for i in range(last_count, cur):
                b = loc.nth(i)
                rid = b.get_attribute("data-review-id") or ""
                if not rid or rid in seen_ids:
                    continue

                # déplier "Voir plus" si présent
                with suppress(Exception):
                    mb = b.locator('button[aria-label^="Voir plus"]')
                    if mb.count(): mb.first.click()

                # auteur
                auteur = ""
                with suppress(Exception):
                    auteur = b.locator('.d4r55').inner_text()

                # contributions
                contributions = ""
                with suppress(Exception):
                    meta = b.locator('.RfnDt').inner_text()
                    m = re.search(r'(\d[\d\u00A0 ]*)\s*avis', meta)
                    if m: contributions = m.group(1).replace('\u00A0','').replace(' ','')
                
                # note
                note = ""
                with suppress(Exception):
                    n1 = b.locator('.DU9Pgb .fontBodyLarge')
                    if n1.count():
                        raw = n1.first.inner_text()   # ex: "4/5"
                        m = re.search(r'(\d+[.,]?\d*)\s*/\s*5', raw)
                        if m: note = m.group(1).replace(',', '.')
                if not note:
                    with suppress(Exception):
                        n2 = b.locator('[aria-label*="étoiles"], [role="img"]')
                        if n2.count():
                            raw2 = n2.first.get_attribute("aria-label") or ""
                            m2 = re.search(r'(\d+[.,]?\d*)', raw2)
                            if m2: note = m2.group(1).replace(',', '.')

                # date + texte
                date = ""
                with suppress(Exception):
                    date = clean_date(b.locator('.xRkPPb').inner_text())
                texte = ""
                with suppress(Exception):
                    texte = (b.locator('.wiI7pd').inner_text()
                             if b.locator('.wiI7pd').count()
                             else b.locator('span.wiI7pd, span[class*="wiI7pd"]').inner_text())

                rows.append([note_moyenne, nb_avis_total, auteur, contributions, note, date, texte])
                seen_ids.add(rid)
                gained += 1

            last_count = cur
            return gained

        # boucle de scroll
        while True:
            round_idx += 1

            # Scroll en rafale
            for _ in range(SCROLLS_PER_ROUND):
                try:
                    page.evaluate("(el,dy)=>el.scrollBy(0, dy)", scroller, SCROLL_STEP_PX)
                except Exception:
                    with suppress(Exception): page.keyboard.press("End")
                human_sleep(*SCROLL_PAUSE)

            # attendre des nouveaux items
            with suppress(PWTimeout):
                page.wait_for_function(
                    "document.querySelectorAll('div[data-review-id]').length > %d" % last_count,
                    timeout=1200
                )

            gained = extract_new_only()
            total = len(rows)
            print(f"  • Tour {round_idx}: +{gained} (total {total})")

            # Arrêt si quota atteint (delta ou top-up)
            if (target_new is not None) and (total >= target_new):
                print(f"[STOP] Quota atteint ({total}/{target_new}) -> stop.")
                break

            if gained == 0:
                idle_rounds += 1
            else:
                idle_rounds = 0

            if idle_rounds >= IDLE_ROUNDS_LIMIT:
                print(f"✅ Stabilisé : plus de nouveaux avis ({total}).")
                break

        # si on a dépassé un peu la cible, on tronque
        if target_new is not None and len(rows) > target_new:
            rows = rows[:target_new]

        # Dédup si TOP-UP (ne garder que les vraiment nouveaux vs fichier)
        if force_topup:
            existing = load_existing_keys(OUT_PATH)
            def key_of(r):
                # r = [note_moyenne, nb_avis_total, auteur, contributions, note, date, avis]
                return (r[2], r[4], r[5], r[6])
            before_len = len(rows)
            rows = [r for r in rows if key_of(r) not in existing]
            print(f"[TOPUP] {len(rows)} nouveaux avis uniques (sur {before_len}) après dédup fichier.")

        # append des nouvelles lignes
        append_rows(OUT_PATH, rows)
        added_count = len(rows)

        # MàJ de l'état delta (on met au moins ce qu'on a vu)
        if nb_avis_total is not None:
            set_prev_total(HOTEL_KEY, max(get_prev_total(HOTEL_KEY), min(existing_rows_count(OUT_PATH), nb_avis_total)))

        # Comptages finaux et LOG
        after_count_file = existing_rows_count(OUT_PATH)
        mode = "topup" if force_topup else "delta"

        # Impression d’un bloc synthèse + écriture du journal
        print_run_summary(
            hotel_key=HOTEL_KEY,
            note_moyenne=note_moyenne,
            nb_avis_total_google=nb_avis_total,
            before=before_count_file,
            added=added_count,
            after=after_count_file,
            mode=mode,
            file_path=OUT_PATH
        )
        log_ingestion_run(
            hotel_key=HOTEL_KEY,
            file_path=OUT_PATH,
            before=before_count_file,
            added=added_count,
            after=after_count_file,
            nb_avis_total_google=nb_avis_total,
            note_moyenne=note_moyenne,
            mode=mode
        )

        # Message final console
        print(f"\n💾 Ajouté {added_count} nouveaux avis → {OUT_PATH}")
        print("✔ Terminé.")

        with suppress(Exception): browser.close()

if __name__ == "__main__":
    scrape_google_maps_delta()
