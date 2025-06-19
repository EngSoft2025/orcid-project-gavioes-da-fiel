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

# Router para os endpoints de "works" (via ORCID)
works_router = APIRouter(
    prefix="/orcid/{orcid_id}/works",
    tags=["Works"],
)

@works_router.get("/")
def list_works(orcid_id: str):
    oid = normalize_orcid(orcid_id)
    return get_works(oid)

@works_router.get("/with_authors")
def list_works_with_authors(orcid_id: str):
    oid = normalize_orcid(orcid_id)
    return get_works_with_authors(oid)

@works_router.get("/openalex")
def list_works_openalex(orcid_id: str):
    oid = normalize_orcid(orcid_id)
    return get_works_openalex(oid)


# Router para o endpoint de publicação por DOI (via OpenAlex + ORCID)
publication_router = APIRouter(
    prefix="/works/publication",
    tags=["Publication"],
)

@publication_router.get("/{doi:path}", response_model=Dict[str, Any])
def get_publication(doi: str):
    d_norm = normalize_doi(doi)
    try:
        return get_publication_details(d_norm)
    except HTTPException as e:
        # propaga 404, 502, etc.
        raise e
