# app/routers/orcid.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from app.services.orcid_service import (
    search_by_name,
    get_name,
    get_keywords,
    get_personal,
    get_employments,
    get_educations,
    get_all_data,
    get_orcid_metrics,
    get_orcid_stats,
)
from app.utils.utils import normalize_orcid

router = APIRouter()


@router.get("/search/name", response_model=List[Dict[str, str]])
def search_name(query: str, max_results: int = 10):
    """
    Busca autores cujo nome corresponde ao termo e retorna JSON com "orcid" e "full_name".
    """
    return search_by_name(query, max_results)


@router.get("/{orcid_id}/name")
def read_name(orcid_id: str):
    """
    Retorna o nome formatado completo do autor ORCID.
    """
    oid = normalize_orcid(orcid_id)
    return get_name(oid)


@router.get("/{orcid_id}/keywords")
def read_keywords(orcid_id: str):
    """
    Retorna as keywords associadas ao autor ORCID.
    """
    oid = normalize_orcid(orcid_id)
    return get_keywords(oid)


@router.get("/{orcid_id}/personal")
def read_personal(orcid_id: str):
    """
    Retorna informações pessoais (nome, biografia, e-mails, etc.).
    """
    oid = normalize_orcid(orcid_id)
    return get_personal(oid)


@router.get("/{orcid_id}/employments")
def read_employments(orcid_id: str):
    """
    Retorna histórico de empregos do autor.
    """
    oid = normalize_orcid(orcid_id)
    return get_employments(oid)


@router.get("/{orcid_id}/educations")
def read_educations(orcid_id: str):
    """
    Retorna histórico educacional do autor.
    """
    oid = normalize_orcid(orcid_id)
    return get_educations(oid)


@router.get("/{orcid_id}/all")
def read_all(orcid_id: str):
    """
    Monta um JSON unificado com nome, obras, keywords, dados pessoais, empregos e formações.
    """
    oid = normalize_orcid(orcid_id)
    data = get_all_data(oid)
    if not data:
        raise HTTPException(status_code=404, detail="ORCID não encontrado")
    return data


@router.get("/{orcid_id}/metrics")
def metrics(orcid_id: str):
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
    oid = normalize_orcid(orcid_id)
    return get_orcid_metrics(oid)


@router.get("/{orcid_id}/stats")
def stats(orcid_id: str):
    """
    Retorna a série temporal para construção de gráfico:
    {
      "years": [...],
      "publications": [...],
      "citations": [...]
    }
    """
    oid = normalize_orcid(orcid_id)
    return get_orcid_stats(oid)
