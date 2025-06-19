# app/services/openalex_service.py

from typing import Dict, Any, Optional
import requests
from fastapi import HTTPException

from api_clients.openalex_client import format_works_from_openalex
from api_clients.orcid_client import fetch_orcid, format_works as format_orcid_works
from app.utils.utils import normalize_doi, normalize_orcid


def get_publication_details(doi: str) -> Dict[str, Any]:
    """
    Retorna detalhes de uma publicação a partir do DOI, combinando dados do OpenAlex
    e, se disponível, informações adicionais do autor no ORCID.

    Args:
        doi (str): DOI da publicação (pode vir com prefixo URL ou "doi:").

    Returns:
        Dict[str, Any]: Dicionário contendo:
            - doi (str)
            - id (str)
            - title (str)
            - publication_year (int)
            - type (str)
            - cited_by_count (int)
            - authorships (List[Dict[str,str]])
            - container, url, path (opcionais, se presentes no ORCID)
            - orcid_publication_year (opcional, se houver discrepância de ano)

    Raises:
        HTTPException:
            - 502: falha na conexão com o OpenAlex
            - 404: publicação não encontrada no OpenAlex
            - demais códigos de erro HTTP repassados
    """
    # Normaliza o DOI e monta a chave para o OpenAlex
    d_norm = normalize_doi(doi)
    key = f"doi:{d_norm}"

    # Consulta o OpenAlex
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

    # Extrai o primeiro ORCID de autoria, se existir
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
        # Busca a obra correspondente no registro ORCID
        for w in formatted:
            if w.get("doi") and normalize_doi(w["doi"]) == d_norm:
                orcid_rec = w.copy()
                orcid_rec["orcid_id"] = oid
                break

    # Monta o resultado base usando dados do OpenAlex
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

    # Se houver registro ORCID, adiciona campos extras
    if orcid_rec:
        for fld in ("container", "url", "path"):
            if orcid_rec.get(fld) and fld not in result:
                result[fld] = orcid_rec[fld]

        # Ajusta ano se houver divergência
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
    Retorna lista de obras de um autor ORCID consultando o OpenAlex.

    Args:
        orcid_id (str): Identificador ORCID do autor.

    Returns:
        Dict[str, Any]: {"works": List[Dict[str, Any]]}

    Raises:
        HTTPException:
            - 500: falha genérica ao obter obras do OpenAlex
    """
    try:
        works = format_works_from_openalex(orcid_id)
        return {"works": works}
    except HTTPException:
        # Repassa erros HTTP conhecidos
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar obras no OpenAlex: {e}")
