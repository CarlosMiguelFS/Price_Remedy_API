"""Tenta scrape Drogasil via Playwright + input de busca da home (anti-bot tolera essa rota)."""
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

MEDS_DROGASIL = {
    "Simeticona 125mg Medley": ["Simeticona 125mg Medley"],
    "Dipirona 1g Cimed": ["Dipirona 1g Cimed"],
    "Cimegripe": ["Cimegripe"],
    "Glyxambi": ["Glyxambi"],
    "Tadalafila 5mg EMS": ["Tadalafila 5mg EMS"],
    "Sertralina 50mg Medley": ["Sertralina 50mg Medley"],
    "Glifage XR 500mg": ["Glifage XR 500mg"],
    "Rosuvastatina 20mg Althaia": ["Rosuvastatina 20mg Althaia"],
    "Durateston": ["Durateston"],
    "Domperidona 10mg EMS": ["Domperidona 10mg EMS"],
    "Fluconazol 150mg Cimed": ["Fluconazol 150mg Cimed"],
    "Nimesulida 100mg Eurofarma": ["Nimesulida 100mg Eurofarma"],
    "Atenolol 25mg Medley": ["Atenolol 25mg Medley"],
    "Loratadina 10mg Cimed": ["Loratadina 10mg Cimed"],
    "Pantoprazol 40mg Medley": ["Pantoprazol 40mg Medley"],
}


def main():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        ctx = browser.new_context(
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = ctx.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Vai pra home pra ganhar cookies/sessao
        page.goto("https://www.drogasil.com.br", timeout=60000)
        page.wait_for_timeout(4500)

        title = page.title()
        print(f"[home] title={title[:60]}", file=sys.stderr)
        if "Access Denied" in title:
            print("DROGASIL BLOQUEOU HOME. Aborting.", file=sys.stderr)
            browser.close()
            return results

        for canonical, queries in MEDS_DROGASIL.items():
            found = None
            for q in queries:
                try:
                    # Volta pra home, preenche input, da Enter
                    if "drogasil.com.br" not in page.url or "/search" not in page.url:
                        page.goto("https://www.drogasil.com.br", timeout=45000)
                        page.wait_for_timeout(2500)
                    # encontra o input
                    inp = page.query_selector('input[placeholder*="Busca" i]') or \
                          page.query_selector('input[type="search"]')
                    if not inp:
                        print(f"  [drogasil] input nao encontrado para '{q}'", file=sys.stderr)
                        continue
                    inp.click()
                    inp.fill("")
                    inp.type(q, delay=50)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(5000)
                    # extrai produtos
                    cards = page.evaluate("""() => {
                        const anchors = Array.from(document.querySelectorAll('a[href*=".html"]'));
                        const out = [];
                        for (const a of anchors) {
                            const h = a.getAttribute('href') || '';
                            if (h.includes('/bulas/') || h.includes('/medicamentos/') ||
                                h.includes('saude.html') || h.includes('beleza.html') ||
                                h.includes('vitaminas-e-suplementos.html') ||
                                h.includes('cosmeticos.html')) continue;
                            const m = h.match(/-([0-9]{4,8})\\.html$/);
                            const text = (a.innerText || a.getAttribute('title') || '').trim().slice(0,120);
                            out.push({href: h, sku: m ? m[1] : null, text});
                        }
                        return out.slice(0, 30);
                    }""")
                    # escolhe primeiro com SKU
                    for c in cards:
                        if c.get("sku"):
                            href = c["href"]
                            if not href.startswith("http"):
                                href = "https://www.drogasil.com.br" + href
                            found = {
                                "sku": c["sku"],
                                "url": href,
                                "name_found": c["text"],
                            }
                            break
                    if not found:
                        # se nenhum tem sku, pega o primeiro link com /<nome>.html que nao seja institucional
                        for c in cards:
                            href = c["href"]
                            if href.endswith(".html"):
                                if not href.startswith("http"):
                                    href = "https://www.drogasil.com.br" + href
                                found = {
                                    "sku": None,
                                    "url": href,
                                    "name_found": c["text"],
                                }
                                break
                except Exception as e:
                    print(f"  [drogasil error '{q}']: {e}", file=sys.stderr)
                if found:
                    break
                time.sleep(0.6)

            if found and found.get("sku"):
                print(f"  OK   {canonical} -> {found['sku']} | {found['name_found'][:50]}")
                results[canonical] = found
            elif found:
                print(f"  URL  {canonical} -> (sem sku) {found['url']}")
                results[canonical] = found
            else:
                print(f"  MISS {canonical}")
            time.sleep(1.0)

        browser.close()

    out_path = Path(__file__).parent / "skus_drogasil.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em {out_path}")


if __name__ == "__main__":
    main()
