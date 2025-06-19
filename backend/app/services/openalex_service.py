# app/services/openalex_service.py

from typing import Dict, Any, Optional
import requests
from fastapi import HTTPException

from api_clients.openalex_client import (
    # (Caso queira reutilizar métricas ou outros helpers do OpenAlex)
    # parse_orcid_data,
    # fetch_citations,
    # count_by_year,
    # compute_metrics,
    format_works_from_openalex
)
from api_clients.orcid_client import (
    fetch_orcid,
    format_works as format_orcid_works
)
from app.utils.utils import normalize_doi, normalize_orcid


def get_publication_details(doi: str) -> Dict[str, Any]:
    """
    Busca detalhes de uma publicação pelo DOI:
    - Recupera dados do OpenAlex
    - Extrai autor principal com ORCID e, se disponível, obtém detalhes
      adicionais do registro ORCID para complementar o resultado.
    """
    # 1. Normaliza o DOI
    d_norm = normalize_doi(doi)
    key = f"doi:{d_norm}"

    # 2. Chama a API do OpenAlex
    oa_url = f"https://api.openalex.org/works/{key}"
    try:
        resp = requests.get(oa_url, timeout=10)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar ao OpenAlex: {e}")

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Obra não encontrada no OpenAlex para esse DOI")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar obra no OpenAlex")

    work_oa = resp.json()

    # 3. Tenta extrair o primeiro ORCID de autoria
    first_orcid_url: Optional[str] = next(
        (
            a["author"]["orcid"]
            for a in work_oa.get("authorships", [])
            if a.get("author", {}).get("orcid")
        ),
        None
    )

    orcid_rec: Optional[Dict[str, Any]] = None
    if first_orcid_url:
        oid = normalize_orcid(first_orcid_url)
        raw = fetch_orcid(oid, section="works") or {}
        formatted = format_orcid_works(raw) or []
        for w in formatted:
            if w.get("doi") and normalize_doi(w["doi"]) == d_norm:
                orcid_rec = w.copy()
                orcid_rec["orcid_id"] = oid
                break

    # 4. Monta o resultado base a partir do OpenAlex
    result: Dict[str, Any] = {
        "doi":              d_norm,
        "id":               work_oa.get("id"),
        "title":            work_oa.get("display_name"),
        "publication_year": work_oa.get("publication_year"),
        "type":             work_oa.get("type"),
        "cited_by_count":   work_oa.get("cited_by_count"),
        "authorships": [
            {
                "author_name":  a["author"].get("display_name"),
                "author_orcid": a["author"].get("orcid")
            }
            for a in work_oa.get("authorships", [])
        ]
    }

    # 5. Se houver dados do ORCID, complementa campos adicionais
    if orcid_rec:
        for fld in ("container", "url", "path"):
            if orcid_rec.get(fld) and fld not in result:
                result[fld] = orcid_rec[fld]

        # Ajusta ano se houver discrepância
        yr = orcid_rec.get("year")
        try:
            yr_int = int(yr)  # type: ignore
        except Exception:
            yr_int = None
        if yr_int and int(result["publication_year"]) != yr_int:  # type: ignore
            result["orcid_publication_year"] = yr

    return result


def get_works_from_openalex(orcid_id: str) -> Dict[str, Any]:
    """
    Proxy para format_works_from_openalex, trazendo obras completas
    do OpenAlex para um dado ORCID.
    """
    try:
        works = format_works_from_openalex(orcid_id)
        return {"works": works}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar obras no OpenAlex: {e}")
