# scripts/scrape_google_maps_hotel_4.py — v2 anti-palier
import csv, os, re, time, random
from contextlib import suppress
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ===== À PERSONNALISER =====
HOTEL_NAME = "BW_Litteraire_Marcel_Ayme"
URL = ("https://www.google.com/maps/place/H%C3%B4tel+Litt%C3%A9raire+Marcel+Aym%C3%A9,+BW+Premier+Collection/"
       "@48.8864947,2.3330798,470m/data=!3m1!1e3!4m12!3m11!1s0x47e66e5aaa9c27e7:0x4041da69c3028e9a!"
       "5m3!1s2025-08-19!4m1!1i2!8m2!3d48.8864912!4d2.3356547!9m1!1b1!16s%2Fg%2F1tfzg1sp?entry=ttu")
# ===========================

# ===== Réglages vitesse/stabilité =====
HEADLESS = True
SCROLLS_PER_ROUND   = 36            # + de scrolls par rafale
SCROLL_PAUSE        = (0.004, 0.012)
IDLE_ROUNDS_LIMIT   = 6             # rechargement plus agressif
MAX_RELOADS         = 6
HARD_CAP            = 20000

# ⚡ Laisse les styles (meilleure virtualisation) ; on bloque images/médias/polices
BLOCK_RESOURCE_TYPES = {"image", "media", "font"}

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
        page.wait_for_timeout(300)
        for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
            b = page.locator(f'button:has-text("{txt}")')
            if b.count():
                b.first.click(timeout=1200); page.wait_for_timeout(300); return
        for fr in page.frames:
            with suppress(Exception):
                for txt in ["Tout accepter","J'accepte","Accepter tout","Accepter"]:
                    el = fr.locator(f'button:has-text("{txt}")')
                    if el.count():
                        el.first.click(timeout=1200); page.wait_for_timeout(300); return

def ensure_filters(page):
    # Source = Google
    with suppress(Exception):
        chip = page.locator("button:has-text('Tous les avis'), button:has-text('Google'), button:has-text('Tripadvisor')").first
        if chip.count() and "Google" not in (chip.inner_text() or ""):
            chip.click()
            menu = page.locator("div[role='menu'], div[role='listbox']")
            g = menu.locator("div:has-text('Google'), span:has-text('Google')")
            if g.count(): g.first.click(); page.wait_for_timeout(200); print("🔧 Source d'avis = Google")
    # Tri = Les plus récents
    with suppress(Exception):
        btn = page.locator('button[aria-label*="Trier"], button:has-text("Avis les plus"), button:has-text("Trier")')
        if btn.count():
            btn.first.click()
            page.locator('div[role="menu"] div:has-text("Les plus récents")').first.click()
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
    avg, total = "", 0
    with suppress(Exception):
        m = re.search(r'(\d+[.,]?\d*)', (page.locator('[aria-label*="étoiles sur 5"]').first.get_attribute("aria-label") or ""))
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
    """Marque le vrai conteneur scrollable des avis avec [data-scroller=1]."""
    page.evaluate("""() => {
        const isScrollable = el => el && (el.scrollHeight - el.clientHeight) > 20 &&
                                   getComputedStyle(el).overflowY !== 'visible';
        // 1) piste connue (classes Maps)
        let sc = document.querySelector('div[aria-label*="Avis"] .m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd');
        // 2) sinon, remonter depuis une carte d'avis
        if (!isScrollable(sc)) {
          const cards = document.querySelectorAll('div[data-review-id]');
          if (cards.length) {
            let el = cards[cards.length-1].parentElement;
            while (el && !isScrollable(el)) el = el.parentElement;
            sc = el || sc;
          }
        }
        // 3) fallback : plus grand scrollable de la page
        if (!isScrollable(sc)) {
          const cands = Array.from(document.querySelectorAll('div')).filter(isScrollable);
          sc = cands.sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight))[0]
               || document.scrollingElement || document.body;
        }
        sc.setAttribute('data-scroller','1');
    }""")

def open_reviews(context, url):
    page = context.new_page(); page.set_default_timeout(8000)
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    accept_consent(page)
    with suppress(PWTimeout): page.wait_for_load_state("networkidle", timeout=6000)
    with suppress(Exception): page.get_by_role("tab", name=re.compile("Avis", re.IGNORECASE)).click()
    with suppress(Exception): page.locator('div[role="tab"]:has-text("Avis")').first.click()
    page.wait_for_selector('div[data-review-id]', timeout=15000)
    with suppress(Exception): page.evaluate("document.body.style.zoom='0.85'")
    ensure_filters(page)
    mark_scroller(page)
    return page

def deep_scroll(page, steps=28, mode="burst"):
    """Scroll direct sur le conteneur des avis (débloque les plateaux)."""
    page.evaluate(
        """(p) => {
            const { steps, mode } = p;
            const sc = document.querySelector('[data-scroller="1"]')
                   || document.scrollingElement || document.body;
            const H  = sc.clientHeight;
            const dy = Math.max(200, Math.ceil(H*0.92));

            if (mode === 'jump') {
                // sauts + micro "secousses" pour réveiller la virtualisation
                for (let i=0;i<steps;i++) {
                    sc.scrollBy(0, dy);
                    sc.scrollBy(0, -40);
                    sc.scrollBy(0, +120);
                }
            } else {
                for (let i=0;i<steps;i++) sc.scrollBy(0, dy);
            }

            // pousser un coup à fond si on est proche du bas actuel
            if (sc.scrollHeight - sc.scrollTop - H < H*0.5) {
                sc.scrollTop = sc.scrollHeight;
            }
        }""",
        {"steps": steps, "mode": mode}
    )
    page.wait_for_timeout(120)  # petite pause pour laisser loader


def scroll_more(page):
    with suppress(Exception):
        last = page.locator('div[data-review-id]').last()
        last.scroll_into_view_if_needed()
    with suppress(Exception): page.mouse.wheel(0, 9000)
    with suppress(Exception): page.keyboard.press("PageDown")
    rnd(*SCROLL_PAUSE)

def write_header_if_needed(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "review_id","note_moyenne","nb_avis_total","auteur","contributions","note","date","avis"
            ])

def extract_visible_batch(page):
    return page.evaluate("""() => {
        const nodes = [...document.querySelectorAll('div[data-review-id]')];
        return nodes.map(n => {
            const rid = n.getAttribute('data-review-id') || '';
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
            return { rid, auteur, contributions, note, date, avis };
        });
    }""")

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
            viewport={"width": 1600, "height": 2000},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
        )

        # Bloquer ressources lourdes
        def route_handler(route):
            try:
                if route.request.resource_type in BLOCK_RESOURCE_TYPES:
                    return route.abort()
            except Exception:
                pass
            return route.continue_()
        context.route("**/*", route_handler)

        print("🧭 Ouverture de la page Google Maps…")
        page = open_reviews(context, URL)
        avg, total_expected = get_hotel_summary(page)
        print(f"📊 Résumé hôtel → note_moyenne={avg} | nb_avis_total={total_expected or 'inconnu'}")
        print("🧭 Conteneur scrollable détecté.")
        print("🔽 Défilement + collecte (turbo)…")

        # Dédup à partir du CSV existant
        seen = set()
        with suppress(Exception):
            with open(out_csv, newline="", encoding="utf-8") as f:
                r = csv.reader(f); next(r, None)
                for row in r:
                    if row and row[0]: seen.add(row[0])

        idle = reloads = rounds = 0
        plateau_rounds = 0

        while True:
            rounds += 1

            # Scroll rafale + scroll profond si plateau
            for _ in range(SCROLLS_PER_ROUND):
                scroll_more(page)
            if plateau_rounds >= 1:
                deep_scroll(page, steps=28, mode="burst")
            if plateau_rounds >= 3:          # si le plateau persiste, mode "jump"
                deep_scroll(page, steps=18, mode="jump")

            # Extraction en lot
            raw_batch = []
            with suppress(Exception): raw_batch = extract_visible_batch(page)

            gained, rows = 0, []
            for item in (raw_batch or []):
                rid = item.get("rid") or ""
                if not rid or rid in seen: continue
                auteur = sanitize(item.get("auteur",""))
                contributions = re.sub(r"\D","", item.get("contributions","") or "")
                note = (item.get("note") or "").replace(",", ".")
                date = clean_date(item.get("date",""))
                texte = sanitize(item.get("avis",""))
                rows.append([rid, avg, total_expected or "", auteur, contributions, note, date, texte])
                seen.add(rid); gained += 1

            if rows:
                with open(out_csv, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerows(rows)

            print(f"  • Tour {rounds}: +{gained} (écrit {len(seen)})")

            if total_expected and len(seen) >= total_expected: print(f"✅ Objectif atteint ({len(seen)}/{total_expected})."); break
            if len(seen) >= HARD_CAP: print(f"🛑 Limite de sécurité atteinte ({HARD_CAP})."); break

            plateau_rounds = 0 if gained else (plateau_rounds + 1)
            idle = idle + 1 if gained == 0 else 0

            if idle >= IDLE_ROUNDS_LIMIT:
                if reloads >= MAX_RELOADS:
                    print(f"✅ Stabilisé : plus de nouveaux avis (total {len(seen)})."); break
                reloads += 1
                print(f"🔁 Reload #{reloads} — réouverture & refiltres…")
                page = open_reviews(context, URL)      # remonte aussi le marqueur [data-scroller]
                ensure_filters(page); mark_scroller(page)
                with suppress(Exception):
                    avg2, tot2 = get_hotel_summary(page)
                    if avg2: avg = avg2
                    if tot2: total_expected = tot2
                idle = plateau_rounds = 0

        print(f"\n✅ {len(seen)} avis uniques présents dans le CSV → raw_data/avis_google_{HOTEL_NAME}.csv")
        with suppress(Exception): browser.close()

if __name__ == "__main__":
    scrape_all()
