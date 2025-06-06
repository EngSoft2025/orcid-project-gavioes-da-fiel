# endpoints.py


from typing import List, Dict, Any, Optional, Set
import logging
from collections import Counter
import re
import requests

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

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
    compute_metrics,
    format_works_from_openalex
)

app = FastAPI()

# Configurações de CORS
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



# ========== requisições de filtro ===========

_DOI_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/|^doi:\s*", re.I)
_ORCID_URL_RE = re.compile(r"^https?://orcid\.org/", re.I)

def normalize_doi(doi: Optional[str]) -> str:
    """
    Remove prefixos de URL ou 'doi:' e retorna o DOI em minúsculas.
    Exemplo: "https://doi.org/10.1000/xyz" -> "10.1000/xyz"
    """
    return _DOI_RE.sub("", (doi or "").strip()).lower()


def normalize_orcid(orcid: str) -> str:
    """
    Remove eventual URL e espaços de um ORCID, mantendo apenas o formato numérico com hífens.
    Exemplo: "https://orcid.org/0000-0002-1234-5678" -> "0000-0002-1234-5678"
    """
    return _ORCID_URL_RE.sub("", orcid.strip())


def filter_by_year(works: List[Dict], year: int) -> List[Dict]:
    """
    Retorna apenas as obras cujo campo 'year' bate com o ano especificado.
    Caso 'year' venha como inteiro ou string numérica, faz a comparação corretamente.
    """
    resultado: List[Dict] = []
    for w in works:
        ano_obra = w.get("year")
        if isinstance(ano_obra, int) and ano_obra == year:
            resultado.append(w)
        elif isinstance(ano_obra, str) and ano_obra.isdigit() and int(ano_obra) == year:
            resultado.append(w)
    return resultado


def filter_by_keyword(works: List[Dict], keyword: str) -> List[Dict]:
    """
    Retorna apenas as obras que contêm 'keyword' (case-insensitive)
    no título, abstract/short_description ou na lista de keywords.
    """
    sk = keyword.lower()
    filtrado: List[Dict] = []

    for w in works:
        match = False

        # Verifica título
        title = w.get("title", "")
        if isinstance(title, str) and sk in title.lower():
            match = True

        # Verifica abstract/short_description
        if not match:
            abstract = w.get("short_description") or w.get("abstract")
            if isinstance(abstract, str) and sk in abstract.lower():
                match = True

        # Verifica lista de palavras‐chave
        if not match:
            kws = w.get("keywords", [])
            if isinstance(kws, list):
                for kw_item in kws:
                    txt: Optional[str] = None
                    if isinstance(kw_item, str):
                        txt = kw_item
                    elif isinstance(kw_item, dict):
                        txt = kw_item.get("content")
                    if isinstance(txt, str) and sk in txt.lower():
                        match = True
                        break

        if match:
            filtrado.append(w)

    return filtrado


@app.get("/orcid/{orcid_id}/works/filter_by_keyword")
def filter_works_by_keyword(
    orcid_id: str,
    keyword: str = Query(..., description="Keyword para buscar nos títulos, abstracts e keywords."),
    year: Optional[int] = Query(None, ge=0, description="(Opcional) Ano para filtrar antes de buscar pela keyword")
):
    try:
        orcid_id_norm = normalize_orcid(orcid_id)

        # Busca todas as obras do ORCID
        raw = fetch_orcid(orcid_id_norm, section="works") or {}
        all_works = format_orcid_works(raw) or []

        # Se veio year, filtra primeiro por ano
        if year is not None:
            all_works = filter_by_year(all_works, year)

        # Em seguida aplica o filtro por keyword
        filtered = filter_by_keyword(all_works, keyword)

        return {
            "orcid_id": orcid_id_norm,
            "keyword_searched": keyword,
            "year_filter": year,
            "works": filtered
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Erro interno ao filtrar obras por keyword: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")


@app.get("/orcid/{orcid_id}/works/filter_by_year")
def filter_works_by_year(
    orcid_id: str,
    year: int = Query(..., ge=0, description="Ano de publicação para filtrar"),
    keyword: Optional[str] = Query(None, description="(Opcional) Filtrar por palavra-chave após ter filtrado por ano")
):
    try:
        orcid_id_norm = normalize_orcid(orcid_id)

        # Busca todas as obras do ORCID
        raw = fetch_orcid(orcid_id_norm, section="works") or {}
        all_works = format_orcid_works(raw) or []

        # Filtra por ano
        filtered_by_year = filter_by_year(all_works, year)

        # Se veio keyword, aplica filtro por keyword no conjunto já filtrado por ano
        if keyword:
            filtered_by_year = filter_by_keyword(filtered_by_year, keyword)

        return {
            "orcid_id": orcid_id_norm,
            "year": year,
            "keyword_filter": keyword,
            "works": filtered_by_year
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Erro interno ao filtrar obras por ano: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")


@app.get("/orcid/{orcid_id}/works/filter_by_citations")
def filter_works_by_citations(
    orcid_id: str,
    year: Optional[int] = Query(
        None,
        ge=0,
        description="(Opcional) Ano para filtrar antes de ordenar por citações"
    ),
    keyword: Optional[str] = Query(
        None,
        description="(Opcional) Filtrar por keyword antes de ordenar por citações"
    )
):
    try:
        orcid_id_norm = normalize_orcid(orcid_id)

        # Busca todas as obras do ORCID
        raw = fetch_orcid(orcid_id_norm, section="works") or {}
        all_works = format_orcid_works(raw) or []

        # Se vier 'year', filtra primeiro todas as obras por ano
        if year is not None:
            all_works = filter_by_year(all_works, year)

        # Se vier 'keyword', filtra no conjunto já filtrado por ano
        if keyword:
            all_works = filter_by_keyword(all_works, keyword)

        # Monta um dicionário de IDs para obter citações:
        #    chave = "doi:<doi_normalizado>" → valor = ano (podemos usar o próprio campo 'year' ou 0)
        ids_para_citacoes: Dict[str, int] = {}
        for w in all_works:
            raw_doi = w.get("doi")
            if not raw_doi:
                continue
            d_norm = normalize_doi(raw_doi)
            # Se quisermos usar o ano no filtro, podemos pegar w.get("year") ou simplesmente 0
            ids_para_citacoes[f"doi:{d_norm}"] = w.get("year", 0)  # valor do dicionário não é usado no fetch_citations

        # Chama fetch_citations para obter { "doi:<doi>": cited_by_count }
        doi_to_cit = fetch_citations(ids_para_citacoes)

        # Para cada obra, adiciona o campo "cited_by_count"
        works_with_counts: List[Dict] = []
        for w in all_works:
            w_copy = w.copy()
            raw_doi = w.get("doi")
            if raw_doi:
                d_norm = normalize_doi(raw_doi)
                key = f"doi:{d_norm}"
                w_copy["cited_by_count"] = doi_to_cit.get(key, 0)
            else:
                w_copy["cited_by_count"] = 0
            works_with_counts.append(w_copy)

        unique_by_doi: List[Dict] = []
        seen_dois: set[str] = set()
        for w in works_with_counts:
            raw_doi = w.get("doi")
            if not raw_doi:
                unique_by_doi.append(w)
                continue

            d_norm = normalize_doi(raw_doi)
            if d_norm not in seen_dois:
                seen_dois.add(d_norm)
                unique_by_doi.append(w)
            # caso já tenha visto este DOI, ignora as duplicatas


        # Ordena todas as obras em ordem decrescente de citações
        all_works_sorted = sorted(
            unique_by_doi,
            key=lambda x: x.get("cited_by_count", 0),
            reverse=True,
        )

        return {
            "orcid_id":                  orcid_id_norm,
            "year_filter":               year,
            "keyword_filter":            keyword,
            "works_sorted_by_citations": all_works_sorted
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Erro interno ao filtrar obras por citações: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")


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