#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lista publicações de um ORCID ordenadas por nº de citações (OpenAlex).
"""

import requests
import sys
import html
from typing import List, Tuple

OA_WORKS_URL = "https://api.openalex.org/works"
PER_PAGE = 200           # máximo permitido
TIMEOUT  = 20
MAILTO   = "jujuorlando5@gmail.com"

HEADERS  = {
    # bom-tom: declare sua app + e-mail no User-Agent
    "User-Agent": f"orcid-citations/1.0 (mailto:{MAILTO})"
}


def fetch_works_openalex(orcid: str) -> List[Tuple[str, int, str, int]]:
    """Retorna [(title, year, doi_url, cited_by_count)]."""
    cursor = "*"
    all_works: List[Tuple[str, int, str, int]] = []

    while True:
        params = {
            "filter": f"author.orcid:{orcid}",
            "per-page": PER_PAGE,
            "cursor": cursor,
            "mailto": MAILTO         # <- identifica a requisição
            # sem 'select=' para evitar erros de campo
        }
        r = requests.get(OA_WORKS_URL, params=params,
                         headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 403:
            raise RuntimeError("OpenAlex devolveu 403. "
                               "Verifique se o parâmetro 'mailto' contém um e-mail válido.")
        if r.status_code != 200:
            raise RuntimeError(f"OpenAlex erro {r.status_code}")

        payload = r.json()
        for w in payload["results"]:
            title = html.unescape(w.get("display_name") or "Sem título")
            year  = w.get("publication_year") or 0
            doi   = (w.get("ids") or {}).get("doi") or "DOI indisponível"
            cites = w.get("cited_by_count", 0)
            all_works.append((title, year, doi, cites))

        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not cursor:
            break
    return all_works


def main():
    orcid = (sys.argv[1] if len(sys.argv) > 1
             else input("ORCID iD (0000-0000-0000-0000): ").strip())

    print("\nBuscando publicações na OpenAlex…")
    works = fetch_works_openalex(orcid)
    if not works:
        print("Nenhuma obra encontrada.")
        return

    works.sort(key=lambda w: w[3], reverse=True)   # ordena por citações

    print(f"\n{len(works)} publicações de {orcid} (ordenadas por citações):\n")
    for title, year, doi, cites in works:
        print(f"● {title} ({year}) — {cites} citações")
        print(f"  DOI: {doi}")
    print()


if __name__ == "__main__":
    main()
