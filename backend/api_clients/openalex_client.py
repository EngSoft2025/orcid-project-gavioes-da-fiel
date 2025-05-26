# api_clients/openalex_client.py

import html
from typing import List, Dict

import requests
from fastapi import HTTPException

# OpenAlex API configuration
OA_WORKS_URL = "https://api.openalex.org/works"
OA_PER_PAGE = 200
OA_TIMEOUT = 20
OA_MAILTO = "gabrielabreu571@gmail.com"
OA_HEADERS = {
    "User-Agent": f"orcid-citations/1.0 (mailto:{OA_MAILTO})"
}


def fetch_works_openalex(orcid_id: str) -> List[Dict]:
    """
    Busca todas as obras de um autor (por ORCID) no OpenAlex e retorna
    uma lista de dicts com { title, year, doi, cited_by_count }.
    """
    cursor = "*"
    works: List[Dict] = []

    while True:
        params = {
            "filter":    f"author.orcid:{orcid_id}",
            "per-page":  OA_PER_PAGE,
            "cursor":    cursor,
            "mailto":    OA_MAILTO
        }
        resp = requests.get(OA_WORKS_URL, params=params, headers=OA_HEADERS, timeout=OA_TIMEOUT)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao acessar OpenAlex: {resp.status_code}"
            )
        payload = resp.json()

        for item in payload.get("results", []):
            works.append({
                "title":            html.unescape(item.get("display_name", "Sem título")),
                "year":             item.get("publication_year") or 0,
                "doi":              (item.get("ids") or {}).get("doi"),
                "cited_by_count":   item.get("cited_by_count", 0),
            })

        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not cursor:
            break

    return works


def format_works_from_openalex(orcid_id: str) -> List[Dict]:
    """
    Busca todas as obras de um autor (por ORCID) no OpenAlex e retorna
    uma lista de dicts com:
      - title
      - year
      - doi
      - url
      - type
      - citations
      - coauthors: List[ { name, orcid } ]
    Inclui coautores (author.orcid) e número de citações.
    """
    cursor = "*"
    works: List[Dict] = []

    while True:
        params = {
            "filter":    f"author.orcid:{orcid_id}",
            "per-page":  OA_PER_PAGE,
            "cursor":    cursor,
            "mailto":    OA_MAILTO
        }
        resp = requests.get(OA_WORKS_URL, params=params, headers=OA_HEADERS, timeout=OA_TIMEOUT)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao acessar OpenAlex: {resp.status_code}"
            )
        payload = resp.json()

        for item in payload.get("results", []):
            # Extrai coautores com ORCID (se houver)
            coauthors = []
            for auth in item.get("authorships", []):
                author = auth.get("author", {}) or {}
                name = author.get("display_name")
                author_orcid = author.get("orcid")
                if name:
                    coauthors.append({
                        "name": name,
                        "orcid": author_orcid
                    })

            works.append({
                "title":      html.unescape(item.get("display_name", "Sem título")),
                "year":       item.get("publication_year") or "----",
                "doi":        (item.get("ids") or {}).get("doi"),
                "url":        (item.get("ids") or {}).get("doi"),
                "type":       item.get("type") or "desconhecido",
                "citations":  item.get("cited_by_count", 0),
                "coauthors":  coauthors
            })

        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not cursor:
            break

    return works
