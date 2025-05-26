project/
│
├── api_clients/
│   ├── __init__.py
│   ├── orcid_client.py       # fetch_orcid, formatters, search_orcid_by_name…
│   └── openalex_client.py    # fetch_works_openalex, format_works_from_openalex…
│
└── endpoints.py             # código acima

Para rodar o servidor:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn endpoints:app --reload --port 8000