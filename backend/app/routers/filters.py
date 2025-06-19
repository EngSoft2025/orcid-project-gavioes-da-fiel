from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.orcid_service import filter_works_by_keyword, filter_works_by_year, filter_works_by_citations
from app.utils.utils import normalize_orcid

router = APIRouter()

@router.get("/filter_by_keyword")
def by_keyword(
    orcid_id: str,
    keyword: str = Query(...),
    year: Optional[int] = Query(None, ge=0)
):
    oid = normalize_orcid(orcid_id)
    return filter_works_by_keyword(oid, keyword, year)

@router.get("/filter_by_year")
def by_year(
    orcid_id: str,
    year: int = Query(..., ge=0),
    keyword: Optional[str] = Query(None)
):
    oid = normalize_orcid(orcid_id)
    return filter_works_by_year(oid, year, keyword)

@router.get("/filter_by_citations")
def by_citations(
    orcid_id: str,
    year: Optional[int] = Query(None, ge=0),
    keyword: Optional[str] = Query(None)
):
    oid = normalize_orcid(orcid_id)
    return filter_works_by_citations(oid, year, keyword)
