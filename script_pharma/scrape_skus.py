"""
Scraper de SKUs por farmacia a partir do markdown de medicamentos mais vendidos.
Gera um JSON (skus_resultado.json) com {farmacia: {nome_med: {sku, url, name_found}}}.
"""
import httpx
import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

# Chave canonica = como vai aparecer no d_para final.
# Valor = lista de termos de busca a tentar (do mais especifico ao mais generico).
MEDS = {
    "drogasil": {
        "Simeticona 125mg Medley": ["Simeticona 125mg Medley", "Simeticona 125mg generico"],
        "Dipirona 1g Cimed": ["Dipirona 1g Cimed", "Dipirona Monoidratada 1g Cimed"],
        "Cimegripe": ["Cimegripe"],
        "Glyxambi": ["Glyxambi", "Glyxambi 10mg 5mg"],
        "Tadalafila 5mg EMS": ["Tadalafila 5mg EMS", "Tadalafila 5mg generico EMS"],
        "Sertralina 50mg Medley": ["Cloridrato de Sertralina 50mg Medley", "Sertralina 50mg Medley"],
        "Glifage XR 500mg": ["Glifage XR 500mg"],
        "Rosuvastatina 20mg Althaia": ["Rosuvastatina 20mg Althaia", "Rosuvastatina Calcica 20mg Althaia"],
        "Durateston": ["Durateston", "Durateston 250mg"],
        "Domperidona 10mg EMS": ["Domperidona 10mg EMS", "Domperidona 10mg generico"],
        "Fluconazol 150mg Cimed": ["Fluconazol 150mg Cimed", "Fluconazol 150mg generico"],
        "Nimesulida 100mg Eurofarma": ["Nimesulida 100mg Eurofarma", "Nimesulida 100mg generico"],
        "Atenolol 25mg Medley": ["Atenolol 25mg Medley", "Atenolol 25mg generico"],
        "Loratadina 10mg Cimed": ["Loratadina 10mg Cimed", "Loratadina 10mg generico"],
        "Pantoprazol 40mg Medley": ["Pantoprazol 40mg Medley", "Pantoprazol 40mg generico"],
    },
    "drogaria_sao_paulo": {
        "Mounjaro 2,5mg": ["Mounjaro 2,5mg", "Mounjaro 2.5mg tirzepatida"],
        "Mounjaro 5mg": ["Mounjaro 5mg tirzepatida"],
        "Mounjaro 7,5mg": ["Mounjaro 7,5mg", "Mounjaro 7.5mg tirzepatida"],
        "Tadalafila 5mg EMS": ["Tadalafila 5mg EMS"],
        "Glifage XR 500mg": ["Glifage XR 500mg"],
        "Wegovy 2,4mg": ["Wegovy 2,4mg", "Wegovy 2.4mg semaglutida"],
        "Wegovy 0,25mg": ["Wegovy 0,25mg", "Wegovy 0.25mg semaglutida"],
        "Dipirona 1g Cimed": ["Dipirona 1g Cimed", "Dipirona Monoidratada 1g Cimed"],
        "Mecobe 1000mcg": ["Mecobe 1000mcg", "Mecobe mecobalamina"],
        "Dipirona 500mg Prati Donaduzzi": ["Dipirona 500mg Prati Donaduzzi", "Dipirona 500mg Prati"],
        "Omeprazol 20mg Cimed": ["Omeprazol 20mg Cimed"],
        "Glyxambi": ["Glyxambi"],
        "Cetoprofeno 150mg Eurofarma": ["Cetoprofeno 150mg Eurofarma"],
        "Nimesulida 100mg Cimed": ["Nimesulida 100mg Cimed"],
        "Tadalafila 5mg Eurofarma": ["Tadalafila 5mg Eurofarma"],
    },
    "pacheco": {
        "Glifage XR 500mg": ["Glifage XR 500mg"],
        "Mounjaro 5mg": ["Mounjaro 5mg tirzepatida"],
        "Mecobe 1000mcg": ["Mecobe 1000mcg"],
        "Glyxambi": ["Glyxambi"],
        "Nimesulida 100mg Cimed": ["Nimesulida 100mg Cimed"],
        "Tadalafila 5mg EMS": ["Tadalafila 5mg EMS"],
        "Fluconazol 150mg Cimed": ["Fluconazol 150mg Cimed"],
        "Rosuvastatina 20mg EMS": ["Rosuvastatina 20mg EMS"],
        "Prednisolona 20mg EMS": ["Prednisolona 20mg EMS"],
        "Ibuprofeno 600mg Prati Donaduzzi": ["Ibuprofeno 600mg Prati Donaduzzi"],
        "Neosoro": ["Neosoro"],
        "Aradois 50mg": ["Aradois 50mg", "Aradois Losartana 50mg"],
        "Pantoprazol 40mg Medley": ["Pantoprazol 40mg Medley"],
        "Aerolin": ["Aerolin", "Aerolin salbutamol"],
        "Wegovy 1mg": ["Wegovy 1mg", "Wegovy 1mg semaglutida"],
    },
    "indiana": {
        "Rosuvastatina 20mg EMS": ["Rosuvastatina 20mg EMS"],
        "Hidroclorotiazida 25mg EMS": ["Hidroclorotiazida 25mg EMS"],
        "Nimesulida 100mg EMS": ["Nimesulida 100mg EMS"],
        "Tadalafila 20mg EMS": ["Tadalafila 20mg EMS"],
        "Apixabana 2,5mg EMS": ["Apixabana 2,5mg EMS", "Apixabana 2.5mg EMS"],
        "Novalgina Flash 1g": ["Novalgina Flash 1g"],
        "Leite de Magnesia EnoMagno": ["Leite de Magnesia EnoMagno", "Leite de Magnesia"],
        "Sal de Fruta Eno Limao": ["Sal de Fruta Eno Limao"],
        "Paracetamol 750mg Cimed": ["Paracetamol 750mg Cimed"],
        "Metoprolol 25mg Cimed": ["Metoprolol 25mg Cimed", "Succinato de Metoprolol 25mg Cimed"],
        "Tadalafila 20mg Cimed": ["Tadalafila 20mg Cimed"],
        "Nimesulida 100mg Cimed": ["Nimesulida 100mg Cimed"],
        "Loratadina 10mg Cimed": ["Loratadina 10mg Cimed"],
        "Dipirona 500mg EMS": ["Dipirona 500mg EMS", "Dipirona Sodica 500mg EMS"],
        "Losartana 50mg EMS": ["Losartana 50mg EMS", "Losartana Potassica 50mg EMS"],
    },
    "santa_lucia": {
        "Losartana 50mg": ["Losartana 50mg", "Losartana Potassica 50mg"],
        "Dipirona 500mg": ["Dipirona 500mg", "Dipirona Sodica 500mg"],
        "Glifage XR 500mg": ["Glifage XR 500mg", "Metformina 500mg XR"],
        "Neosoro": ["Neosoro"],
        "Tadalafila 5mg": ["Tadalafila 5mg"],
        "Nimesulida 100mg": ["Nimesulida 100mg"],
        "Simeticona 75mg/ml": ["Simeticona 75mg/ml", "Simeticona 75mg gotas"],
        "Omeprazol 20mg": ["Omeprazol 20mg"],
        "Paracetamol 750mg": ["Paracetamol 750mg"],
        "Hidroclorotiazida 25mg": ["Hidroclorotiazida 25mg"],
        "Buscopan Composto": ["Buscopan Composto"],
        "Dorflex": ["Dorflex"],
        "Microvlar": ["Microvlar"],
        "Addera D3": ["Addera D3", "Addera D3 vitamina"],
        "Ciclo 21": ["Ciclo 21"],
    },
}

VTEX_DOMAINS = {
    "drogaria_sao_paulo": "drogariasaopaulo.com.br",
    "pacheco": "drogariaspacheco.com.br",
    "indiana": "farmaciaindiana.com.br",
    "santa_lucia": "santaluciadrogarias.com.br",
}


def _tokens(s: str):
    import re, unicodedata
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return [t for t in s.split() if len(t) > 1]


def _score(query: str, product_name: str) -> int:
    """Quantos tokens nao-genericos da query aparecem no nome do produto."""
    if not product_name:
        return 0
    stop = {"mg", "ml", "g", "ui", "mcg", "generico", "comprimido", "comprimidos",
            "capsula", "capsulas", "comp", "cprs", "cps", "de", "do", "da"}
    q_tokens = [t for t in _tokens(query) if t not in stop]
    name_tokens = set(_tokens(product_name))
    score = sum(1 for t in q_tokens if t in name_tokens)
    # bonus se dosagens (que tem numero) baterem
    for t in _tokens(query):
        if any(ch.isdigit() for ch in t) and t in name_tokens:
            score += 1
    return score


def search_vtex(domain: str, query: str, min_score: int = 1):
    """Busca produto via API publica VTEX. Retorna o melhor match acima de min_score, ou None."""
    url = f"https://www.{domain}/api/catalog_system/pub/products/search"
    params = {"ft": query}
    try:
        with httpx.Client(headers=HEADERS, timeout=20) as client:
            resp = client.get(url, params=params)
            if resp.status_code not in (200, 206):
                return None
            data = resp.json()
            if not data:
                return None
            # escolhe o produto com maior score de palavras-chave em comum
            best = None
            best_score = -1
            for prod in data:
                name = prod.get("productName", "")
                s = _score(query, name)
                if s > best_score:
                    best_score = s
                    best = prod
            if best is None or best_score < min_score:
                return None
            items = best.get("items", [])
            sku = items[0].get("itemId") if items else None
            link = best.get("link") or f"https://www.{domain}/{best.get('linkText','')}/p"
            return {
                "sku": sku,
                "url": link,
                "name_found": best.get("productName"),
                "score": best_score,
            }
    except Exception as e:
        print(f"  [vtex error {domain}]: {e}", file=sys.stderr)
        return None


def scrape_vtex_pharmacies(meds_by_pharm: dict) -> dict:
    results = {}
    for pharm, meds in meds_by_pharm.items():
        if pharm not in VTEX_DOMAINS:
            continue
        domain = VTEX_DOMAINS[pharm]
        print(f"\n=== {pharm} ({domain}) ===")
        results[pharm] = {}
        for canonical, queries in meds.items():
            found = None
            for q in queries:
                found = search_vtex(domain, q)
                if found and found.get("sku"):
                    break
                time.sleep(0.3)
            if found and found.get("sku"):
                print(f"  OK   {canonical} -> {found['sku']} [score={found.get('score','?')}] | {found['name_found'][:60]}")
                results[pharm][canonical] = found
            else:
                print(f"  MISS {canonical} (queries tentadas: {queries})")
            time.sleep(0.4)
    return results


def scrape_drogasil(meds: dict) -> dict:
    """Drogasil tem anti-bot na API. Usa Playwright pra acessar a pagina de busca."""
    domain = "drogasil.com.br"
    results = {}
    print(f"\n=== drogasil ({domain}) ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            locale="pt-BR",
            user_agent=HEADERS["User-Agent"],
        )
        page = context.new_page()
        # Visita home primeiro pra warm-up de cookies/anti-bot
        page.goto("https://www.drogasil.com.br", timeout=60000)
        page.wait_for_timeout(3000)

        for canonical, queries in meds.items():
            found = None
            for q in queries:
                try:
                    search_url = f"https://www.drogasil.com.br/search?w={httpx.QueryParams({'q':q})}"
                    # simpler: their search uses ?q= or path
                    search_url = f"https://www.drogasil.com.br/search?w={q.replace(' ', '+')}"
                    page.goto(search_url, timeout=45000)
                    page.wait_for_timeout(2500)
                    # produtos tem links no formato /<slug>-<sku>.html
                    anchors = page.eval_on_selector_all(
                        "a[href$='.html']",
                        "els => els.map(e => e.getAttribute('href'))"
                    )
                    sku = None
                    href = None
                    name_found = None
                    for h in anchors:
                        if not h or "/search" in h:
                            continue
                        # padrao: /produto-slug-1234567.html
                        base = h.rsplit("/", 1)[-1].replace(".html", "")
                        last_seg = base.rsplit("-", 1)[-1]
                        if last_seg.isdigit() and len(last_seg) >= 4:
                            sku = last_seg
                            href = h if h.startswith("http") else f"https://www.drogasil.com.br{h}"
                            name_found = base
                            break
                    if sku:
                        found = {"sku": sku, "url": href, "name_found": name_found}
                        break
                except Exception as e:
                    print(f"  [drogasil error '{q}']: {e}", file=sys.stderr)
                time.sleep(0.5)

            if found:
                print(f"  OK   {canonical} -> {found['sku']} | {found['name_found'][:50]}")
                results[canonical] = found
            else:
                print(f"  MISS {canonical} (queries: {queries})")
            time.sleep(0.6)

        browser.close()
    return results


def main():
    out = {}
    # roda VTEX primeiro (rapido)
    vtex_results = scrape_vtex_pharmacies(MEDS)
    out.update(vtex_results)

    # depois drogasil (lento por causa do playwright)
    if "drogasil" in MEDS:
        out["drogasil"] = scrape_drogasil(MEDS["drogasil"])

    out_path = Path(__file__).parent / "skus_resultado.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em {out_path}")

    # resumo
    print("\n--- RESUMO ---")
    for pharm, meds in out.items():
        total = len(MEDS.get(pharm, {}))
        achados = len(meds)
        print(f"  {pharm}: {achados}/{total}")


if __name__ == "__main__":
    main()
