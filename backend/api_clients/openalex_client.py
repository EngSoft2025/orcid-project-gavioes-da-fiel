# api_clients/openalex_client.py

import html
from typing import List, Dict
import aiohttp
import unicodedata
import re
import collections
import datetime

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


# Constantes para parsing e consulta de citações
ID_TYPES = {"doi", "pmid", "pmcid", "arxiv"}
CHUNK    = 100

def parse_orcid_data(data: dict) -> tuple[dict[str,int], list[int]]:
    """
    Retorna:
      - ids: dicionário { "<tp>:<valor_do_id>": ano_de_publicacao }
      - no_id_years: lista de anos das obras sem identificador externo válido
    Exemplo de chave em ids: "doi:10.1000/xyz123" → 2018
    """
    ids: dict[str,int] = {}
    no_id_years: list[int] = []

    for group in data.get("group", []) or []:
        for work in group.get("work-summary", []) or []:
            # Extrai ano de publicação (ou 0)
            year = int(
                (work.get("publication-date") or {}).get("year", {}).get("value", 0)
            )
            if not year:
                continue

            # Procura pelo primeiro ID externo do tipo suportado
            found_id = False
            for ext in (work.get("external-ids") or {}).get("external-id", []) or []:
                tp = ext.get("external-id-type", "").lower()
                if tp in ID_TYPES:
                    valor = ext.get("external-id-value", "").strip().lower()
                    if valor:
                        key = f"{tp}:{valor}"
                        ids[key] = year
                        found_id = True
                        break
            if not found_id:
                no_id_years.append(year)

    return ids, no_id_years


def fetch_citations(ids: dict[str,int]) -> dict[str,int]:
    """
    Recebe um dicionário { "<tp>:<id>": ano } e retorna { "<tp>:<id>": número_de_citações },
    fazendo requisições ao OpenAlex em lotes de até CHUNK identificadores.
    """
    by_type: dict[str,list[str]] = collections.defaultdict(list)
    for key in ids:
        tp, val = key.split(":", 1)
        by_type[tp].append(val)

    citations: dict[str,int] = {}

    for tp, vals in by_type.items():
        local: dict[str,int] = {}
        # Divide em pedaços (chunks) de tamanho CHUNK
        for i in range(0, len(vals), CHUNK):
            chunk = vals[i : i + CHUNK]
            params = {
                "filter":    f"{tp}:{'|'.join(chunk)}",
                "per-page":  len(chunk),
                "select":    f"{tp},cited_by_count"
            }
            resp = requests.get("https://api.openalex.org/works", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for w in data.get("results", []):
                raw = (w.get(tp) or w.get("ids", {}).get(tp) or "")
                # Caso raw seja algo como "https://doi.org/10.1000/xyz123", limpa o prefixo
                normalized = raw.lower().lstrip("https://doi.org/")
                key = f"{tp}:{normalized}"
                local[key] = w.get("cited_by_count", 0)

        # Garante que cada ID apareça no dicionário, mesmo que não tenha sido retornado
        for v in vals:
            key = f"{tp}:{v}"
            local.setdefault(key, 0)

        citations.update(local)

    return citations

def count_by_year(
    ids: dict[str,int],
    no_id_years: list[int],
    citations: dict[str,int]
) -> tuple[list[int], list[int], list[int]]:
    """
    Agrupa publicações e citações por ano. Retorna três listas: anos, qtd_publicações, qtd_citações.
    """
    pubs = collections.Counter()
    cites = collections.Counter()

    for key, year in ids.items():
        pubs[year] += 1
        cites[year] += citations.get(key, 0)
    for year in no_id_years:
        pubs[year] += 1

    years = sorted(pubs)
    pubs_y = [pubs[y] for y in years]
    cites_y = [cites[y] for y in years]
    return years, pubs_y, cites_y

def compute_metrics(
    years: list[int],
    pubs_y: list[int],
    cites_y: list[int],
    ids: dict[str,int],
    no_id_years: list[int],
    citations: dict[str,int]
) -> dict[str, float | int]:
    """
    Calcula métricas a partir dos arrays de anos, publicações, citações e dos dicionários de IDs/citações.
    """
    works_count     = sum(pubs_y)
    citations_count = sum(cites_y)

    average_citations = (citations_count / works_count) if works_count else 0.0

    current_year = datetime.date.today().year
    cutoff_year  = current_year - 2
    recent_works = sum(pub for yr, pub in zip(years, pubs_y) if yr >= cutoff_year)
    recent_cites = sum(cit for yr, cit in zip(years, cites_y) if yr >= cutoff_year)
    impact_factor_2y = (recent_cites / recent_works) if recent_works else 0.0

    all_cits = list(citations.values()) + [0]*len(no_id_years)
    all_cits.sort(reverse=True)

    h = 0
    for i, c in enumerate(all_cits, 1):
        if c >= i:
            h = i
        else:
            break

    i10 = sum(1 for c in all_cits if c >= 10)
    most_cited = all_cits[0] if all_cits else 0

    impact_factor_2y = float(f"{impact_factor_2y:.2f}")
    average_citations = float(f"{average_citations:.2f}")

    return {
        "total_publicacoes":     works_count,
        "total_citacoes":        citations_count,
        "media_citacoes":        average_citations,
        "fator_de_impacto":      impact_factor_2y,
        "h_index":               h,
        "i10_index":             i10,
        "pesquisa_mais_citada":  most_cited
    }
