# api_clients/orcid_client.py

import html
from typing import List, Dict, Optional

import requests
import unicodedata
from fastapi import HTTPException
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ORCID API configuration
BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 10

def create_session(
    retries: int = 5,
    backoff_factor: float = 1.0,
    status_forcelist: tuple = (429, 500, 502, 503, 504)
) -> requests.Session:
    """
    Cria uma Session do requests com retry configurado.
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

# Sessão global para reuso
SESSION = create_session()

def fetch_orcid(orcid_id: str, section: str = "") -> dict:
    """
    Busca o registro ORCID completo ou uma seção específica.
    Lança HTTPException(502) em caso de erro de comunicação.
    """
    url = f"{BASE_URL}/{orcid_id}/{section}" if section else f"{BASE_URL}/{orcid_id}"
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar ORCID: {e}")

def normalize_name(text: str) -> str:
    """
    Remove acentuação e coloca em minúsculas para comparação.
    Ex: "Isôtâni" -> "isotani"
    """
    nfkd = unicodedata.normalize('NFKD', text)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower()

def search_orcid_by_name(query: str, max_results: int = 15) -> List[Dict[str, str]]:
    """
    Pesquisa autores no ORCID cujo nome contenha todos os termos da query.
    Usa AND na query da API e filtra localmente para garantir coerência.
    Retorna lista de dicts {"orcid": ..., "full_name": ...}.
    """
    # Normaliza tokens
    tokens = [normalize_name(tok) for tok in query.split() if tok.strip()]
    if not tokens:
        return []
    
    # monta query com AND entre termos e URL-encode
    lucene_q = " AND ".join(tokens)
    q_encoded = requests.utils.quote(lucene_q)
    url = f"{BASE_URL}/search/?q={q_encoded}&rows={max_results}"

    # chama API ORCID
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro na ORCID API: {e}")

    data = resp.json()
    raw = data.get("result", []) or []

    # extrai ORCID + full_name
    output: List[Dict[str, str]] = []
    for item in raw:
        orcid_id = item.get("orcid-identifier", {}).get("path")
        if not orcid_id:
            continue
        try:
            record = fetch_orcid(orcid_id)
            name_data = format_name(record)
            full_name = name_data.get("full_name", "") or ""
        except Exception:
            full_name = ""
        output.append({"orcid": orcid_id, "full_name": full_name})

    # filtra localmente: mantém só itens que contenham TODOS os tokens
    output = [
        o for o in output
        if all(tok in normalize_name(o["full_name"]) for tok in tokens)
    ]
    return output

def format_name(data: dict) -> Dict[str, str]:
    """
    Extrai nome completo ('given-names' + 'family-name') do JSON ORCID.
    """
    person = data.get("person", data) or {}
    name = person.get("name", {}) or {}
    given = name.get("given-names", {}).get("value", "")
    family = name.get("family-name", {}).get("value", "")
    return {"full_name": f"{given} {family}".strip()}

def format_personal(data: dict) -> Dict:
    """
    Extrai e formata informações pessoais de um objeto ORCID 'person'.
    Retorna dict com:
      - full_name
      - biography
      - other_names
      - urls
      - emails
      - countries
      - external_ids
    """
    person = (data.get("person") or data) or {}
    result = format_name(person)

    # Biografia
    bio = person.get("biography", {}) or {}
    if isinstance(bio, dict) and bio.get("content"):
        result["biography"] = html.unescape(bio["content"])

    # Outros nomes
    other = person.get("other-names", {}) or {}
    other_list = other.get("other-name", []) or []
    if other_list:
        result["other_names"] = [
            o.get("content") for o in other_list if o and o.get("content")
        ]

    # URLs de pesquisador
    urls = person.get("researcher-urls", {}) or {}
    url_list = urls.get("researcher-url", []) or []
    if url_list:
        result["urls"] = [
            u.get("url", {}).get("value")
            for u in url_list
            if isinstance(u, dict) and u.get("url", {}).get("value")
        ]

    # E-mails
    emails = person.get("emails", {}) or {}
    email_list = emails.get("email", []) or []
    if email_list:
        result["emails"] = [
            e.get("email") for e in email_list if e and e.get("email")
        ]

    # Países (endereços)
    addrs = person.get("addresses", {}) or {}
    addr_list = addrs.get("address", []) or []
    if addr_list:
        result["countries"] = [
            a.get("country", {}).get("value")
            for a in addr_list
            if a and a.get("country", {}).get("value")
        ]

    # Identificadores externos
    ext = person.get("external-identifiers", {}) or {}
    ext_list = ext.get("external-identifier", []) or []
    if ext_list:
        result["external_ids"] = [
            {
                "type": ex.get("external-id-type"),
                "value": ex.get("external-id-value")
            }
            for ex in ext_list
            if ex.get("external-id-type") and ex.get("external-id-value")
        ]

    return result

def format_keywords(data: dict) -> List[str]:
    """
    Extrai lista de palavras-chave de /{orcid_id}/keywords.
    """
    kw_parent = data.get("keywords") or data
    items = kw_parent.get("keyword", []) if isinstance(kw_parent, dict) else []
    return [html.unescape(kw.get("content", "")) for kw in items if kw.get("content")]

def _fmt_date(d: Optional[dict]) -> Optional[str]:
    """
    Formata dict de date (year, month, day) em 'YYYY-M-D'.
    Retorna None se entrada for inválida ou sem componentes.
    """
    if not d or not isinstance(d, dict):
        return None

    # Extrai valores somente se vierem em dicts
    year_dict = d.get("year") or {}
    y = year_dict.get("value")

    month_dict = d.get("month") or {}
    m = month_dict.get("value")

    day_dict = d.get("day") or {}
    day = day_dict.get("value")

    parts = [str(p) for p in (y, m, day) if p is not None]
    return "-".join(parts) if parts else None


def format_employment(data: dict) -> List[Dict]:
    """
    Formata lista de empregos de /{orcid_id}/employments.
    """
    out = []
    for group in data.get("affiliation-group") or []:
        for item in group.get("summaries") or []:
            s = item.get("employment-summary") or {}
            org = s.get("organization") or {}
            out.append({
                "organization": org.get("name"),
                "department":   s.get("department-name"),
                "role_title":   s.get("role-title"),
                "start_date":   _fmt_date(s.get("start-date")),
                "end_date":     _fmt_date(s.get("end-date")),
                "url":          (s.get("url") or {}).get("value")
            })
    return out


def format_education_and_qualifications(data: dict) -> List[Dict]:
    """
    Formata lista de formações de /{orcid_id}/educations.
    """
    out = []
    for group in data.get("affiliation-group") or []:
        for item in group.get("summaries") or []:
            s = item.get("education-summary") or {}
            org = s.get("organization") or {}
            out.append({
                "organization": org.get("name"),
                "department":   s.get("department-name"),
                "role_title":   s.get("role-title"),
                "start_date":   _fmt_date(s.get("start-date")),
                "end_date":     _fmt_date(s.get("end-date")),
                "url":          (s.get("url") or {}).get("value")
            })
    return out

def format_works(data: dict) -> List[Dict]:
    """
    Formata lista de obras de /{orcid_id}/works (resumo de works-group).
    """
    works: List[Dict] = []
    for group in data.get("group", []) or []:
        for summary in group.get("work-summary", []) or []:
            title = html.unescape(
                (summary.get("title") or {}).get("title", {}).get("value", "Sem título")
            )
            year = (summary.get("publication-date") or {}).get("year", {}).get("value", "----")
            work_type = summary.get("type") or "desconhecido"
            container = (summary.get("journal-title") or {}).get("value")
            doi = None
            for ext in (summary.get("external-ids") or {}).get("external-id", []):
                if ext.get("external-id-type", "").lower() == "doi":
                    doi = ext.get("external-id-value")
                    break
            url = (summary.get("url") or {}).get("value")
            path = summary.get("path")
            works.append({
                "title":     title,
                "year":      year,
                "type":      work_type,
                "container": container,
                "doi":       doi,
                "url":       url,
                "path":      path,
            })
    return works

def format_works_with_contributors(orcid_id: str, limit: int = 10) -> List[Dict]:
    """
    Busca detalhes completos de até `limit` obras com coautores via /work/{put-code}.
    """
    works: List[Dict] = []
    summary_data = fetch_orcid(orcid_id, section="works") or {}
    count = 0

    for group in summary_data.get("group", []) or []:
        for summary in group.get("work-summary", []) or []:
            if count >= limit:
                return works
            put_code = summary.get("put-code")
            if not put_code:
                continue

            try:
                detail = fetch_orcid(orcid_id, section=f"work/{put_code}")
            except HTTPException:
                continue

            title = html.unescape(
                (detail.get("title") or {}).get("title", {}).get("value", "Sem título")
            )
            year = (detail.get("publication-date") or {}).get("year", {}).get("value", "----")
            work_type = detail.get("type") or "desconhecido"
            container = (detail.get("journal-title") or {}).get("value")

            doi = None
            for ext in (detail.get("external-ids") or {}).get("external-id", []):
                if ext.get("external-id-type", "").lower() == "doi":
                    doi = ext.get("external-id-value")
                    break

            url = (detail.get("url") or {}).get("value")
            path = detail.get("path")

            contributors = []
            for contrib in (detail.get("contributors") or {}).get("contributor", []):
                credit = contrib.get("credit-name")
                name = credit.get("value") if isinstance(credit, dict) else None
                orcid = (contrib.get("contributor-orcid") or {}).get("path")
                if name:
                    contributors.append({"name": name, "orcid": orcid})

            works.append({
                "title":      title,
                "year":       year,
                "type":       work_type,
                "container":  container,
                "doi":        doi,
                "url":        url,
                "path":       path,
                "coauthors":  contributors
            })

            count += 1

    return works