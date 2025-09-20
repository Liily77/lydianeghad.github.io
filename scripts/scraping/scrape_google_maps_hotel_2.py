import csv, os, re, time, random
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ===== À PERSONNALISER =====
HOTEL_NAME = "BW_Empire_Elysees"
URL = "https://www.google.com/maps/place/Best+Western+Empire+Elys%C3%A9es/@48.8780696,2.2930757,470m/data=!3m1!1e3!4m11!3m10!1s0x47e66f9357f0fda5:0xf03292d5bb9a1f96!5m2!4m1!1i2!8m2!3d48.8780661!4d2.2956506!9m1!1b1!16s%2Fg%2F1tcxchxt"
# ===========================

HEADLESS = False
SCROLLS_PER_ROUND = 18
SCROLL_PAUSE = (0.03, 0.08)
IDLE_ROUNDS_LIMIT = 20
MAX_RELOADS = 6
HARD_CAP = 20000

def rnd(a,b): time.sleep(random.uniform(a,b))

def clean_date(s:str)->str:
    if not s: return ""
    return re.sub(r"\s*sur\s+(Google|Tripadvisor).*", "", s, flags=re.I).strip()

def sanitize(t:str)->str:
    if not t: return ""
    return re.sub(r"\s+"," ", t.replace("\u00A0"," ").replace("\u202A","").replace("\u202C","")).strip()

def accept_consent(page):
    try:
        page.wait_for_timeout(300)
        for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
            b = page.locator(f'button:has-text("{txt}")')
            if b.count():
                b.first.click(timeout=1200)
                page.wait_for_timeout(300)
                return
        # variantes en iframe
        for fr in page.frames:
            for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
                el = fr.locator(f'button:has-text("{txt}")')
                if el.count():
                    el.first.click(timeout=1200)
                    page.wait_for_timeout(300)
                    return
    except:
        pass

def ensure_filters(page):
    """Force Source=Google, Tri=Les plus récents, Langue=Toutes les langues."""
    # 1) Source = Google
    try:
        source_chip = page.locator(
            "button:has-text('Tous les avis'), button:has-text('Google'), button:has-text('Tripadvisor')"
        ).first
        if source_chip.count():
            label = (source_chip.inner_text() or "").strip()
            if "Google" not in label:
                source_chip.click()
                menu = page.locator("div[role='menu'], div[role='listbox']")
                google_opt = menu.locator("div:has-text('Google'), span:has-text('Google')")
                if google_opt.count():
                    google_opt.first.click()
                    page.wait_for_timeout(300)
                    print("🔧 Source d'avis = Google")
    except:
        pass

    # 2) Tri = Les plus récents
    try:
        btn = page.locator('button[aria-label*="Trier"], button:has-text("Avis les plus"), button:has-text("Trier")')
        if btn.count():
            btn.first.click()
            page.locator('div[role="menu"] div:has-text("Les plus récents")').first.click()
            page.wait_for_timeout(300)
    except:
        pass

    # 3) Langue = Toutes les langues / Tous les avis
    try:
        chip = page.locator(
            'button:has-text("Français"), button:has-text("Langue"), button:has-text("Tous les avis"), button:has-text("Toutes les langues")'
        )
        if chip.count():
            txt = chip.first.inner_text() or ""
            if re.search(r"Français|Seulement", txt, re.I):
                chip.first.click()
                menu = page.locator("div[role='menu'], div[role='listbox']")
                for label in ["Toutes les langues", "Tous les avis", "Toutes"]:
                    opt = menu.locator(f"div:has-text('{label}'), span:has-text('{label}')")
                    if opt.count():
                        opt.first.click()
                        break
                page.wait_for_timeout(300)
    except:
        pass

def get_hotel_summary(page):
    avg, total = "", 0
    try:
        el = page.locator('[aria-label*="étoiles sur 5"]').first
        raw = el.get_attribute("aria-label") or ""
        m = re.search(r'(\d+[.,]?\d*)', raw)
        if m: avg = m.group(1).replace(",", ".")
    except:
        pass
    try:
        main = page.locator('div[role="main"]').inner_text()
        m2 = re.search(r'(?<![\d,])(\d[\d\s\u00A0]*)\s+avis\b', main, flags=re.I)
        if m2: total = int(re.sub(r"\D","", m2.group(1)))
        if not avg:
            m3 = re.search(r'([0-4](?:[.,]\d))\s*[\n ]+[\d\s\u00A0]+avis', main)
            if m3: avg = m3.group(1).replace(",", ".")
    except:
        pass
    return avg, total

def open_reviews(context, url):
    page = context.new_page()
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    accept_consent(page)
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except PWTimeout:
        pass
    # Aller sur l’onglet Avis
    try:
        page.get_by_role("tab", name=re.compile("Avis", re.IGNORECASE)).click(timeout=7000)
    except:
        page.locator('div[role="tab"]:has-text("Avis")').first.click(timeout=7000)
    page.wait_for_selector('div[data-review-id]', timeout=15000)
    try:
        page.evaluate("document.body.style.zoom='0.9'")
    except:
        pass
    ensure_filters(page)
    return page

def scroll_more(page):
    """Forcer le lazy-load : amène le dernier bloc en vue + wheel + PageDown."""
    try:
        last = page.locator('div[data-review-id]').last()
        last.scroll_into_view_if_needed()
    except:
        pass
    try: page.mouse.wheel(0, 5000)
    except: pass
    try: page.keyboard.press("PageDown")
    except: pass
    rnd(*SCROLL_PAUSE)

def write_header_if_needed(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "review_id","note_moyenne","nb_avis_total","auteur","contributions","note","date","avis"
            ])

def scrape_all():
    out_csv = f"raw_data/avis_google_{HOTEL_NAME}.csv"
    os.makedirs("raw_data", exist_ok=True)
    write_header_if_needed(out_csv)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-gpu","--disable-dev-shm-usage","--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1700, "height": 2200},
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )

        print("🧭 Ouverture de la page Google Maps…")
        page = open_reviews(context, URL)
        avg, total_expected = get_hotel_summary(page)
        print(f"📊 Résumé hôtel → note_moyenne={avg} | nb_avis_total={total_expected or 'inconnu'}")
        print("🧭 Conteneur scrollable détecté.")
        print("🔽 Défilement + collecte (turbo)…")

        # Dédup (reprend un CSV existant)
        seen = set()
        try:
            with open(out_csv, newline="", encoding="utf-8") as f:
                r = csv.reader(f); next(r, None)
                for row in r:
                    if row and row[0]: seen.add(row[0])
        except:
            pass

        idle = 0
        reloads = 0
        rounds  = 0

        def extract_visible_all():
            gained, batch = 0, []
            loc = page.locator('div[data-review-id]')
            n = loc.count()
            for i in range(n):
                b = loc.nth(i)
                rid = b.get_attribute("data-review-id") or ""
                if not rid or rid in seen:
                    continue

                try: auteur = sanitize(b.locator('.d4r55').inner_text())
                except: auteur = ""

                contributions = ""
                try:
                    meta = b.locator('.RfnDt').inner_text()
                    m = re.search(r'(\d[\d\u00A0 ]*)\s*avis', meta)
                    if m: contributions = re.sub(r'\D','', m.group(1))
                except: pass

                note = ""
                try:
                    n1 = b.locator('.DU9Pgb .fontBodyLarge')
                    if n1.count():
                        m0 = re.search(r'(\d+[.,]?\d*)\s*/\s*5', n1.first.inner_text())
                        if m0: note = m0.group(1).replace(',', '.')
                    if not note:
                        n2 = b.locator('[aria-label*="étoiles"], [role="img"]')
                        if n2.count():
                            m2 = re.search(r'(\d+[.,]?\d*)', (n2.first.get_attribute("aria-label") or ""))
                            if m2: note = m2.group(1).replace(',', '.')
                except: pass

                try: date = clean_date(b.locator('.xRkPPb').inner_text())
                except: date = ""
                texte = ""
                try: texte = b.locator('.wiI7pd').inner_text()
                except:
                    try: texte = b.locator('span.wiI7pd, span[class*="wiI7pd"]').inner_text()
                    except: texte = ""

                batch.append([rid, avg, total_expected or "", auteur, contributions, note, date, texte])
                seen.add(rid)
                gained += 1

            if batch:
                with open(out_csv, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerows(batch)
            return gained

        while True:
            rounds += 1

            # Scroll en rafale
            for _ in range(SCROLLS_PER_ROUND):
                scroll_more(page)

            # Extraction
            gained = extract_visible_all()
            print(f"  • Tour {rounds}: +{gained} (écrit {len(seen)})")

            if total_expected and len(seen) >= total_expected:
                print(f"✅ Objectif atteint ({len(seen)}/{total_expected}).")
                break
            if len(seen) >= HARD_CAP:
                print(f"🛑 Limite de sécurité atteinte ({HARD_CAP}).")
                break

            idle = idle + 1 if gained == 0 else 0
            if idle >= IDLE_ROUNDS_LIMIT:
                if reloads >= MAX_RELOADS:
                    print(f"✅ Stabilisé : plus de nouveaux avis (total {len(seen)}).")
                    break
                reloads += 1
                print(f"🔁 Reload #{reloads} — réouverture & refiltres…")
                page = open_reviews(context, URL)
                ensure_filters(page)
                avg2, tot2 = get_hotel_summary(page)
                if avg2: avg = avg2
                if tot2: total_expected = tot2
                idle = 0

        print(f"\n✅ {len(seen)} avis uniques présents dans le CSV → raw_data/avis_google_{HOTEL_NAME}.csv")
        try: browser.close()
        except: pass

if __name__ == "__main__":
    scrape_all()
