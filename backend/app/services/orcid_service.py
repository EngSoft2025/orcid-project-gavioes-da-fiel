# app/services/orcid_service.py

from typing import List, Dict, Any, Optional, Set
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

    Args:
        query (str): Termo de busca para o nome do autor.
        max_results (int): Número máximo de resultados a retornar.

    Returns:
        List[Dict[str, str]]: Lista de dicionários contendo 'orcid' e 'full_name'.
    """
    return search_orcid_by_name(query, max_results)


def get_name(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna o nome completo formatado do autor ORCID.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: Dicionário com o nome completo e campos relacionados.
    """
    data = fetch_orcid(orcid_id)
    return format_name(data)


def get_keywords(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna as keywords associadas ao autor ORCID.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {'keywords': List[str]} com as palavras-chave do autor.
    """
    data = fetch_orcid(orcid_id, section="keywords")
    return {"keywords": format_keywords(data)}


def get_personal(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna informações pessoais do autor (nome, biografia, e-mails, etc.).

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: Dados pessoais formatados do autor.
    """
    data = fetch_orcid(orcid_id, section="person")
    return format_personal(data)


def get_employments(orcid_id: str) -> List[Dict[str, Any]]:
    """
    Retorna histórico de empregos do autor.
    Se algo falhar na formatação, retorna lista vazia.
    """
    raw = fetch_orcid(orcid_id, section="employments")
    try:
        return format_employment(raw or {})
    except Exception:
        return []

def get_educations(orcid_id: str) -> List[Dict[str, Any]]:
    """
    Retorna histórico educacional e qualificações do autor.
    """
    raw = fetch_orcid(orcid_id, section="educations")
    try:
        return format_education_and_qualifications(raw or {})
    except Exception:
        return []


def get_all_data(orcid_id: str) -> Dict[str, Any]:
    """
    Monta um JSON unificado com nome, obras, keywords, dados pessoais,
    histórico de empregos e formações de um autor.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: Dicionário contendo todos os dados agrupados,
        ou vazio se o ORCID não for encontrado.
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
    Busca todas as obras de um autor no ORCID e anexa contagem de citações (via OpenAlex).

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {
            "orcid_id": str,
            "works": List[Dict[str, Any]]
        }

    Raises:
        HTTPException: Em caso de falha ao obter citações.
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []

    # Monta mapeamento DOI → ano
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

    # Anexa citado_por_count a cada obra
    for w in works:
        doi = w.get("doi")
        if doi:
            key = f"doi:{normalize_doi(doi)}"
            w["cited_by_count"] = doi_to_cit.get(key, 0)
        else:
            w["cited_by_count"] = 0

    return {"orcid_id": orcid_id, "works": works}


def get_works_with_authors(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna todas as obras de um autor com lista de coautores.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {'works': List[Dict[str, Any]]}

    Raises:
        HTTPException: Em caso de erro na chamada ao ORCID.
    """
    try:
        works = format_works_with_contributors(orcid_id)
        return {"works": works}
    except HTTPException:
        raise


def get_works_openalex(orcid_id: str) -> Dict[str, Any]:
    """
    Recupera publicações de um autor via OpenAlex, incluindo coautores e citações.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {'works': List[Dict[str, Any]]}

    Raises:
        HTTPException: Em caso de erro inesperado.
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
    Filtra obras de um autor por palavra-chave, opcionalmente pré-filtrando por ano.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        keyword (str): Palavra-chave a ser buscada.
        year (Optional[int]): Ano para pré-filtrar as obras.

    Returns:
        Dict[str, Any]: {
            "orcid_id": str,
            "keyword_searched": str,
            "year_filter": Optional[int],
            "works": List[Dict[str, Any]]
        }
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []
    if year is not None:
        works = filter_by_year(works, year)
    filtered = filter_by_keyword(works, keyword)
    return {
        "orcid_id":        orcid_id,
        "keyword_searched": keyword,
        "year_filter":     year,
        "works":           filtered
    }


def filter_works_by_year(
    orcid_id: str,
    year: int,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filtra obras de um autor por ano de publicação, opcionalmente por palavra-chave.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        year (int): Ano de publicação para filtrar as obras.
        keyword (Optional[str]): Palavra-chave para filtro adicional.

    Returns:
        Dict[str, Any]: {
            "orcid_id": str,
            "year": int,
            "keyword_filter": Optional[str],
            "works": List[Dict[str, Any]]
        }
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []
    filtered = filter_by_year(works, year)
    if keyword:
        filtered = filter_by_keyword(filtered, keyword)
    return {
        "orcid_id":       orcid_id,
        "year":           year,
        "keyword_filter": keyword,
        "works":          filtered
    }


def filter_works_by_citations(
    orcid_id: str,
    year: Optional[int] = None,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filtra obras de um autor por número de citações, opcionalmente pré-filtrando
    por ano e/ou palavra-chave, remove duplicatas e ordena por citações decrescentes.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        year (Optional[int]): Ano para pré-filtrar as obras.
        keyword (Optional[str]): Palavra-chave para filtro antes da ordenação.

    Returns:
        Dict[str, Any]: {
            "orcid_id": str,
            "year_filter": Optional[int],
            "keyword_filter": Optional[str],
            "works_sorted_by_citations": List[Dict[str, Any]]
        }
    """
    raw = fetch_orcid(orcid_id, section="works") or {}
    works = format_orcid_works(raw) or []
    if year is not None:
        works = filter_by_year(works, year)
    if keyword:
        works = filter_by_keyword(works, keyword)
    ids_para_cit = {
        f"doi:{normalize_doi(w['doi'])}": w.get("year", 0)
        for w in works
        if w.get("doi")
    }
    doi_to_cit = fetch_citations(ids_para_cit)
    unique: List[Dict[str, Any]] = []
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
    sorted_works = sorted(unique, key=lambda x: x["cited_by_count"], reverse=True)
    return {
        "orcid_id":                  orcid_id,
        "year_filter":               year,
        "keyword_filter":            keyword,
        "works_sorted_by_citations": sorted_works
    }


def get_orcid_metrics(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna métricas agregadas do autor ORCID:
    total de publicações, total de citações, média de citações,
    fator de impacto (últimos 2 anos), h-index, i10-index e
    pesquisa mais citada.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: Métricas calculadas.

    Raises:
        HTTPException: Em caso de erro ao buscar dados ou citações.
    """
    orcid_data = fetch_orcid(orcid_id, section="works")
    ids, no_id_years = parse_orcid_data(orcid_data or {})
    citations = fetch_citations(ids)
    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)
    return compute_metrics(years, pubs_y, cites_y, ids, no_id_years, citations)


def get_orcid_stats(orcid_id: str) -> Dict[str, Any]:
    """
    Retorna série temporal de publicações e citações por ano.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {
            "years": List[int],
            "publications": List[int],
            "citations": List[int]
        }

    Raises:
        HTTPException: Em caso de erro ao buscar dados ou citações.
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
