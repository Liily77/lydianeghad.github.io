# scripts/scraping/scrape_google_maps_hotel_4.py
# --- Best Western Bretagne Montparnasse --- DELTA + TOP-UP + anti-plateaux + ouverture robuste ---
# Journal d’ingestion + captures debug si l’onglet Avis ne s’ouvre pas

import csv, os, re, time, random, json
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import suppress
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---- Delta state (nécessite scripts/scraping/ingestion_state.py) ----
from scripts.scraping.ingestion_state import get_prev_total, set_prev_total

# ===== À PERSONNALISER =====
HOTEL_KEY  = "BW_Bretagne_Montparnasse"
HOTEL_NAME = "Best Western Bretagne Montparnasse"
URL = "https://www.google.com/maps/place/H%C3%B4tel+de+Bretagne+-+Best+Western/@48.8354345,2.3185617,941m/data=!3m1!1e3!4m11!3m10!1s0x47e671b546f61d93:0x8cfba53fad06d2e3!5m2!4m1!1i2!8m2!3d48.835431!4d2.321142!9m1!1b1!16s%2Fg%2F1hc0v46_j?entry=ttu&g_ep=EgoyMDI1MDkyNC4wIKXMDSoASAFQAw%3D%3D"  
# ===========================

# ===== Sorties & journal =====
OUT_PATH         = Path("data/raw/avis_google_BW_Bretagne_Montparnasse.csv")
STATE_DIR        = Path("data/state")
DEBUG_DIR        = STATE_DIR / "debug"
INGESTION_CSV    = STATE_DIR / "ingestion_runs.csv"
INGESTION_JSONL  = STATE_DIR / "ingestion_runs.jsonl"
WRITE_JSONL      = True  # passe à False si tu ne veux pas le miroir JSONL

# ===== Réglages vitesse/stabilité =====
HEADLESS = (os.environ.get("PW_HEADLESS", "1") != "0")  # mets PW_HEADLESS=0 pour voir le navigateur
SCROLLS_PER_ROUND   = 36
SCROLL_PAUSE        = (0.004, 0.012)
IDLE_ROUNDS_LIMIT   = 6
MAX_RELOADS         = 6
HARD_CAP            = 20000
WAIT_REVIEWS_TIMEOUT_MS = 45000  # attente robuste de la liste d’avis

# ⚡ Laisse les styles (meilleure virtualisation) ; on bloque images/médias/polices
BLOCK_RESOURCE_TYPES = {"image", "media", "font"}

# Nombre d'avis récents à prendre même si delta=0 (anti-trou)
RECENT_TOPUP = 60

def rnd(a,b): time.sleep(random.uniform(a,b))

def clean_date(s:str)->str:
    if not s: return ""
    return re.sub(r"\s*sur\s+(Google|Tripadvisor).*", "", s, flags=re.I).strip()

def sanitize(t:str)->str:
    if not t: return ""
    t = t.replace("\u00A0"," ").replace("\u202A","").replace("\u202C","")
    return re.sub(r"\s+", " ", t).strip()

def accept_consent(page):
    with suppress(Exception):
        page.wait_for_timeout(400)
        for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter","J’accepte tout","Accepter les cookies"]:
            b = page.locator(f'button:has-text("{txt}")')
            if b.count():
                b.first.click(timeout=1500); page.wait_for_timeout(350); return
        for fr in page.frames:
            with suppress(Exception):
                for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter","J’accepte tout","Accepter les cookies"]:
                    el = fr.locator(f'button:has-text("{txt}")')
                    if el.count():
                        el.first.click(timeout=1500); page.wait_for_timeout(350); return

def ensure_filters(page):
    # Tri = Les plus récents
    with suppress(Exception):
        btn = page.locator('button[aria-label*="Trier"], button:has-text("Avis les plus"), button:has-text("Trier")')
        if btn.count():
            btn.first.click()
            page.locator('div[role="menu"], div[role="listbox"]').locator("div:has-text('Les plus récents'), span:has-text('Les plus récents')").first.click()
            page.wait_for_timeout(200)
    # Langue = Toutes les langues
    with suppress(Exception):
        chip = page.locator('button:has-text("Français"), button:has-text("Langue"), button:has-text("Toutes les langues"), button:has-text("Tous les avis")')
        if chip.count() and re.search(r"Français|Seulement", chip.first.inner_text() or "", re.I):
            chip.first.click()
            menu = page.locator("div[role='menu'], div[role='listbox']")
            for label in ["Toutes les langues", "Tous les avis", "Toutes"]:
                opt = menu.locator(f"div:has-text('{label}'), span:has-text('{label}')")
                if opt.count(): opt.first.click(); break
            page.wait_for_timeout(200)

def get_hotel_summary(page):
    avg, total = "", None
    with suppress(Exception):
        lab = page.locator('[aria-label*="étoiles sur 5"]').first.get_attribute("aria-label") or ""
        m = re.search(r'(\d+[.,]?\d*)', lab); 
        if m: avg = m.group(1).replace(",", ".")
    with suppress(Exception):
        main = page.locator('div[role="main"]').inner_text()
        m2 = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', main, flags=re.I)
        if m2: total = int(re.sub(r"\D","", m2.group(1)))
        if not avg:
            m3 = re.search(r'([0-4](?:[.,]\d))\s*[\n ]+[\d\s\u00A0]+avis', main)
            if m3: avg = m3.group(1).replace(",", ".")
    return avg, total

def mark_scroller(page):
    page.evaluate("""() => {
        const isScrollable = el => el && (el.scrollHeight - el.clientHeight) > 20 &&
                                   getComputedStyle(el).overflowY !== 'visible';
        let sc = document.querySelector('div[aria-label*="Avis"] .m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd');
        if (!isScrollable(sc)) {
          const cards = document.querySelectorAll('div[data-review-id]');
          if (cards.length) {
            let el = cards[cards.length-1].parentElement;
            while (el && !isScrollable(el)) el = el.parentElement;
            sc = el || sc;
          }
        }
        if (!isScrollable(sc)) {
          const cands = Array.from(document.querySelectorAll('div')).filter(isScrollable);
          sc = cands.sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight))[0]
               || document.scrollingElement || document.body;
        }
        if (sc) sc.setAttribute('data-scroller','1');
    }""")

def deep_scroll(page, steps=28, mode="burst"):
    page.evaluate(
        """(p) => {
            const { steps, mode } = p;
            const sc = document.querySelector('[data-scroller="1"]')
                   || document.scrollingElement || document.body;
            const H  = sc.clientHeight;
            const dy = Math.max(200, Math.ceil(H*0.92));
            if (mode === 'jump') {
                for (let i=0;i<steps;i++) { sc.scrollBy(0, dy); sc.scrollBy(0, -40); sc.scrollBy(0, +120); }
            } else {
                for (let i=0;i<steps;i++) sc.scrollBy(0, dy);
            }
            if (sc.scrollHeight - sc.scrollTop - H < H*0.5) sc.scrollTop = sc.scrollHeight;
        }""",
        {"steps": steps, "mode": mode}
    )
    page.wait_for_timeout(120)

def save_debug_artifacts(page, label: str):
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        png = DEBUG_DIR / f"{label}_{ts}.png"
        html = DEBUG_DIR / f"{label}_{ts}.html"
        page.screenshot(path=str(png), full_page=True)
        html_content = page.content()
        with open(html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[DEBUG] Screenshot: {png}")
        print(f"[DEBUG] HTML dump : {html}")
    except Exception as e:
        print(f"[DEBUG] Capture impossible: {e}")

def click_reviews_entrypoints(page) -> bool:
    """Essaye plusieurs points d’entrée pour ouvrir les avis."""
    try:
        # 1) Onglet "Avis" (FR/EN)
        tab = page.get_by_role("tab", name=re.compile("Avis|Reviews", re.I))
        if tab.count():
            tab.first.click(timeout=4000)
            return True
    except Exception:
        pass
    try:
        # 2) Bouton 'Avis' en tant que bouton générique
        btn = page.locator("button:has-text('Avis'), button:has-text('Reviews')")
        if btn.count():
            btn.first.click(timeout=4000)
            return True
    except Exception:
        pass
    try:
        # 3) Lien/bouton "Voir tous les avis"
        more = page.locator("a:has-text('Voir tous les avis'), button:has-text('Voir tous les avis'), a:has-text('All reviews'), button:has-text('All reviews')")
        if more.count():
            more.first.click(timeout=4000)
            return True
    except Exception:
        pass
    try:
        # 4) Sélecteurs internes Google Maps (jsaction)
        jsbtn = page.locator("button[jsaction*='pane.reviewChart.moreReviews'], button[jsaction*='pane.rating.moreReviews']")
        if jsbtn.count():
            jsbtn.first.click(timeout=4000)
            return True
    except Exception:
        pass
    return False

def wait_reviews_list(page) -> bool:
    """Attend l’apparition de la liste d’avis via plusieurs sélecteurs."""
    sels = [
        "div[data-review-id]",
        "div[aria-label*='Avis'] div[data-review-id]",
        "div.section-review",                    # anciens layouts
        "div[role='region'][aria-label*='Avis'] div[data-review-id]"  # <- corrigé (quote en trop supprimée)
    ]
    deadline = time.time() + (WAIT_REVIEWS_TIMEOUT_MS/1000.0)
    while time.time() < deadline:
        for s in sels:
            try:
                if page.locator(s).first.count():
                    # état 'attached' : pas besoin d’être visible à l’écran
                    page.locator(s).first.wait_for(state="attached", timeout=1500)
                    return True
            except Exception:
                pass
        page.wait_for_timeout(350)
    return False

def open_reviews(context, url):
    page = context.new_page(); page.set_default_timeout(8000)
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    accept_consent(page)
    with suppress(PWTimeout): page.wait_for_load_state("networkidle", timeout=6000)

    # Essayer d’ouvrir les avis
    if not click_reviews_entrypoints(page):
        print("[WARN] Point d’entrée 'Avis' non cliqué du 1er coup, on retente après zoom-out…")
    with suppress(Exception): page.evaluate("document.body.style.zoom='0.85'")
    if not click_reviews_entrypoints(page):
        print("[WARN] 2e tentative sur les entrées 'Avis'…")

    # Attendre la liste
    ok = wait_reviews_list(page)
    if not ok:
        print("[ERROR] La liste d’avis n’est pas apparue dans le délai imparti.")
        save_debug_artifacts(page, "hotel4_open_reviews_timeout")
        raise PWTimeout("Liste d'avis introuvable")

    # Tri & zoom
    ensure_filters(page)
    mark_scroller(page)
    return page

def existing_rows_count(path: Path) -> int:
    if not path.exists(): return 0
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            r = csv.reader(f); next(r, None)
            return sum(1 for _ in r)
    except Exception:
        return 0

def append_rows(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["note_moyenne","nb_avis_total","auteur","contributions","note","date","avis"])
        for r in rows: w.writerow(r)

def load_existing_keys(path: Path):
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
            csv.writer(f).writerow(
                ["timestamp","hotel_key","file","before","added","after","nb_avis_total_google","note_moyenne","mode"]
            )

def log_ingestion_run(hotel_key: str, file_path: Path, before: int, added: int, after: int,
                      nb_avis_total_google: Optional[int], note_moyenne: str, mode: str):
    ensure_ingestion_csv_header()
    ts = datetime.now().isoformat(timespec="seconds")
    row = [ts, hotel_key, str(file_path), before, added, after, nb_avis_total_google, note_moyenne, mode]
    with open(INGESTION_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    if WRITE_JSONL:
        with open(INGESTION_JSONL, "a", encoding="utf-8") as jf:
            jf.write(json.dumps({
                "timestamp": ts, "hotel_key": hotel_key, "file": str(file_path),
                "before": before, "added": added, "after": after,
                "nb_avis_total_google": nb_avis_total_google,
                "note_moyenne": note_moyenne, "mode": mode
            }, ensure_ascii=False) + "\n")

def print_run_summary(hotel_key: str, note_moyenne: str, nb_avis_total_google: Optional[int],
                      before: int, added: int, after: int, mode: str, file_path: Path):
    total_google = nb_avis_total_google if nb_avis_total_google is not None else "?"
    print(f"""
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
""".strip())

# ---------- Extraction DOM ----------
def extract_visible_batch(page):
    return page.evaluate("""() => {
        const nodes = [...document.querySelectorAll('div[data-review-id]')];
        return nodes.map(n => {
            const auteur = n.querySelector('.d4r55')?.textContent?.trim() || '';
            const meta = n.querySelector('.RfnDt')?.textContent || '';
            let contributions = '';
            const m = meta && meta.match(/(\\d[\\d\\u00A0 ]*)\\s*avis/i);
            if (m) contributions = m[1].replace(/\\D/g,'');
            let note = '';
            const n1 = n.querySelector('.DU9Pgb .fontBodyLarge');
            if (n1) {
                const m0 = n1.textContent.match(/(\\d+[.,]?\\d*)\\s*\\/\\s*5/);
                if (m0) note = m0[1].replace(',', '.');
            }
            if (!note) {
                const n2 = n.querySelector('[aria-label*="étoiles"], [role="img"]');
                const lab = n2?.getAttribute('aria-label') || '';
                const m2 = lab.match(/(\\d+[.,]?\\d*)/);
                if (m2) note = m2[1].replace(',', '.');
            }
            const date = n.querySelector('.xRkPPb')?.textContent?.trim() || '';
            const avis = (n.querySelector('.wiI7pd')?.textContent
                        || n.querySelector('span.wiI7pd, span[class*="wiI7pd"]')?.textContent
                        || '').trim();
            return { auteur, contributions, note, date, avis };
        });
    }""")

# ----------------------------------------

def scrape_google_maps_delta():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-gpu","--disable-dev-shm-usage","--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1700, "height": 2400},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")
        )

        def route_handler(route):
            try:
                if route.request.resource_type in BLOCK_RESOURCE_TYPES:
                    return route.abort()
            except Exception:
                pass
            return route.continue_()
        context.route("**/*", route_handler)

        print("🧭 Ouverture de la page Google Maps…")
        for attempt in range(2):
            try:
                page = open_reviews(context, URL)
                break
            except Exception as e:
                if attempt == 0:
                    print(f"[WARN] Ouverture avis échouée, on retente (reset contexte) : {e}")
                    with suppress(Exception): context.close()
                    context = browser.new_context(
                        viewport={"width": 1700, "height": 2400},
                        locale="fr-FR",
                        timezone_id="Europe/Paris",
                        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")
                    )
                    context.route("**/*", route_handler)
                    continue
                else:
                    print(f"⛔ Ouverture impossible : {e}")
                    with suppress(Exception): browser.close()
                    return
        print("✅ Onglet Avis prêt.")

        note_moyenne, nb_avis_total = get_hotel_summary(page)
        print(f"📊 Résumé hôtel → note_moyenne={note_moyenne} | nb_avis_total={nb_avis_total}")

        # ---- DELTA / TOP-UP ----
        prev_total_state  = get_prev_total(HOTEL_KEY)
        before_count_file = existing_rows_count(OUT_PATH)

        if nb_avis_total is not None:
            prev_total = min(before_count_file, nb_avis_total)
            set_prev_total(HOTEL_KEY, prev_total)
        else:
            prev_total = max(prev_total_state, before_count_file)

        target_new = None if nb_avis_total is None else max(nb_avis_total - prev_total, 0)
        print(f"[DELTA] prev_total={prev_total}  ->  target_new={target_new}")

        force_topup = False
        if target_new == 0:
            print(f"[TOPUP] Pas de delta. On prend quand même les {RECENT_TOPUP} avis les plus récents (anti-trou).")
            target_new = RECENT_TOPUP
            force_topup = True

        # Dédup vs fichier
        seen_keys = load_existing_keys(OUT_PATH)
        idle = reloads = rounds = 0
        plateau_rounds = 0
        collected = []

        while True:
            rounds += 1

            for _ in range(SCROLLS_PER_ROUND):
                rnd(*SCROLL_PAUSE)
            if plateau_rounds >= 1:
                deep_scroll(page, steps=28, mode="burst")
            if plateau_rounds >= 3:
                deep_scroll(page, steps=18, mode="jump")

            # Extraction en lot
            raw_batch = []
            with suppress(Exception):
                raw_batch = extract_visible_batch(page)

            gained = 0
            for item in (raw_batch or []):
                auteur = sanitize(item.get("auteur",""))
                contributions = re.sub(r"\D","", item.get("contributions","") or "")
                note = (item.get("note") or "").replace(",", ".")
                date = clean_date(item.get("date",""))
                texte = sanitize(item.get("avis",""))
                key = (auteur, note, date, texte)
                if key in seen_keys:
                    continue
                collected.append([note_moyenne, nb_avis_total, auteur, contributions, note, date, texte])
                seen_keys.add(key)
                gained += 1

            # Arrêt si quota atteint
            if (target_new is not None) and (len(collected) >= target_new):
                print(f"[STOP] Quota atteint ({len(collected)}/{target_new}) -> stop.")
                break
            if len(seen_keys) >= HARD_CAP:
                print(f"🛑 Limite de sécurité atteinte ({HARD_CAP})."); break

            plateau_rounds = 0 if gained else (plateau_rounds + 1)
            idle = idle + 1 if gained == 0 else 0

            if idle >= IDLE_ROUNDS_LIMIT:
                if reloads >= MAX_RELOADS:
                    print(f"✅ Stabilisé : plus de nouveaux avis (total collectés {len(collected)})."); break
                reloads += 1
                print(f"🔁 Reload #{reloads} — réouverture & refiltres…")
                try:
                    page = open_reviews(context, URL)
                except Exception as e:
                    print(f"[WARN] Reload: ouverture avis KO: {e}")
                    save_debug_artifacts(page, "hotel4_reload_open_fail")
                    break
                with suppress(Exception):
                    nm2, tot2 = get_hotel_summary(page)
                    if nm2: note_moyenne = nm2
                    if tot2: nb_avis_total = tot2
                idle = plateau_rounds = 0

        # Tronque si dépassement
        if (target_new is not None) and (len(collected) > target_new):
            collected = collected[:target_new]

        # Dédup spécifique TOP-UP (vs fichier)
        if force_topup and collected:
            existing = load_existing_keys(OUT_PATH)
            def key_of(r):  # r = [note_moyenne, nb_avis_total, auteur, contributions, note, date, avis]
                return (r[2], r[4], r[5], r[6])
            before_len = len(collected)
            collected = [r for r in collected if key_of(r) not in existing]
            print(f"[TOPUP] {len(collected)} nouveaux avis uniques (sur {before_len}) après dédup fichier.")

        # Append au RAW
        append_rows(OUT_PATH, collected)
        added_count = len(collected)

        # MàJ état delta
        if nb_avis_total is not None:
            set_prev_total(HOTEL_KEY, max(get_prev_total(HOTEL_KEY), min(existing_rows_count(OUT_PATH), nb_avis_total)))

        # Comptes & journal
        after_count_file = existing_rows_count(OUT_PATH)
        mode = "topup" if force_topup else "delta"

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

        print(f"\n💾 Ajouté {added_count} nouveaux avis → {OUT_PATH}")
        print("✔ Terminé.")
        with suppress(Exception): browser.close()

# alias pour compat éventuelle
def open_and_prepare_page(context, url):  # noqa
    return open_reviews(context, url)

if __name__ == "__main__":
    scrape_google_maps_delta()
