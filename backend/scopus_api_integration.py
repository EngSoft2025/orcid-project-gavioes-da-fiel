# scopus api key:	a58e0338deeb28109969b118fded896b

import os
import sys
import requests
from requests.exceptions import HTTPError
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import argparse

# --- Carrega sua chave da env var SCOPUS_API_KEY ---
SCOPUS_KEY = "a58e0338deeb28109969b118fded896b"

BASE_URL = "https://api.elsevier.com"
HEADERS = {
    "Accept": "application/json",
    "X-ELS-APIKey": SCOPUS_KEY
}
TIMEOUT = 10

def create_session(retries=5, backoff_factor=1.0,
                   status_forcelist=(429, 500, 502, 503, 504)):
    """Configura uma Session com retry e backoff exponencial."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SESSION = create_session()

def get_author_profile(orcid=None, author_id=None):
    """
    Recupera perfil completo de um autor via ORCID ou Scopus Author ID.
    Retorna um dict com nome, afiliação, métricas, áreas e período de publicação.
    """
    if author_id:
        endpoint = f"{BASE_URL}/content/author/author_id/{author_id}"
    else:
        endpoint = f"{BASE_URL}/content/author/orcid/{orcid}"
    params = {"view": "ENHANCED"}

    try:
        resp = SESSION.get(endpoint, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except HTTPError as e:
        if e.response.status_code == 401:
            print("401 Unauthorized: verifique sua Scopus API Key em SCOPUS_API_KEY", file=sys.stderr)
        else:
            print(f"HTTPError ({e.response.status_code}): {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Erro de conexão: {e}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()["author-retrieval-response"][0]
    core = data.get("coredata", {})
    profile = data.get("author-profile", {})

    # Nome preferido ou first name variant
    pref = profile.get("preferred-name", {})
    given = pref.get("given-name")
    surname = pref.get("surname")
    indexed = pref.get("indexed-name")
    if not (given and surname):
        variants = profile.get("name-variant", [])
        if variants:
            given = variants[0].get("given-name")
            surname = variants[0].get("surname")

    # Afiliação atual
    aff = profile.get("affiliation-current", {}).get("affiliation", {})
    ip = aff.get("ip-doc", aff)
    affiliation_name = ip.get("preferred-name", {}).get("$") or ip.get("afdispname")
    addr = ip.get("address", {})
    affiliation_city = addr.get("city")
    affiliation_country = addr.get("country")

    # Áreas de assunto
    subj_areas = [
        sa.get("$")
        for sa in data.get("subject-areas", {}).get("subject-area", [])
        if sa.get("$")
    ]

    # Período de publicação
    pr = profile.get("publication-range", {})
    pub_start = pr.get("@start")
    pub_end = pr.get("@end")

    return {
        "scopus_id": core.get("dc:identifier", "").split(":")[-1],
        "orcid": core.get("orcid"),
        "given_name": given,
        "surname": surname,
        "indexed_name": indexed,
        "document_count": int(core.get("document-count", 0)),
        "citation_count": int(core.get("citation-count", 0)),
        "cited_by_count": int(core.get("cited-by-count", 0)),
        "h_index": int(data.get("h-index", 0)),
        "coauthor_count": int(data.get("coauthor-count", 0)),
        "publication_start": pub_start,
        "publication_end": pub_end,
        "subject_areas": subj_areas,
        "affiliation_name": affiliation_name,
        "affiliation_city": affiliation_city,
        "affiliation_country": affiliation_country
    }

def get_subject_areas(author_id: str):
    """
    Busca áreas de assunto via consulta padrão de autor.
    """
    url = f"{BASE_URL}/content/search/author"
    params = {"query": f"AU-ID({author_id})", "view": "STANDARD"}
    resp = SESSION.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    entry = resp.json()["search-results"]["entry"][0]

    raw = entry.get("subject-area", [])
    areas = []
    if isinstance(raw, str):
        areas = [raw]
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                areas.append(item)
            elif isinstance(item, dict):
                areas.append(item.get("$") or item.get("subject-area"))
    return areas

def search_author_works(author_id: str, count: int = 5):
    """
    Recupera os trabalhos mais recentes (por ano) de um autor no Scopus.
    """
    url = f"{BASE_URL}/content/search/scopus"
    params = {
        "query": f"AU-ID({author_id})",
        "sort": "pubyear,desc",
        "count": count
    }
    resp = SESSION.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    entries = resp.json().get("search-results", {}).get("entry", [])
    works = []
    for e in entries:
        works.append({
            "title": e.get("dc:title"),
            "year": e.get("prism:coverDate", "")[:4],
            "doi": e.get("prism:doi"),
            "citations": e.get("citedby-count")
        })
    return works

def main():
    parser = argparse.ArgumentParser(description="Utilitário Scopus Author")
    parser.add_argument("author_id", help="Scopus Author ID (ex: 7003734634)")
    parser.add_argument("-m", "--mode",
                        choices=["profile", "subjects", "works", "all"],
                        default="all",
                        help="O que buscar: profile, subjects, works ou all")
    parser.add_argument("-c", "--count", type=int, default=5,
                        help="Número de trabalhos para listar (works)")
    args = parser.parse_args()

    aid = args.author_id
    mode = args.mode

    if mode in ("profile", "all"):
        profile = get_author_profile(author_id=aid)
        print("\n=== Perfil Completo ===")
        for k, v in profile.items():
            print(f"{k}: {v}")

    if mode in ("subjects", "all"):
        print("\n=== Áreas de Pesquisa ===")
        for area in get_subject_areas(aid):
            print(f"- {area}")

    if mode in ("works", "all"):
        print(f"\n=== Últimos {args.count} Trabalhos ===")
        for w in search_author_works(aid, count=args.count):
            print(f"- {w['title']} ({w['year']}), DOI: {w['doi']}, citações: {w['citations']}")

if __name__ == "__main__":
    main()
