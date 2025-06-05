import asyncio
import aiohttp
import unicodedata
import re
import collections
import json
import datetime


# ---- constantes ----
HEADERS  = {"User-Agent": "orcid-colab/4.1"}
ID_TYPES = {"doi", "pmid", "pmcid", "arxiv"}
CHUNK, CONC = 100, 15

# ---- I/O ----
def get_orcid() -> str:
    return input("Digite seu ORCID (exemplo: 0000-0003-1574-0784): ").strip()

# ---- normalização ----
def _norm(text: str) -> str:
    return re.sub(
        r"\W+","",
        unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode()
    ).lower()

# ---- ORCID fetch ----
async def fetch_orcid(orcid: str) -> dict:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    async with aiohttp.ClientSession(headers=HEADERS) as sess:
        for attempt in range(2):
            try:
                async with sess.get(url,
                                    headers={"Accept": "application/json"},
                                    timeout=60) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except asyncio.TimeoutError:
                if attempt == 1:
                    raise

# ---- parsing de obras ----
def parse_orcid_data(data: dict) -> tuple[dict[str,int], list[int]]:
    ids: dict[str,int] = {}
    no_id_years: list[int] = []

    for group in data.get("group", []):
        for work in group.get("work-summary", []):
            year = int(
                (work.get("publication-date") or {})
                    .get("year", {})
                    .get("value", 0)
            )
            if not year:
                continue

            for ext in (work.get("external-ids") or {}).get("external-id", []):
                tp = ext.get("external-id-type", "").lower()
                if tp in ID_TYPES:
                    key = f"{tp}:{ext['external-id-value'].strip().lower()}"
                    ids[key] = year
                    break
            else:
                no_id_years.append(year)

    return ids, no_id_years

# ---- OpenAlex fetch ----
async def fetch_chunk(sess: aiohttp.ClientSession, tp: str, vals: list[str]) -> dict:
    params = {
        "filter": f"{tp}:{'|'.join(vals)}",
        "per-page": len(vals),
        "select": f"{tp},cited_by_count"
    }
    async with sess.get("https://api.openalex.org/works",
                        params=params,
                        timeout=60) as resp:
        resp.raise_for_status()
        return await resp.json()

async def fetch_citations(ids: dict[str,int]) -> dict[str,int]:
    by_type: dict[str,list[str]] = collections.defaultdict(list)
    for key in ids:
        tp, val = key.split(":", 1)
        by_type[tp].append(val)

    citations: dict[str,int] = {}
    sem = asyncio.Semaphore(CONC)
    async with aiohttp.ClientSession(headers=HEADERS) as sess:
        async def worker(tp: str, vals: list[str]):
            local: dict[str,int] = {}
            for i in range(0, len(vals), CHUNK):
                chunk = vals[i : i+CHUNK]
                async with sem:
                    data = await fetch_chunk(sess, tp, chunk)
                for w in data["results"]:
                    raw = (w.get(tp) or w.get("ids", {}).get(tp) or "")
                    key = f"{tp}:{raw.lower().lstrip('https://doi.org/')}"
                    local[key] = w.get("cited_by_count", 0)
            for v in vals:
                local.setdefault(f"{tp}:{v}", 0)
            citations.update(local)

        await asyncio.gather(*(worker(tp, vals) for tp, vals in by_type.items()))

    return citations

# ---- contagem por ano ----
def count_by_year(
    ids: dict[str,int],
    no_id_years: list[int],
    citations: dict[str,int]
) -> tuple[list[int], list[int], list[int]]:
    pubs = collections.Counter()
    cites = collections.Counter()

    for key, year in ids.items():
        pubs[year] += 1
        cites[year] += citations.get(key, 0)
    for year in no_id_years:
        pubs[year] += 1

    years = sorted(pubs)
    pubs_y = [pubs[y] for y in years]
    cites_y = [cites[y] for y in years]
    return years, pubs_y, cites_y

# ---- métricas agregadas ----

def compute_metrics(
    years: list[int],
    pubs_y: list[int],
    cites_y: list[int],
    ids: dict[str,int],
    no_id_years: list[int],
    citations: dict[str,int]
) -> dict[str, float | int]:
    # 1) totais gerais
    works_count     = sum(pubs_y)
    citations_count = sum(cites_y)

    # 2) média de citações por trabalho
    average_citations = (citations_count / works_count) if works_count else 0.0

    # 3) fator de impacto (ultimos 2 anos)
    current_year = datetime.date.today().year
    cutoff_year  = current_year - 2
    recent_works = sum(pub for yr, pub in zip(years, pubs_y) if yr >= cutoff_year)
    recent_cites = sum(cit for yr, cit in zip(years, cites_y) if yr >= cutoff_year)
    impact_factor_2y = (recent_cites / recent_works) if recent_works else 0.0

    # 4) lista de citações ordenada para h-index / i10 / mais citado
    all_cits = list(citations.values()) + [0]*len(no_id_years)
    all_cits.sort(reverse=True)

    # 5) h-index
    h = 0
    for i, c in enumerate(all_cits, 1):
        if c >= i:
            h = i
        else:
            break

    # 6) i10-index
    i10 = sum(1 for c in all_cits if c >= 10)

    # 7) trabalho mais citado
    most_cited = all_cits[0] if all_cits else 0

    # 8) formatação com 2 casas decimais
    impact_factor_2y = float(f"{impact_factor_2y:.2f}")
    average_citations = float(f"{average_citations:.2f}")

    return {
        "total_publicacoes":     works_count,
        "total_citacoes":        citations_count,
        "media_citacoes":     average_citations,
        "fator_de_impacto":      impact_factor_2y,
        "h_index":               h,
        "i10_index":             i10,
        "pesquisa_mais_citada":            most_cited
    }

# ---- main ----
async def main():
    orcid = get_orcid()

    orcid_data = await fetch_orcid(orcid)
    ids, no_id_years = parse_orcid_data(orcid_data)
    citations = await fetch_citations(ids)
    years, pubs_y, cites_y = count_by_year(ids, no_id_years, citations)

    metrics = compute_metrics(years, pubs_y, cites_y, ids, no_id_years, citations)

    output = {
        "years": years,
        "publications": pubs_y,
        "citations": cites_y,
        **metrics,
        # "topics": topics
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
