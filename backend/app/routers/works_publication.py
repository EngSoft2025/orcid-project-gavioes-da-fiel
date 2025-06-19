# app/routers/works_publication.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.orcid_service import (
    get_works,
    get_works_with_authors,
    get_works_openalex,
)
from app.services.openalex_service import get_publication_details, get_works_from_openalex
from app.utils.utils import normalize_orcid, normalize_doi

# Router para endpoints de obras via ORCID
works_router = APIRouter(
    prefix="/orcid/{orcid_id}/works",
    tags=["Works"],
    responses={404: {"description": "Recurso não encontrado"}}
)

@works_router.get("/")
def list_works(orcid_id: str):
    """
    Retorna todas as obras de um autor ORCID, incluindo contagem de citações.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        dict: {
            "orcid_id": str,
            "works": List[Dict[str, Any]]
        }
    """
    oid = normalize_orcid(orcid_id)
    return get_works(oid)


@works_router.get("/with_authors")
def list_works_with_authors(orcid_id: str):
    """
    Retorna todas as obras de um autor, com lista de coautores.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        dict: {
            "works": List[Dict[str, Any]]
        }
    """
    oid = normalize_orcid(orcid_id)
    return get_works_with_authors(oid)


@works_router.get("/openalex")
def list_works_openalex(orcid_id: str):
    """
    Recupera publicações de um autor via OpenAlex, incluindo coautores e citações.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        dict: {
            "works": List[Dict[str, Any]]
        }
    """
    oid = normalize_orcid(orcid_id)
    return get_works_openalex(oid)


# Router para endpoint de detalhes de publicação via DOI
publication_router = APIRouter(
    prefix="/works/publication",
    tags=["Publication"],
    responses={
        404: {"description": "Publicação não encontrada"},
        502: {"description": "Erro de comunicação com serviço externo"}
    }
)

@publication_router.get("/{doi:path}", response_model=Dict[str, Any])
def get_publication(doi: str):
    """
    Retorna detalhes de uma publicação a partir do DOI,
    combinando dados do OpenAlex e, se disponível, do ORCID.

    Args:
        doi (str): DOI da publicação (com ou sem prefixo "doi:" ou URL).

    Returns:
        Dict[str, Any]: {
            "doi": str,
            "id": str,
            "title": str,
            "publication_year": int,
            "type": str,
            "cited_by_count": int,
            "authorships": List[Dict[str, str]],
            ... (campos adicionais do ORCID, se houver)
        }

    Raises:
        HTTPException: 
            - 404 se a publicação não for encontrada no OpenAlex,
            - 502 em caso de falha de conexão ou erro externo.
    """
    d_norm = normalize_doi(doi)
    try:
        return get_publication_details(d_norm)
    except HTTPException as e:
        raise e
