import requests
import sys
import html

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
            raw_title = summary.get("title", {}) \
                               .get("title", {}) \
                               .get("value", "Sem título")
            title = html.unescape(raw_title)

            pub_date = summary.get("publication-date") or {}
            year = (pub_date.get("year") or {}).get("value")
            # ignora obras sem ano válido
            try:
                year = int(year)
            except (TypeError, ValueError):
                continue

            # extrair DOI a partir de external-ids
            doi_link = None
            ext_ids = (summary.get("external-ids") or {}).get("external-id", []) or []
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
    # obtém ORCID iD
    if len(sys.argv) > 1:
        orcid = sys.argv[1]
    else:
        orcid = input("Digite o ORCID iD (ex: 0000-0003-1574-0784): ").strip()

    works = fetch_orcid_works(orcid)
    if not works:
        print("Nenhuma publicação encontrada ou erro na requisição.")
        sys.exit(0)

    # 1) extrai anos únicos e ordena
    anos = sorted({year for (_, year, _) in works})

    # 2) exibe anos numerados
    print(f"\nAnos com publicações para {orcid}:")
    for idx, ano in enumerate(anos, start=1):
        print(f" {idx}. {ano}")

    # 3) usuário escolhe um ano
    escolha = input("\nEscolha o número do ano para filtrar: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(anos)):
        print("Escolha inválida.")
        sys.exit(1)
    ano_sel = anos[int(escolha) - 1]

    # 4) filtra obras por ano
    filtradas = [(t, y, link) for (t, y, link) in works if y == ano_sel]

    # 5) mostra resultados
    print(f"\nPublicações de {ano_sel}:\n")
    if not filtradas:
        print("Nenhuma publicação encontrada neste ano.")
    else:
        for title, year, link in filtradas:
            print(f"- {title} ({year})\n  Link: {link}")
    print()
