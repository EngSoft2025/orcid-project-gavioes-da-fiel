from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import html
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import sys


# Configurações
BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 10

# Cria sessão com retries

def create_session(retries=5, backoff_factor=1.0,
                   status_forcelist=(429, 500, 502, 503, 504)):
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

# Função auxiliar para buscar endpoint ORCID

def fetch_orcid(orcid_id: str, section: str = ""):
    url = f"{BASE_URL}/{orcid_id}/{section}" if section else f"{BASE_URL}/{orcid_id}"
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar ORCID: {e}")

# Funções de processamento

def format_name(data: dict):
    person = data.get("person", data)
    name = person.get("name", {})
    given = name.get("given-names", {}).get("value", "")
    family = name.get("family-name", {}).get("value", "")
    return {"full_name": f"{given} {family}".strip()}


def format_works(data: dict) -> list[dict]:
    """
    Recebe o JSON cru em 'data', extrai título e ano, e devolve uma lista de dicts:
    [ { "title": "...", "year": "2021" }, ... ]
    """
    works = []
    groups = data.get("group", [])
    for group in groups:
        for summary in group.get("work-summary", []):
            # Título
            raw_title = summary.get("title", {}) \
                               .get("title", {}) \
                               .get("value", "Sem título")
            title = html.unescape(raw_title)

            # Data de publicação: pode vir None, então substituímos por {}
            pub_date = summary.get("publication-date") or {}
            year = pub_date.get("year", {}).get("value", "----")

            works.append({"title": title, "year": year})
    return works


def format_keywords(data: dict):
    if isinstance(data.get('keywords'), dict):
        items = data['keywords'].get('keyword', [])
    else:
        items = data.get('keyword', [])
    return [html.unescape(kw.get('content', '')) for kw in items]


def format_personal(data: dict):
    person = data.get("person", data)
    result = format_name(data)
    bio = person.get("biography", {}).get("content")
    if bio:
        result["biography"] = html.unescape(bio)
    # Outros nomes
    other = person.get("other-names", {}).get("other-name", [])
    if other:
        result["other_names"] = [o.get("content") for o in other]
    # URLs
    urls = person.get("researcher-urls", {}).get("researcher-url", [])
    if urls:
        result["urls"] = [u.get("url", {}).get("value") for u in urls]
    # Emails
    emails = person.get("emails", {}).get("email", [])
    if emails:
        result["emails"] = [e.get("email") for e in emails]
    # Addresses
    addresses = person.get("addresses", {}).get("address", [])
    if addresses:
        result["countries"] = [a.get("country", {}).get("value") for a in addresses]
    # External IDs
    externals = person.get("external-identifiers", {}).get("external-identifier", [])
    if externals:
        result["external_ids"] = [{"type": ex.get("external-id-type"), "value": ex.get("external-id-value")} for ex in externals]
    return result

# Inicializa FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List, Dict

@app.get("/orcid/search/name", response_model=List[Dict[str, str]])
def search_name(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Busca autores cujo nome corresponde ao termo e retorna JSON com "orcid" e "full_name".
    Usa fetch_orcid + format_name diretamente para obter o nome formatado.
    """
    quoted = requests.utils.quote(query)
    url = f"{BASE_URL}/search/?q={quoted}&rows={max_results}"

    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro na ORCID API: {e}")

    data = resp.json()
    results = data.get("result", []) or []

    output: List[Dict[str, str]] = []
    for item in results:
        orcid_id = item.get("orcid-identifier", {}).get("path")
        if not orcid_id:
            continue
        try:
            record = fetch_orcid(orcid_id)
            name_data = format_name(record)
            # Extrai string de nome, caso format_name retorne dict
            if isinstance(name_data, dict):
                full_name = name_data.get("full_name", "")
            else:
                full_name = str(name_data)
        except Exception:
            full_name = ""

        output.append({
            "orcid": orcid_id,
            "full_name": full_name
        })

    return output


@app.get("/orcid/search/work")
def search_work(title: str, max_results: int = 10):
    q = f"title:\"{title}\""
    url = f"{BASE_URL}/search/?q={requests.utils.quote(q)}&rows={max_results}"
    data = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT).json()
    results = data.get("result", [])
    return [item.get("orcid-identifier", {}).get("path") for item in results]

# Endpoints
@app.get("/orcid/{orcid_id}/name")
def get_name(orcid_id: str):
    data = fetch_orcid(orcid_id)
    return format_name(data)

@app.get("/orcid/{orcid_id}/works")
def get_works(orcid_id: str):
    data = fetch_orcid(orcid_id, "works")
    return {"works": format_works(data)}

@app.get("/orcid/{orcid_id}/keywords")
def get_keywords(orcid_id: str):
    data = fetch_orcid(orcid_id, "keywords")
    return {"keywords": format_keywords(data)}

@app.get("/orcid/{orcid_id}/personal")
def get_personal(orcid_id: str):
    data = fetch_orcid(orcid_id, "person")
    return format_personal(data)

@app.get("/orcid/{orcid_id}/all")
def get_all(orcid_id: str):
    """
    Monta um JSON unificado com várias seções:
    { "name": ..., "works": [...], "keywords": [...], "personal": {...} }
    """
    # ... supondo que você já tenha fetch_orcid e format_keywords etc.
    basic   = fetch_orcid(orcid_id, "")
    works_d = fetch_orcid(orcid_id, "works")
    keywords_d = fetch_orcid(orcid_id, "keywords")
    personal_d = fetch_orcid(orcid_id, "person")

    if not basic:
        raise HTTPException(status_code=404, detail="ORCID não encontrado")

    return {
        "name": basic.get("person", {}).get("name", {}),
        "works": format_works(works_d or {}),
        "keywords": format_keywords(keywords_d or {}),
        "personal": format_personal(personal_d or {})
    }

"""
Para rodar:
    1)  python3 -m venv venv
    2)  source venv/bin/activate
    3)  uvicorn api:app --reload --port 8000
"""