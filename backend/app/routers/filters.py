from fastapi import APIRouter, Query
from typing import Optional

from app.services.orcid_service import (
    filter_works_by_keyword,
    filter_works_by_year,
    filter_works_by_citations
)
from app.utils.utils import normalize_orcid

router = APIRouter()

@router.get("/filter_by_keyword")
def by_keyword(
    orcid_id: str,
    keyword: str = Query(..., description="Palavra-chave para buscar em títulos, resumos ou keywords"),
    year: Optional[int] = Query(None, ge=0, description="Ano opcional para pré-filtrar as obras")
):
    """
    Filtra as obras de um autor por palavra-chave, opcionalmente pré-filtrando por ano.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        keyword (str): Palavra-chave a ser buscada.
        year (Optional[int]): Ano para pré-filtrar as obras.

    Returns:
        dict: {
            "orcid_id": str,
            "keyword_searched": str,
            "year_filter": Optional[int],
            "works": List[Dict]
        }
    """
    oid = normalize_orcid(orcid_id)
    return filter_works_by_keyword(oid, keyword, year)


@router.get("/filter_by_year")
def by_year(
    orcid_id: str,
    year: int = Query(..., ge=0, description="Ano de publicação para filtrar"),
    keyword: Optional[str] = Query(None, description="Palavra-chave opcional para filtrar após o ano")
):
    """
    Filtra as obras de um autor por ano de publicação, opcionalmente por palavra-chave.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        year (int): Ano de publicação para filtrar as obras.
        keyword (Optional[str]): Palavra-chave para filtro adicional.

    Returns:
        dict: {
            "orcid_id": str,
            "year": int,
            "keyword_filter": Optional[str],
            "works": List[Dict]
        }
    """
    oid = normalize_orcid(orcid_id)
    return filter_works_by_year(oid, year, keyword)


@router.get("/filter_by_citations")
def by_citations(
    orcid_id: str,
    year: Optional[int] = Query(None, ge=0, description="Ano opcional para pré-filtrar as obras"),
    keyword: Optional[str] = Query(None, description="Palavra-chave opcional para pré-filtrar as obras")
):
    """
    Filtra as obras de um autor por número de citações, opcionalmente pré-filtrando por ano e/ou palavra-chave.

    Args:
        orcid_id (str): Identificador ORCID do autor.
        year (Optional[int]): Ano para pré-filtrar as obras.
        keyword (Optional[str]): Palavra-chave para filtro antes da ordenação.

    Returns:
        dict: {
            "orcid_id": str,
            "year_filter": Optional[int],
            "keyword_filter": Optional[str],
            "works_sorted_by_citations": List[Dict]
        }
    """
    oid = normalize_orcid(orcid_id)
    return filter_works_by_citations(oid, year, keyword)
