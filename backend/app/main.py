# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import orcid, filters
from app.routers.works_publication import works_router, publication_router

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orcid.router, prefix="/orcid", tags=["ORCID"])
app.include_router(works_router)  # prefix="/orcid/{orcid_id}/works", tags=["Works"]
app.include_router(filters.router, prefix="/orcid/{orcid_id}/works", tags=["Filters"])
app.include_router(publication_router)  # prefix="/works/publication", tags=["Publication"]
