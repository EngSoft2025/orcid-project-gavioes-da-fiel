import requests
import sys
import html

def fetch_orcid_keywords(orcid_id: str):
    """
    Retorna a lista de keywords cadastradas no perfil ORCID.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
    headers = {"Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Erro na requisição de record: {resp.status_code}")
        return []

    data = resp.json()
    keywords = data.get("person", {}) \
                   .get("keywords", {}) \
                   .get("keyword", [])
    return [html.unescape(kw.get("content", "")) for kw in keywords]


def fetch_orcid_works(orcid_id: str):
    """
    Retorna lista de tuplas (title, year, doi_link) de todas as publicações.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Erro na requisição de works: {resp.status_code}")
        return []

    works = []
    data = resp.json()
    for group in data.get("group", []):
        for summary in group.get("work-summary", []):
            # título
            raw_title = summary \
                .get("title", {}) \
                .get("title", {}) \
                .get("value", "Sem título")
            title = html.unescape(raw_title)

            # ano
            pub_date = summary.get("publication-date") or {}
            year = (pub_date.get("year") or {}).get("value", "----")

            # extrair DOI a partir de external-ids
            doi_link = None
            ext_ids_container = summary.get("external-ids")
            if isinstance(ext_ids_container, dict):
                ext_ids = ext_ids_container.get("external-id", []) or []
            else:
                ext_ids = []

            for ext in ext_ids:
                if ext.get("external-id-type", "").lower() == "doi":
                    url_obj = ext.get("external-id-url")
                    if isinstance(url_obj, dict) and url_obj.get("value"):
                        doi_link = url_obj["value"]
                    else:
                        doi_val = ext.get("external-id-value")
                        if doi_val:
                            doi_link = f"https://doi.org/{doi_val}"
                    break

            works.append((title, year, doi_link or "Link não disponível"))
    return works


if __name__ == "__main__":
    # ORCID pela CLI ou input
    if len(sys.argv) > 1:
        orcid = sys.argv[1]
    else:
        orcid = input("Digite o ORCID iD (ex: 0000-0003-1574-0784): ").strip()

    # 1) Pega as keywords
    kw_list = fetch_orcid_keywords(orcid)
    if not kw_list:
        print("Nenhuma keyword cadastrada ou erro na requisição.")
        sys.exit(0)

    # 2) Mostra as keywords numeradas
    print(f"\nKeywords de {orcid}:")
    for idx, kw in enumerate(kw_list, start=1):
        print(f" {idx}. {kw}")

    # 3) Usuário escolhe uma
    escolha = input("\nEscolha o número da keyword para filtrar as publicações: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(kw_list)):
        print("Escolha inválida.")
        sys.exit(1)
    selected_kw = kw_list[int(escolha) - 1]

    # 4) Busca todas as publicações e filtra por keyword no título
    works = fetch_orcid_works(orcid)
    filtered = [
        (t, y, link)
        for (t, y, link) in works
        if selected_kw.lower() in t.lower()
    ]

    # 5) Mostra o resultado com DOI extraído da API
    print(f"\nPublicações com a keyword “{selected_kw}”:\n")
    if not filtered:
        print("Nenhuma publicação encontrada com essa keyword.")
    else:
        for title, year, doi_link in filtered:
            print(f"- {title} ({year})\n  DOI: {doi_link}")
    print()
