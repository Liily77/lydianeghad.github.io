import csv, os, re, time, random
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# --------- CONFIG ----------
HOTEL_NAME = "BW_Ronceray_Opera"
URL = "https://www.google.com/maps/place/Best+Western+H%C3%B4tel+Ronceray-Op%C3%A9ra/@48.8719708,2.3393857,470m/data=!3m1!1e3!4m11!3m10!1s0x47e66e3e9be04a55:0x4c041e52c3afe33b!5m2!4m1!1i2!8m2!3d48.8719673!4d2.3419606!9m1!1b1!16s%2Fg%2F113fj52c3k9"

MAX_REVIEWS = 1200
IDLE_ROUNDS_LIMIT = 25
SCROLLS_PER_ROUND = 10      # plus de scrolls par tour
SCROLL_STEP_PX = 3000
SCROLL_PAUSE = (0.08, 0.16) # pauses très courtes
AUTOSAVE_EVERY = 200



def human_sleep(a,b): time.sleep(random.uniform(a,b))

def clean_date(s:str)->str:
    if not s: return ""
    return re.sub(r"\s*sur\s+(Google|Tripadvisor).*", "", s, flags=re.I).strip()

def accept_google_consent(page):
    try:
        page.wait_for_timeout(400)
        for text in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
            btn = page.locator(f'button:has-text("{text}")')
            if btn.count():
                btn.first.click(timeout=1200)
                page.wait_for_timeout(300)
                return
        for fr in page.frames:
            try:
                for text in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
                    el = fr.locator(f'button:has-text("{text}")')
                    if el.count():
                        el.first.click(timeout=1200)
                        page.wait_for_timeout(300)
                        return
            except:
                pass
    except:
        pass

def get_hotel_summary(page):
    """Renvoie (note_moyenne, nb_avis_total) en gérant '1 189' / '1\\n189' et évite '81189'."""
    note_moyenne, nb_avis_total = "", ""

    # note moyenne (aria-label “X,X étoiles sur 5”)
    try:
        el = page.locator('[aria-label*="étoiles sur 5"]').first
        raw = el.get_attribute("aria-label") or ""
        m = re.search(r'(\d+[.,]?\d*)', raw)
        if m: note_moyenne = m.group(1).replace(',', '.')
    except: pass

    # nb avis — capture chiffres avec espaces/sauts de ligne puis filtre, en évitant un chiffre qui colle avant (ex: "3,8\n1 189 avis")
    try:
        txt = page.locator('div[role="main"]').inner_text()
        # on ignore un chiffre immédiatement avant le groupe “X avis”
        m2 = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', txt, flags=re.I)
        if m2:
            nb_avis_total = re.sub(r'\D','', m2.group(1))
    except: pass

    if not nb_avis_total:
        nodes = page.locator(':text("avis")')
        for i in range(nodes.count()):
            try:
                t = nodes.nth(i).inner_text()
                m = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', t, flags=re.I)
                if m:
                    nb_avis_total = re.sub(r'\D','', m.group(1))
                    break
            except: pass

    # fallback note si vide : première décimale 0–5 proche du mot "avis"
    if not note_moyenne:
        try:
            t2 = page.locator('div[role="main"]').inner_text()
            m = re.search(r'([0-4](?:[.,]\d)?)\s*(?:\n| )+\d[\d\s\u00A0]*\s+avis', t2, flags=re.I)
            if m: note_moyenne = m.group(1).replace(',', '.')
        except: pass

    return note_moyenne, nb_avis_total

def open_and_prepare_page(context, url):
    page = context.new_page()
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    accept_google_consent(page)
    try: page.wait_for_load_state("networkidle", timeout=8000)
    except PWTimeout: pass

    # ouvrir l’onglet Avis
    try:
        page.get_by_role("tab", name=re.compile("Avis", re.IGNORECASE)).click(timeout=6000)
    except:
        page.locator('div[role="tab"]:has-text("Avis")').first.click(timeout=6000)

    page.wait_for_selector('div[data-review-id]', timeout=12000)

    # zoom out pour afficher plus d’éléments par écran
    try:
        page.evaluate("document.body.style.zoom='0.85'")
    except: pass

    return page

def scrape_google_maps():
    with sync_playwright() as p:
        # Headless = plus rapide. Si Google fait la difficile, repasse à headless=False.
        browser = p.chromium.launch(headless=True, args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ])
        context = browser.new_context(
            viewport={"width": 1700, "height": 2400},   # grand viewport
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )

        # ⚡ bloque images / vidéos / fonts / tiles lourdes
        def should_block(url: str) -> bool:
            if re.search(r'\.(png|jpg|jpeg|gif|webp|svg)(\?.*)?$', url): return True
            if re.search(r'\.(mp4|webm|avi|mov)(\?.*)?$', url): return True
            if re.search(r'\.(woff2?|ttf|otf)(\?.*)?$', url): return True
            # tiles & images carto
            if "maps.googleapis.com/maps/vt" in url: return True
            if "maps.gstatic.com/mapfiles" in url: return True
            if "googleusercontent.com" in url and "/maps" in url: return True
            return False

        context.route("**/*", lambda route: route.abort() if should_block(route.request.url) else route.continue_())

        print("🧭 Ouverture de la page Google Maps…")
        # 1 retry si besoin
        for attempt in range(2):
            try:
                page = open_and_prepare_page(context, URL)
                break
            except Exception as e:
                if attempt == 0:
                    try: context.close()
                    except: pass
                    context = browser.new_context(
                        viewport={"width": 1700, "height": 2400},
                        locale="fr-FR",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                    )
                    context.route("**/*", lambda route: route.abort() if should_block(route.request.url) else route.continue_())
                    continue
                else:
                    print(f"⛔ Ouverture impossible : {e}")
                    browser.close()
                    return
        print("✅ Onglet Avis ouvert.")

        note_moyenne, nb_avis_total = get_hotel_summary(page)
        print(f"📊 Résumé hôtel → note_moyenne={note_moyenne} | nb_avis_total={nb_avis_total}")

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

        seen_ids, rows = set(), []
        idle_rounds, round_idx = 0, 0
        last_count = 0

        def save_csv(path):
            os.makedirs("raw_data", exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["note_moyenne","nb_avis_total","auteur","contributions","note","date","avis"])
                w.writerows(rows)

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
                try:
                    mb = b.locator('button[aria-label^="Voir plus"]')
                    if mb.count(): mb.first.click()
                except: pass

                # auteur
                try: auteur = b.locator('.d4r55').inner_text()
                except: auteur = ""

                # contributions (ex: "Local Guide · 79 avis · 27 photos")
                contributions = ""
                try:
                    meta = b.locator('.RfnDt').inner_text()
                    m = re.search(r'(\d[\d\u00A0 ]*)\s*avis', meta)
                    if m: contributions = m.group(1).replace('\u00A0','').replace(' ','')
                except: pass

                # note individuelle
                note = ""
                try:
                    n1 = b.locator('.DU9Pgb .fontBodyLarge')
                    if n1.count():
                        raw = n1.first.inner_text()   # ex: "3/5"
                        m = re.search(r'(\d+[.,]?\d*)\s*/\s*5', raw)
                        if m: note = m.group(1).replace(',', '.')
                    if not note:
                        n2 = b.locator('[aria-label*="étoiles"], [role="img"]')
                        if n2.count():
                            raw2 = n2.first.get_attribute("aria-label") or ""
                            m2 = re.search(r'(\d+[.,]?\d*)', raw2)
                            if m2: note = m2.group(1).replace(',', '.')
                except: pass

                # date + texte
                try: date = clean_date(b.locator('.xRkPPb').inner_text())
                except: date = ""
                texte = ""
                try: texte = b.locator('.wiI7pd').inner_text()
                except:
                    try: texte = b.locator('span.wiI7pd, span[class*="wiI7pd"]').inner_text()
                    except: texte = ""

                rows.append([note_moyenne, nb_avis_total, auteur, contributions, note, date, texte])
                seen_ids.add(rid)
                gained += 1

            last_count = cur
            return gained

        out_path = f"raw_data/avis_google_{HOTEL_NAME}.csv"

        print("🔽 Défilement + collecte (turbo)…")
        while True:
            round_idx += 1

            # Scroll en rafale (peu d'attentes)
            for _ in range(SCROLLS_PER_ROUND):
                try:
                    page.evaluate("(el,dy)=>el.scrollBy(0, dy)", scroller, SCROLL_STEP_PX)
                except:
                    page.keyboard.press("End")
                human_sleep(*SCROLL_PAUSE)

            # Attendre brièvement qu’un nouveau lot apparaisse
            try:
                page.wait_for_function(
                    "document.querySelectorAll('div[data-review-id]').length > %d" % last_count,
                    timeout=1200
                )
            except PWTimeout:
                pass

            gained = extract_new_only()
            total = len(rows)
            print(f"  • Tour {round_idx}: +{gained} (total {total})")

            if total and total % AUTOSAVE_EVERY == 0:
                save_csv(out_path)
                print(f"  • 💾 Autosauvegarde ({total})")

            if gained == 0:
                idle_rounds += 1
            else:
                idle_rounds = 0

            if total >= MAX_REVIEWS:
                print(f"🛑 MAX_REVIEWS atteint ({total})."); break
            if idle_rounds >= IDLE_ROUNDS_LIMIT:
                print(f"✅ Stabilisé : plus de nouveaux avis ({total})."); break

        save_csv(out_path)
        print(f"\n✅ {len(rows)} avis enregistrés → {out_path}")
        browser.close()

if __name__ == "__main__":
    scrape_google_maps()
