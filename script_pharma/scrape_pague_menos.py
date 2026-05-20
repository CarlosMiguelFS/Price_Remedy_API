"""Busca SKUs dos top 15 mais vendidos na Pague Menos via API VTEX publica.
Gera saida JSON com {nome_canonico: {sku, url, name_found, score}}.
"""
import httpx
import json
import time
import sys
import re
import unicodedata
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

DOMAIN = "paguemenos.com.br"

# Top 15 mais vendidos - mesma lista usada para Santa Lucia (perfil de farmacia popular).
MEDS = {
    "Losartana 50mg": ["Losartana 50mg", "Losartana Potassica 50mg"],
    "Dipirona 500mg": ["Dipirona 500mg", "Dipirona Sodica 500mg"],
    "Glifage XR 500mg": ["Glifage XR 500mg", "Metformina 500mg XR"],
    "Neosoro": ["Neosoro"],
    "Tadalafila 5mg": ["Tadalafila 5mg"],
    "Nimesulida 100mg": ["Nimesulida 100mg"],
    "Simeticona 75mg/ml": ["Simeticona 75mg/ml", "Simeticona 75mg gotas", "Luftal 75mg"],
    "Omeprazol 20mg": ["Omeprazol 20mg"],
    "Paracetamol 750mg": ["Paracetamol 750mg"],
    "Hidroclorotiazida 25mg": ["Hidroclorotiazida 25mg"],
    "Buscopan Composto": ["Buscopan Composto"],
    "Dorflex": ["Dorflex"],
    "Microvlar": ["Microvlar"],
    "Addera D3": ["Addera D3", "Addera D3 vitamina"],
    "Ciclo 21": ["Ciclo 21"],
}


def _tokens(s: str):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return [t for t in s.split() if len(t) > 1]


def _score(query: str, product_name: str) -> int:
    if not product_name:
        return 0
    stop = {"mg", "ml", "g", "ui", "mcg", "generico", "comprimido", "comprimidos",
            "capsula", "capsulas", "comp", "cprs", "cps", "de", "do", "da"}
    q_tokens = [t for t in _tokens(query) if t not in stop]
    name_tokens = set(_tokens(product_name))
    score = sum(1 for t in q_tokens if t in name_tokens)
    for t in _tokens(query):
        if any(ch.isdigit() for ch in t) and t in name_tokens:
            score += 1
    return score


def search_vtex(query: str, min_score: int = 1):
    url = f"https://www.{DOMAIN}/api/catalog_system/pub/products/search"
    params = {"ft": query}
    try:
        with httpx.Client(headers=HEADERS, timeout=20) as client:
            resp = client.get(url, params=params)
            if resp.status_code not in (200, 206):
                print(f"  [http {resp.status_code}] {query}", file=sys.stderr)
                return None
            data = resp.json()
            if not data:
                return None
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
            link = best.get("link") or f"https://www.{DOMAIN}/{best.get('linkText','')}/p"
            return {
                "sku": sku,
                "url": link,
                "name_found": best.get("productName"),
                "score": best_score,
            }
    except Exception as e:
        print(f"  [vtex error]: {e}", file=sys.stderr)
        return None


def main():
    print(f"=== Pague Menos ({DOMAIN}) ===")
    results = {}
    for canonical, queries in MEDS.items():
        found = None
        for q in queries:
            found = search_vtex(q)
            if found and found.get("sku"):
                break
            time.sleep(0.3)
        if found and found.get("sku"):
            print(f"  OK   {canonical:30s} -> {found['sku']:>10} [score={found.get('score','?')}] | {found['name_found'][:55]}")
            results[canonical] = found
        else:
            print(f"  MISS {canonical} (queries: {queries})")
        time.sleep(0.4)

    out_path = Path(__file__).parent / "skus_pague_menos.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em {out_path}")
    print(f"\nTotal encontrado: {len(results)}/{len(MEDS)}")


if __name__ == "__main__":
    main()
