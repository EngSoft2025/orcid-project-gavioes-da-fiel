from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import html
from pydantic import BaseModel, EmailStr
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from typing import List, Dict
import db
# Configurações
BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 10

# Cria sessão com retries
def create_session(retries=5, backoff_factor=1.0,
                   status_forcelist=(429, 500, 502, 503, 504)):

    try:
        db.init_db()
    except Exception as e:
        print(f"[WARN] Could not initialize database: {e}")
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
    

# Configuração para OpenAlex
OA_WORKS_URL = "https://api.openalex.org/works"
OA_PER_PAGE   = 200
OA_TIMEOUT    = 20
OA_MAILTO     = "gabrielabreu571@gmail.com"
OA_HEADERS    = {
    "User-Agent": f"orcid-citations/1.0 (mailto:{OA_MAILTO})"
}

# Função para buscar endpoint do openAlex
def fetch_works_openalex(orcid_id: str) -> List[Dict]:
    """
    Busca todas as obras do autor no OpenAlex e retorna lista de dicts:
      { title, year, doi, cited_by_count }
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
        r = requests.get(OA_WORKS_URL, params=params,
                         headers=OA_HEADERS, timeout=OA_TIMEOUT)
        if r.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao acessar OpenAlex: {r.status_code}"
            )
        payload = r.json()
        for w in payload.get("results", []):
            works.append({
                "title":            html.unescape(w.get("display_name") or "Sem título"),
                "year":             w.get("publication_year") or 0,
                "doi":              (w.get("ids") or {}).get("doi"),
                "cited_by_count":   w.get("cited_by_count", 0),
            })

        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not cursor:
            break

    return works


# Funções de processamento

def format_name(data: dict):
    person = data.get("person", data)
    name = person.get("name", {})
    given = name.get("given-names", {}).get("value", "")
    family = name.get("family-name", {}).get("value", "")
    return {"full_name": f"{given} {family}".strip()}


def format_works(data: dict) -> list[dict]:
    """
    Recebe o JSON de /{orcid_id}/works (v3.0), que tem no topo:
      { "group": [ { "work-summary": [ … ] }, … ] }
    e devolve uma lista de dicts com todos os campos, evitando AttributeError:
    """
    works = []
    for group in data.get("group", []):
        for summary in group.get("work-summary", []):
            # título
            title = html.unescape(
                (summary.get("title") or {})
                    .get("title", {})
                    .get("value", "Sem título")
            )
            # ano
            year = (
                (summary.get("publication-date") or {})
                    .get("year", {})
                    .get("value", "----")
            )
            # tipo de obra
            work_type = summary.get("type") or "desconhecido"

            # container/jornal (pode ser null)
            container = (summary.get("journal-title") or {}).get("value")

            # DOI (se existir em external-ids)
            doi = None
            for ext in (summary.get("external-ids") or {}).get("external-id", []):
                if ext.get("external-id-type", "").lower() == "doi":
                    doi = ext.get("external-id-value")
                    break

            # URL (pode ser null)
            url = (summary.get("url") or {}).get("value")

            # path ORCID
            path = summary.get("path") or None

            works.append({
                "title":     title,
                "year":      year,
                "type":      work_type,
                "container": container,
                "doi":       doi,
                "url":       url,
                "path":      path,
            })
    return works


def _fmt_date(d: dict) -> str | None:
    if not d: 
        return None
    y = d.get("year", {}).get("value")
    m = d.get("month", {}).get("value")
    day = d.get("day", {}).get("value")
    parts = [p for p in (y, m, day) if p]
    return "-".join(parts) if parts else None

def format_employment(data: dict) -> list[dict]:
    """
    data é o JSON retornado por /{orcid_id}/employments
    """
    employments = []
    for group in data.get("affiliation-group", []):
        for item in group.get("summaries", []):
            s = item.get("employment-summary", {})
            org = s.get("organization", {}) or {}
            employments.append({
                "organization": org.get("name"),
                "department": s.get("department-name"),
                "role_title": s.get("role-title"),
                "start_date": _fmt_date(s.get("start-date")),
                "end_date": _fmt_date(s.get("end-date")),
                "url": (s.get("url") or {}).get("value")
            })
    return employments

def format_education_and_qualifications(data: dict) -> list[dict]:
    """
    data é o JSON retornado por /{orcid_id}/educations
    """
    educations = []
    for group in data.get("affiliation-group", []):
        for item in group.get("summaries", []):
            s = item.get("education-summary", {})
            org = s.get("organization", {}) or {}
            educations.append({
                "organization": org.get("name"),
                "department": s.get("department-name"),
                "role_title": s.get("role-title"),  # ex: "Ph.D. in Information Engineering"
                "start_date": _fmt_date(s.get("start-date")),
                "end_date": _fmt_date(s.get("end-date")),
                "url": (s.get("url") or {}).get("value")
            })
    return educations
    

def format_keywords(data: dict):
    if isinstance(data.get('keywords'), dict):
        items = data['keywords'].get('keyword', [])
    else:
        items = data.get('keyword', [])
    return [html.unescape(kw.get('content', '')) for kw in items]


def format_personal(data: dict):
    """
    Extrai e formata informações pessoais de um objeto ORCID 'person' ou wrapper {'person': {...}}.
    Retorna um dict com:
      - full_name
      - biography (se existir)
      - other_names (lista, se existir)
      - urls (lista, se existir)
      - emails (lista, se existir)
      - countries (lista, se existir)
      - external_ids (lista de dicts, se existir)
    """
    # Garante que tenhamos sempre um dict, nunca None
    person = (data.get("person") or data) or {}
    result = format_name(data)

    # Biografia
    bio_obj = person.get("biography") or {}
    if isinstance(bio_obj, dict):
        content = bio_obj.get("content")
        if content:
            result["biography"] = html.unescape(content)

    # Outros nomes
    other_obj = person.get("other-names") or {}
    other_list = other_obj.get("other-name") or []
    if isinstance(other_list, list) and other_list:
        result["other_names"] = [
            o.get("content")
            for o in other_list
            if o and o.get("content")
        ]

    # URLs de pesquisador
    urls_obj = person.get("researcher-urls") or {}
    url_list = urls_obj.get("researcher-url") or []
    if isinstance(url_list, list) and url_list:
        result["urls"] = [
            u.get("url", {}).get("value")
            for u in url_list
            if isinstance(u, dict) and u.get("url", {}).get("value")
        ]

    # E-mails
    emails_obj = person.get("emails") or {}
    email_list = emails_obj.get("email") or []
    if isinstance(email_list, list) and email_list:
        result["emails"] = [
            e.get("email")
            for e in email_list
            if e and e.get("email")
        ]

    # Países (endereços)
    addr_obj = person.get("addresses") or {}
    addr_list = addr_obj.get("address") or []
    if isinstance(addr_list, list) and addr_list:
        result["countries"] = [
            a.get("country", {}).get("value")
            for a in addr_list
            if a and a.get("country", {}).get("value")
        ]

    # Identificadores externos
    ext_obj = person.get("external-identifiers") or {}
    ext_list = ext_obj.get("external-identifier") or []
    if isinstance(ext_list, list) and ext_list:
        result["external_ids"] = [
            {
                "type": ex.get("external-id-type"),
                "value": ex.get("external-id-value")
            }
            for ex in ext_list
            if ex and ex.get("external-id-type") and ex.get("external-id-value")
        ]

    return result

# classes auxiliares do login 
class SignUpIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignInIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str 
# Inicializa FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Endpoints
@app.get("/orcid/{orcid_id}/name")
def get_name(orcid_id: str):
    data = fetch_orcid(orcid_id)
    return format_name(data)

@app.get("/orcid/{orcid_id}/works")
def get_works(orcid_id: str):
    """
    Busca todas as obras do ORCID para o authorId fornecido,
    formata cada resumo usando format_works e retorna:
      { "works": [ { title, year, type, container, doi, url, contributors }, … ] }
    """
    # chama a API ORCID na seção "works"
    try:
        raw = fetch_orcid(orcid_id, "works")
    except HTTPException:
        # propaga erros de rede ou status != 200
        raise

    # garante um dict para não quebrar format_works
    works_list = format_works(raw or {})

    return {"works": works_list}

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
    emp_d   = fetch_orcid(orcid_id, "employments")
    edu_d   = fetch_orcid(orcid_id, "educations")

    if not basic:
        raise HTTPException(status_code=404, detail="ORCID não encontrado")

    return {
        "name": basic.get("person", {}).get("name", {}),
        "works": format_works(works_d or {}),
        "keywords": format_keywords(keywords_d or {}),
        "personal": format_personal(personal_d or {}),
        "employments": format_employment(emp_d or {}),
        "educations": format_education_and_qualifications(edu_d or {})
    }

# — Filter_by_keyword"
@app.get("/orcid/{orcid_id}/works/filter_by_keyword")
def filter_works_by_keyword(orcid_id: str, keyword: str = Query(..., description="…")):
    raw = fetch_orcid(orcid_id, "works") or {}
    works = format_works(raw)
    return {"works": [w for w in works if keyword.lower() in w["title"].lower()]}

# — Filter_by_year
@app.get("/orcid/{orcid_id}/works/filter_by_year")
def filter_works_by_year(
    orcid_id: str,
    year: int = Query(..., ge=0, description="Ano de publicação a filtrar")
):
    """
    Retorna apenas as obras publicadas em 'year'.
    Ignora qualquer registro cujo campo 'year' não seja um número válido.
    """
    raw = fetch_orcid(orcid_id, "works") or {}
    works = format_works(raw)

    filtered = []
    for w in works:
        y = w.get("year", "")
        # só converte se y for dígito (ex.: "2020"), caso contrário pula
        if y.isdigit() and int(y) == year:
            filtered.append(w)

    return {"year": year, "works": filtered}

# — Filter_by_citations
@app.get("/orcid/{orcid_id}/works/filter_by_citations")
def filter_works_by_citations(orcid_id: str):
    """
    Retorna todas as obras ordenadas pelo número de citações (via OpenAlex),
    incluindo para cada item o campo `citations`.
    """
    # Busca as obras no OpenAlex, já com o campo 'cited_by_count'
    works = fetch_works_openalex(orcid_id)

    # Renomeia 'cited_by_count' para 'citations' e mantém os demais campos
    for w in works:
        w["citations"] = w.pop("cited_by_count", 10)

    # Ordena em ordem decrescente de citações
    works.sort(key=lambda w: w["citations"], reverse=True)

    return {"works": works}

@app.post("/signup", status_code=201)
def signup(payload: SignUpIn):
    """
    Create a new user if the e-mail is not taken.
    """
    if db.get_user_by_email(payload.email):
        raise HTTPException(
            status_code=409,
            detail="E-mail already registered."
        )

    user_id = db.create_user(payload.name, payload.email, payload.password)
    user_row = db.get_user_by_email(payload.email)  # (id, name, email, created_at)

    return {
        "user": {
            "id": user_row[0],
            "name": user_row[1],
            "email": user_row[2],
            "created_at": user_row[3]
        }
    }


@app.post("/signin")
def signin(payload: SignInIn):
    """
    Authenticate and return the user record (minus password hash).
    """
    user = db.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid e-mail or password."
        )

    # user == (id, name, email, created_at)
    return {
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "created_at": user[3]
        }
    }


"""
Para rodar:
    1)  python3 -m venv venv
    2)  source venv/bin/activate

    Instale os requisitos:
    pip install fastapi uvicorn
    pip install "uvicorn[standard]"
    pip install requests

    3)  uvicorn api:app --reload --port 8000
"""

"""
    Comandos:
    GET Works:
    curl -X GET   "http://localhost:8000/orcid/0000-0003-1574-0784/works"   -H "Accept: application/json"
    
    # Buscar nome completo
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/name" -H "Accept: application/json"

    # Buscar palavras-chave
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/keywords" -H "Accept: application/json"

    # Buscar dados pessoais
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/personal" -H "Accept: application/json"

    # Buscar todas as informações
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/all" -H "Accept: application/json"

    # Buscar por nome
    curl -X GET "http://localhost:8000/orcid/search/name?query=Seiji%20Isotani" -H "Accept: application/json"

    # Filtrar obras por palavra-chave no título
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/works/filter_by_keyword?keyword=AI" -H "Accept: application/json"

    # Filtrar obras por ano de publicação
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/works/filter_by_year?year=2021" -H "Accept: application/json"

    # Filtrar obras por número de citações (via OpenAlex)
    curl -X GET "http://localhost:8000/orcid/0000-0003-1574-0784/works/filter_by_citations" -H "Accept: application/json"
"""

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
