import requests
import argparse
import sys

BASE_URL = "https://api.openalex.org"

def search_author_by_name(name, max_results=5):
    url = f"{BASE_URL}/authors"
    params = {"search": name, "per-page": max_results}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()["results"]

    print(f"\n🔍 Autores encontrados para: '{name}'")
    for author in data:
        print(f"- Nome: {author.get('display_name')}")
        print(f"  ID: {author.get('id')}")
        print(f"  Instituição: {author.get('last_known_institution', {}).get('display_name')}")
        print()

def get_author_works(author_openalex_id, max_results=5):
    author_id = author_openalex_id.replace("https://openalex.org/", "")
    url = f"{BASE_URL}/works"
    params = {
        "filter": f"author.id:{author_id}",
        "sort": "publication_date:desc",
        "per-page": max_results
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    works = response.json()["results"]

    print(f"\n📝 Trabalhos do autor ({author_openalex_id}):")
    for w in works:
        print(f"- Título: {w.get('title')}")
        print(f"  Ano: {w.get('publication_year')}")
        print(f"  DOI: {w.get('doi')}")
        print(f"  Citations: {w.get('cited_by_count')}")
        print()

def get_institution_info(name, max_results=3):
    """
    Busca informações sobre instituições pelo nome.
    """
    url = f"{BASE_URL}/institutions"
    params = {"search": name, "per-page": max_results}
    response = requests.get(url, params=params)
    response.raise_for_status()
    institutions = response.json()["results"]

    if not institutions:
        print(f"Nenhuma instituição encontrada para '{name}'.")
        return

    print(f"\n🏛️ Instituições encontradas para: '{name}'")
    for inst in institutions:
        print(f"- Nome: {inst.get('display_name')}")
        print(f"  ID: {inst.get('id')}")
        print(f"  País: {inst.get('country_code')}, Cidade: {inst.get('geo', {}).get('city')}")
        print(f"  Trabalhos: {inst.get('works_count')}, Citações: {inst.get('cited_by_count')}")
        print()

BASE_URL = "https://api.openalex.org"

def search_author_by_orcid(orcid):
    url = f"{BASE_URL}/authors/orcid:{orcid}"
    params = {
        "mailto": "gabrielabreu571@gmail.com"
    }
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Mostra código e mensagem de erro retornada
        print(f"Erro {response.status_code}: {response.text}")
        return

    author = response.json()
    print(f"\n🔍 Autor encontrado: {author['display_name']}")
    print(f"- OpenAlex ID: {author['id']}")
    inst = author.get("last_known_institution") or {}
    print(f"- Instituição: {inst.get('display_name', '—')}")
    print(f"- Trabalhos publicados: {author.get('works_count')}")
    print(f"- Citações recebidas: {author.get('cited_by_count')}\n")



def main():
    parser = argparse.ArgumentParser(description="Consulta OpenAlex")
    parser.add_argument("query", help="Nome do autor ou ID OpenAlex")
    parser.add_argument("--mode", choices=["search-author", "author-works", "institution", "search-orcid"], default="search-author")
    parser.add_argument("--count", type=int, default=5, help="Número de resultados")
    args = parser.parse_args()

    if args.mode == "search-author":
        search_author_by_name(args.query, max_results=args.count)
    elif args.mode == "author-works":
        get_author_works(args.query, max_results=args.count)
    elif args.mode == "institution":
        get_institution_info(args.query, max_results=args.count)
    elif args.mode == "search-orcid":
        search_author_by_orcid(args.query)
    else:
        print("Modo inválido", file=sys.stderr)
    
if __name__ == "__main__":
    main()
