# ORCID & OpenAlex Backend

Este é o servidor FastAPI que expõe endpoints para consulta de dados de autores e publicações usando as APIs do ORCID e do OpenAlex.

---

## Funcionalidades

- **Busca de autor por nome**  
- **Dados do autor** (nome, palavras-chave, perfil pessoal, histórico de empregos e formações)  
- **Obras do autor** (via ORCID e OpenAlex), incluindo contagem de citações  
- **Filtros de obras** (por ano, palavra-chave e número de citações)  
- **Métricas agregadas** (total de publicações, citações, h-index, etc.)  
- **Exportação em XML** do perfil completo do pesquisador  
- **Detalhes de uma publicação** a partir de um DOI (OpenAlex + ORCID lookup)  

---

## Estrutura de diretórios

```bash
backend/
├── app/
│   ├── main.py                    # Ponto de entrada FastAPI
│   ├── routers/                   # Definição das rotas
│   │   ├── orcid.py
│   │   ├── filters.py
│   │   └── works_publication.py
│   ├── services/                  # Integração com APIs
│   │   ├── orcid_service.py
│   │   └── openalex_service.py
│   └── utils/                     # Helpers (normalização, filtros, XML)
│       └── utils.py
│
├── api_clients/                   # Wrappers para ORCID / OpenAlex
│   ├── __init__.py
│   ├── orcid_client.py
│   └── openalex_client.py
│
├── requirements.txt               # Dependências Python
└── README.md                      
````

## Pré-requisitos

* Python 3.10+
* pip

---

## Instalação e execução

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
