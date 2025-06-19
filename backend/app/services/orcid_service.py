# app/services/orcid_service.py

from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from api_clients.orcid_client import (
    fetch_orcid,
    search_orcid_by_name,
    format_name,
    format_keywords,
    format_personal,
    format_employment,
    format_education_and_qualifications,
    format_works as format_orcid_works,
    format_works_with_contributors
)
from api_clients.openalex_client import (
    fetch_citations,
    parse_orcid_data,
    count_by_year,
    compute_metrics
)
from app.utils.utils import (
    normalize_doi,
    filter_by_year,
    filter_by_keyword
)


def search_by_name(query: str, max_results: int) -> List[Dict[str, str]]:
    """
    Busca autores cujo nome corresponde ao termo.
    """
    return search_orcid_by_name(query, max_results)


def get_name(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna o nome completo formatado do autor ORCID.
    """
    data = fetch_orcid(orcid_id)
    return format_name(data)


def get_keywords(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna as keywords associadas ao autor ORCID.
    """
    data = fetch_orcid(orcid_id, section="keywords")
    return {"keywords": format_keywords(data)}


def get_personal(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna informações pessoais (nome, biografia, e-mails, etc.).
    """
    data = fetch_orcid(orcid_id, section="person")
    return format_personal(data)


def get_employments(orcid_id: str) -> List[Dict[str, Any]]:
    """
    Retorna histórico de empregos do autor.
    """
    data = fetch_orcid(orcid_id, section="employments")
    return format_employment(data or {})


def get_educations(orcid_id: str) -> List[Dict[str, Any]]:
    """
    Retorna histórico educacional do autor.
    """
    data = fetch_orcid(orcid_id, section="educations")
    return format_education_and_qualifications(data or {})


def get_all_data(orcid_id: str) -> Dict[str, Any]:
    """
    Monta um JSON unificado com nome, obras (via ORCID), keywords,
    dados pessoais, empregos e formações.
    """
    basic = fetch_orcid(orcid_id)
    if not basic:
        return {}

    keywords = fetch_orcid(orcid_id, section="keywords")
    personal = fetch_orcid(orcid_id, section="person")
    emp = fetch_orcid(orcid_id, section="employments")
    edu = fetch_orcid(orcid_id, section="educations")
    works = fetch_orcid(orcid_id, section="works")

    return {
        "name":        basic.get("person", {}).get("name", {}),
        "works":       format_orcid_works(works or {}),
        "keywords":    format_keywords(keywords or {}),
        "personal":    format_personal(personal or {}),
        "employments": format_employment(emp or {}),
        "educations":  format_education_and_qualifications(edu or {}),
    }


def get_works(orcid_id: str) -> Dict[str, Any]:
    """
    Busca todas as obras do ORCID e anexa contagem de citações (via OpenAlex).
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []

    # Monta dicionário de DOIs → ano
    ids_para_cit = {}
    for w in works:
        doi = w.get("doi")
        if doi:
            d_norm = normalize_doi(doi)
            ids_para_cit[f"doi:{d_norm}"] = w.get("year", 0)

    try:
        doi_to_cit = fetch_citations(ids_para_cit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao obter citações: {e}")

    # Anexa cited_by_count a cada obra
    for w in works:
        doi = w.get("doi")
        if doi:
            key = f"doi:{normalize_doi(doi)}"
            w["cited_by_count"] = doi_to_cit.get(key, 0)
        else:
            w["cited_by_count"] = 0

    return {
        "orcid_id": orcid_id,
        "works": works
    }


def get_works_with_authors(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna todas as obras com lista de coautores.
    """
    try:
        works = format_works_with_contributors(orcid_id)
        return {"works": works}
    except HTTPException:
        raise


def get_works_openalex(orcid_id: str) -> Dict[str, Any]:
    """
    Recupera publicações do autor via OpenAlex, incluindo coautores e citações.
    """
    try:
        from api_clients.openalex_client import format_works_from_openalex
        works = format_works_from_openalex(orcid_id)
        return {"works": works}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")


def filter_works_by_keyword(
    orcid_id: str,
    keyword: str,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Filtra obras por ano (opcional) e keyword.
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []

    if year is not None:
        works = filter_by_year(works, year)

    filtered = filter_by_keyword(works, keyword)
    return {
        "orcid_id":       orcid_id,
        "keyword_searched": keyword,
        "year_filter":    year,
        "works":          filtered
    }


def filter_works_by_year(
    orcid_id: str,
    year: int,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filtra obras por ano e, opcionalmente, por keyword.
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []

    filtered = filter_by_year(works, year)
    if keyword:
        filtered = filter_by_keyword(filtered, keyword)

    return {
        "orcid_id":      orcid_id,
        "year":          year,
        "keyword_filter": keyword,
        "works":         filtered
    }


def filter_works_by_citations(
    orcid_id: str,
    year: Optional[int] = None,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filtra por ano/keyword (opcionais), anexa contagem de citações,
    remove duplicatas e ordena decrescente por citações.
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []

    if year is not None:
        works = filter_by_year(works, year)
    if keyword:
        works = filter_by_keyword(works, keyword)

    # Busca contagens
    ids_para_cit = {
        f"doi:{normalize_doi(w['doi'])}": w.get("year", 0)
        for w in works
        if w.get("doi")
    }
    doi_to_cit = fetch_citations(ids_para_cit)

    # Anexa e remove duplicatas por DOI
    unique = []
    seen: Set[str] = set()
    for w in works:
        doi = w.get("doi")
        if not doi:
            unique.append({**w, "cited_by_count": 0})
            continue
        d_norm = normalize_doi(doi)
        if d_norm in seen:
            continue
        seen.add(d_norm)
        w_copy = w.copy()
        w_copy["cited_by_count"] = doi_to_cit.get(f"doi:{d_norm}", 0)
        unique.append(w_copy)

    # Ordena
    sorted_works = sorted(unique, key=lambda w: w["cited_by_count"], reverse=True)
    return {
        "orcid_id":                orcid_id,
        "year_filter":             year,
        "keyword_filter":          keyword,
        "works_sorted_by_citations": sorted_works
    }


def get_orcid_metrics(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna métricas agregadas do autor ORCID:
    total_publicacoes, total_citacoes, media_citacoes,
    fator_de_impacto (últimos 2 anos), h_index, i10_index, pesquisa_mais_citada.
    """
    orcid_data = fetch_orcid(orcid_id, section="works")
    ids, no_id_years = parse_orcid_data(orcid_data or {})
    citations = fetch_citations(ids)

    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)
    metrics = compute_metrics(years, pubs_y, cites_y, ids, no_id_years, citations)
    return metrics


def get_orcid_stats(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna série temporal para gráficos:
    years, publications, citations.
    """
    orcid_data = fetch_orcid(orcid_id, section="works")
    ids, no_id_years = parse_orcid_data(orcid_data or {})
    citations = fetch_citations(ids)

    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)
    return {
        "years":        years,
        "publications": pubs_y,
        "citations":    cites_y
    }
