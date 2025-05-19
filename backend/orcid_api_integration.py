import requests
import json
import html
import argparse
import sys
import time
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# Constantes de configuração
BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 10  # segundos de timeout por request

TOP_LEVEL = ["record", "person", "activities"]
PERSON_SECTIONS = [
    "address", "email", "external-identifiers",
    "researcher-urls", "other-names", "keywords"
]

def create_session(retries=5, backoff_factor=1.0,
                   status_forcelist=(429, 500, 502, 503, 504)):
    """
    Configura uma Session com retry e backoff exponencial.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SESSION = create_session()

def fetch_endpoint(orcid_id: str, section: str):
    """
    Tenta buscar o JSON de um endpoint; em caso de erro retorna None.
    """
    url = f"{BASE_URL}/{orcid_id}/{section}"
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter '{section}' para {orcid_id}: {e}", file=sys.stderr)
        return None

def get_nome(orcid_id: str):
    """
    Recupera e imprime o nome completo de um autor a partir do seu ORCID iD.
    """
    data = fetch_endpoint(orcid_id, "")
    if not data:
        print(f"Erro ao obter dados básicos para {orcid_id}.")
        return

    person = data.get("person", {})
    nome = person.get("name", {}) \
                 .get("given-names", {}) \
                 .get("value", "")
    sobrenome = person.get("name", {}) \
                      .get("family-name", {}) \
                      .get("value", "")
    print(f"Nome completo: {nome} {sobrenome}\n")

def get_list_of_publications_from_author(orcid_id: str):
    """
    Lista as publicações (works), decodificando HTML entities.
    """
    data = fetch_endpoint(orcid_id, "works")
    if not data:
        print(f"Erro ao obter publicações para {orcid_id}.")
        return

    groups = data.get("group", [])
    if not groups:
        print(f"Nenhuma publicação encontrada para {orcid_id}.\n")
        return

    print(f"Publicações encontradas para {orcid_id}:\n")
    for group in groups:
        for summary in group.get("work-summary", []):
            raw_title = summary.get("title", {}) \
                               .get("title", {}) \
                               .get("value", "Sem título")
            title = html.unescape(raw_title)

            pub_date = summary.get("publication-date", {}) or {}
            year = pub_date.get("year", {}) \
                           .get("value", "----")
            print(f"- {title} ({year})")
    print()

def get_list_keywords(orcid_id: str):
    """
    Busca e imprime a lista de palavras-chave (keywords) via API.
    Suporta resposta com 'keywords.keyword' ou raiz 'keyword'.
    """
    data = fetch_endpoint(orcid_id, "keywords")
    if not data:
        print(f"Nenhum dado de keywords obtido para {orcid_id}.")
        return

    # detecta estrutura de lista de keywords
    if isinstance(data.get('keywords'), dict):
        items = data['keywords'].get('keyword', [])
    else:
        items = data.get('keyword', [])

    if not items:
        print(f"Nenhuma palavra-chave encontrada para {orcid_id}.\n")
        return

    print(f"Palavras-chave para {orcid_id}:\n")
    for kw in items:
        content = kw.get('content') or '----'
        print(f"- {html.unescape(content)}")
    print()


def get_list_all_personal_data(orcid_id: str):
    """
    Busca e imprime todos os dados pessoais públicos via API.
    """
    data = fetch_endpoint(orcid_id, "person")
    if not data:
        print(f"Nenhum dado de pessoa obtido para {orcid_id}.")
        return

    # o endpoint /v3.0/{orcid}/person retorna diretamente o objeto person,
    # enquanto /v3.0/{orcid} retorna { "person": {...} }
    person = data.get("person", data)

    # Nome
    name = person.get("name", {})
    given = name.get("given-names", {}).get("value", "")
    family = name.get("family-name", {}).get("value", "")
    print(f"Nome completo: {given} {family}")

    # Biografia
    bio = person.get("biography", {}).get("content")
    if bio:
        print(f"Biografia: {html.unescape(bio)}")

    # Outros nomes
    other_names = person.get("other-names", {}).get("other-name", [])
    if other_names:
        print("\nOutros nomes:")
        for o in other_names:
            print(f"- {o.get('content','')}")

    # URLs de pesquisador
    urls = person.get("researcher-urls", {}).get("researcher-url", [])
    if urls:
        print("\nURLs de pesquisador:")
        for u in urls:
            link = u.get("url", {}).get("value", "")
            label = u.get("url-name")
            # só exibe o rótulo se não for None
            if label:
                print(f"- {label}: {link}")
            else:
                print(f"- {link}")

    # E-mails
    emails = person.get("emails", {}).get("email", [])
    if emails:
        print("\nE-mails:")
        for e in emails:
            addr = e.get("email", "")
            suffix = " (principal)" if e.get("primary", False) else ""
            print(f"- {addr}{suffix}")

    # Endereços (este endpoint só traz country)
    addresses = person.get("addresses", {}).get("address", [])
    if addresses:
        print("\nEndereços:")
        for a in addresses:
            country = a.get("country", {}).get("value", "")
            if country:
                print(f"- {country}")

    # Identificadores externos
    externals = person.get("external-identifiers", {}).get("external-identifier", [])
    if externals:
        print("\nIdentificadores externos:")
        for ex in externals:
            id_type = ex.get("external-id-type", "")
            id_val = ex.get("external-id-value", "")
            print(f"- {id_type}: {id_val}")

    print()

import requests.utils
import html

def search_by_name(name: str, max_results: int = 10):
    """
    Busca e imprime autores cujo nome corresponde ao termo.
    """
    # formata a query e monta a URL de busca
    query = requests.utils.quote(name)
    url = f"{BASE_URL}/search/?q={query}&rows={max_results}"
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar por nome '{name}': {e}")
        return

    data = resp.json()
    results = data.get("result", [])
    if not results:
        print(f"Nenhum autor encontrado para '{name}'.\n")
        return

    print(f"Autores encontrados para '{name}':\n")
    for item in results:
        identifier = item.get("orcid-identifier", {})
        orcid = identifier.get("path", "")
        person = item.get("person", {})
        pname = person.get("name", {})
        given = pname.get("given-names", {}).get("value", "")
        family = pname.get("family-name", {}).get("value", "")
        print(f"- {given} {family} (ORCID: {orcid})")
    print()

def search_by_work_title(title: str, max_results: int = 10):
    """
    Busca e imprime registros de autores que publicaram obras cujo título corresponde ao termo.
    """
    # usa o campo title na query de busca
    q = f"title:\"{title}\""
    query = requests.utils.quote(q)
    url = f"{BASE_URL}/search/?q={query}&rows={max_results}"
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar por título '{title}': {e}")
        return

    data = resp.json()
    results = data.get("result", [])
    if not results:
        print(f"Nenhuma obra encontrada para '{title}'.\n")
        return

    print(f"Registros encontrados para título '{title}':\n")
    for item in results:
        identifier = item.get("orcid-identifier", {})
        orcid = identifier.get("path", "")
        print(f"- ORCID: {orcid}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Utilitário ORCID e Busca")
    parser.add_argument(
        "identifier",
        help="ORCID iD do autor (ex: 0000-0003-1574-0784) ou termo de busca, dependendo do modo"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["nome", "works", "keywords", "personal", "all", "search-name", "search-work"],
        default="all",
        help="Modo de operação: nome, works, keywords, personal, all, search-name ou search-work"
    )
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="Máximo de resultados para buscas (apenas search-name e search-work)"
    )
    args = parser.parse_args()
    identifier = args.identifier
    mode = args.mode

    '''
        buscas por ocrid id: 
            python3 codigo.py orcid_id -- mode {função que vc quer}
    
        Se for buscar por nome: 
            python3 codigo.py "nome" -- mode função que vc quer
    '''

    if mode == "nome":
        get_nome(identifier)
    elif mode == "works":
        get_list_of_publications_from_author(identifier)
    elif mode == "keywords":
        get_list_keywords(identifier)
    elif mode == "personal":
        get_list_all_personal_data(identifier)
    elif mode == "search-name":
        search_by_name(identifier, max_results=args.max_results)
    elif mode == "search-work":
        search_by_work_title(identifier, max_results=args.max_results)
    elif mode == "all":
        get_nome(identifier)
        get_list_of_publications_from_author(identifier)
        get_list_keywords(identifier)
        get_list_all_personal_data(identifier)
    else:
        print(f"Modo desconhecido: {mode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
