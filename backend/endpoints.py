# endpoints.py

from typing import List, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api_clients.orcid_client import (
    fetch_orcid,
    search_orcid_by_name,
    format_name,
    format_keywords,
    format_personal,
    format_employment,
    format_education_and_qualifications,
    format_works as format_orcid_works,
    format_works_with_contributors as format_orcid_works_with_contributors 
)

from api_clients.openalex_client import (
    parse_orcid_data,
    fetch_citations,
    count_by_year,
    compute_metrics
)

app = FastAPI()

# Configurações de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ORCID Endpoints ---

@app.get("/orcid/search/name", response_model=List[Dict[str, str]])
def search_name(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Busca autores cujo nome corresponde ao termo e retorna JSON com "orcid" e "full_name".
    """
    try:
        return search_orcid_by_name(query, max_results)
    except HTTPException:
        raise

@app.get("/orcid/{orcid_id}/name")
def get_name(orcid_id: str):
    """
    Retorna o nome formatado completo do autor ORCID.
    """
    data = fetch_orcid(orcid_id)
    return format_name(data)

@app.get("/orcid/{orcid_id}/works")
def get_works(orcid_id: str):
    """
    Busca todas as obras do ORCID e formata usando a função `format_works`.
    """
    raw = fetch_orcid(orcid_id, section="works")
    works_list = format_orcid_works(raw or {})
    return {"works": works_list}

@app.get("/orcid/{orcid_id}/works_with_authors")
def get_works_authors(orcid_id: str):
    """
    Retorna todas as obras com lista de coautores.
    """
    try:
        # esta função faz múltiplas chamadas ao ORCID para cada obra
        from api_clients.orcid_client import format_works_with_contributors
        works = format_works_with_contributors(orcid_id)
        return {"works": works}
    except HTTPException:
        raise


@app.get("/orcid/{orcid_id}/works-openalex")
def get_works_from_openalex(orcid_id: str):
    """
    Recupera publicações do autor via OpenAlex, incluindo coautores e número de citações.
    """
    try:
        works = format_works_from_openalex(orcid_id)
        return {"works": works}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
    

@app.get("/orcid/{orcid_id}/keywords")
def get_keywords(orcid_id: str):
    """
    Retorna as keywords associadas ao autor ORCID.
    """
    data = fetch_orcid(orcid_id, section="keywords")
    return {"keywords": format_keywords(data)}

@app.get("/orcid/{orcid_id}/personal")
def get_personal(orcid_id: str):
    """
    Retorna informações pessoais (nome, biografia, e-mails, etc.).
    """
    data = fetch_orcid(orcid_id, section="person")
    return format_personal(data)

@app.get("/orcid/{orcid_id}/employments")
def get_employments(orcid_id: str):
    """
    Retorna histórico de empregos do autor.
    """
    data = fetch_orcid(orcid_id, section="employments")
    return {"employments": format_employment(data or {})}

@app.get("/orcid/{orcid_id}/educations")
def get_educations(orcid_id: str):
    """
    Retorna histórico educacional do autor.
    """
    data = fetch_orcid(orcid_id, section="educations")
    return {"educations": format_education_and_qualifications(data or {})}

@app.get("/orcid/{orcid_id}/all")
def get_all(orcid_id: str):
    """
    Monta um JSON unificado com nome, obras (via OpenAlex), palavras-chave,
    dados pessoais, empregos e formações.
    """
    
    basic     = fetch_orcid(orcid_id)
    keywords  = fetch_orcid(orcid_id, section="keywords")
    personal  = fetch_orcid(orcid_id, section="person")
    emp       = fetch_orcid(orcid_id, section="employments")
    edu       = fetch_orcid(orcid_id, section="educations")
    works     = fetch_orcid(orcid_id, section="works")


    # try:
    #    works = format_orcid_works_with_contributors(orcid_id)
    # except HTTPException:
    #    works = []

    # Via OpenAlex
    # try:
    #     works_oa = format_works_from_openalex(orcid_id)
    # except HTTPException:
    #     works_oa = []

    if not basic:
        raise HTTPException(status_code=404, detail="ORCID não encontrado")

    return {
        "name":         basic.get("person", {}).get("name", {}),
        "works":        format_orcid_works(works or {}),
        "keywords":     format_keywords(keywords or {}),
        "personal":     format_personal(personal or {}),
        "employments":  format_employment(emp or {}),
        "educations":   format_education_and_qualifications(edu or {})
    }

@app.get("/orcid/{orcid_id}/works/filter_by_keyword")
def filter_works_by_keyword(orcid_id: str, keyword: str = Query(..., description="Palavra-chave para filtrar títulos")):
    """
    Retorna obras cujo título contenha a palavra-chave.
    """
    raw   = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw)
    filtered = [w for w in works if keyword.lower() in w["title"].lower()]
    return {"works": filtered}

@app.get("/orcid/{orcid_id}/works/filter_by_year")
def filter_works_by_year(
    orcid_id: str,
    year: int = Query(..., ge=0, description="Ano de publicação para filtrar")
):
    """
    Retorna apenas as obras publicadas no ano especificado.
    """
    raw   = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw)
    filtered = [w for w in works if str(w.get("year", "")).isdigit() and int(w["year"]) == year]
    return {"year": year, "works": filtered}

import re

_DOI_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/|^doi:\s*", re.I)

def normalize_doi(doi: str | None) -> str:
    """
    Remove prefixos de URL ou 'doi:' e retorna o DOI em minúsculas.
    """
    return _DOI_RE.sub("", (doi or "").strip()).lower()

@app.get("/orcid/{orcid_id}/works/filter_by_citations")
def filter_works_by_citations(orcid_id: str):
    # Busca no ORCID
    raw   = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw)         # [{ "doi": "...", ... }, …]

    # DOIs únicos normalizados
    dois = {normalize_doi(w.get("doi")) for w in works if w.get("doi")}

    # Busca em lote no OpenAlex (paginado)
    doi_to_cit = {}
    oa_url = "https://api.openalex.org/works"
    try:
        cursor = "*"
        while cursor and len(doi_to_cit) < len(dois):
            params = {
                "filter"  : f"author.orcid:https://orcid.org/{orcid_id}",
                "per-page": 200,               # limite da API
                "cursor"  : cursor,
            }
            resp = requests.get(oa_url, params=params, timeout=10)
            data = resp.json()
            for item in data.get("results", data.get("works", [])):
                d = normalize_doi(item.get("doi"))
                if d:
                    c = item.get("cited_by_count", item.get("citations", 0)) or 0
                    doi_to_cit[d] = c
            cursor = data.get("meta", {}).get("next_cursor")
            if cursor == "null": 
                cursor = None
    except Exception:
        pass   # prossegue para fallback

    # consulta individual para DOIs ainda faltando
    for d in dois - doi_to_cit.keys():
        try:
            r = requests.get(f"{oa_url}/doi:{d}", timeout=5)
            r.raise_for_status()
            j = r.json()
            doi_to_cit[d] = j.get("cited_by_count", 0) or 0
        except Exception:
            doi_to_cit[d] = 0

    # Pega as contagens e ordena
    for w in works:
        d = normalize_doi(w.get("doi"))
        w["citations"] = doi_to_cit.get(d, 0)

    works.sort(key=lambda w: w["citations"], reverse=True)
    return {"works": works}

@app.get("/orcid/{orcid_id}/metrics")
def get_orcid_metrics(orcid_id: str):
    """
    Retorna métricas agregadas do autor ORCID, incluindo:
    - total_publicacoes
    - total_citacoes
    - media_citacoes
    - fator_de_impacto (últimos 2 anos)
    - h_index
    - i10_index
    - pesquisa_mais_citada
    """
    orcid_data = fetch_orcid(orcid_id, section="works")
    ids, no_id_years = parse_orcid_data(orcid_data)
    citations = fetch_citations(ids)

    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)
    metrics = compute_metrics(years, pubs_y, cites_y, ids, no_id_years, citations)
    return metrics

@app.get("/orcid/{orcid_id}/stats")
def get_orcid_stats(orcid_id: str):
    """
    Retorna a série temporal para construção de gráfico:
    {
      "years": [...],
      "publications": [...],
      "citations": [...]
    }
    """
    orcid_data = fetch_orcid(orcid_id, section="works")
    ids, no_id_years = parse_orcid_data(orcid_data)

    citations = fetch_citations(ids)

    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)
    return {
        "years": years,
        "publications": pubs_y,
        "citations": cites_y
    }

# Monta diretório estático para rodar o HTML
app.mount("/", StaticFiles(directory="static", html=True), name="static")
