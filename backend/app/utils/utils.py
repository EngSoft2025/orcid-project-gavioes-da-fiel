# app/utils/utils.py

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import logging
from fastapi import Response, HTTPException
from xml.dom.minidom import parseString

# Regex para normalização
_DOI_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/|^doi:\s*", re.I)
_ORCID_URL_RE = re.compile(r"^https?://orcid\.org/", re.I)


# Normalização de IDs
def normalize_doi(doi: Optional[str]) -> str:
    """
    Remove prefixos de URL ou 'doi:' e retorna o DOI em minúsculas.
    Exemplo: "https://doi.org/10.1000/xyz" -> "10.1000/xyz"
    """
    return _DOI_RE.sub("", (doi or "").strip()).lower()


def normalize_orcid(orcid: str) -> str:
    """
    Remove eventual URL e espaços de um ORCID, mantendo apenas o formato numérico com hífens.
    Exemplo: "https://orcid.org/0000-0002-1234-5678" -> "0000-0002-1234-5678"
    """
    return _ORCID_URL_RE.sub("", orcid.strip())


# Filtros sobre listas de obras
def filter_by_year(works: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
    """
    Retorna apenas as obras cujo campo 'year' bate com o ano especificado.
    """
    resultado: List[Dict[str, Any]] = []
    for w in works:
        ano_obra = w.get("year")
        if isinstance(ano_obra, int) and ano_obra == year:
            resultado.append(w)
        elif isinstance(ano_obra, str) and ano_obra.isdigit() and int(ano_obra) == year:
            resultado.append(w)
    return resultado


def filter_by_keyword(works: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
    Retorna apenas as obras que contêm 'keyword' (case-insensitive)
    no título, abstract/short_description ou na lista de keywords.
    """
    sk = keyword.lower()
    filtrado: List[Dict[str, Any]] = []

    for w in works:
        match = False

        # Verifica título
        title = w.get("title", "")
        if isinstance(title, str) and sk in title.lower():
            match = True

        # Verifica abstract/short_description
        if not match:
            abstract = w.get("short_description") or w.get("abstract") or ""
            if isinstance(abstract, str) and sk in abstract.lower():
                match = True

        # Verifica lista de palavras‐chave
        if not match:
            for kw_item in w.get("keywords", []):
                txt: Optional[str] = None
                if isinstance(kw_item, str):
                    txt = kw_item
                elif isinstance(kw_item, dict):
                    txt = kw_item.get("content")
                if isinstance(txt, str) and sk in txt.lower():
                    match = True
                    break

        if match:
            filtrado.append(w)

    return filtrado


# Conversão de dicionário para XML
def dict_to_xml(data: Any, root: ET.Element):
    """
    Converte recursivamente um dicionário ou lista para elementos XML.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            safe_key = re.sub(r'[^a-zA-Z0-9_.-]', '_', key)
            child = ET.SubElement(root, safe_key)
            dict_to_xml(value, child)

    elif isinstance(data, list):
        singular_tag = root.tag.rstrip('s')
        if singular_tag == root.tag:
            singular_tag = 'item'
        for item in data:
            child = ET.SubElement(root, singular_tag)
            dict_to_xml(item, child)

    else:
        if data is not None:
            root.text = str(data)


def build_pretty_xml(data: Any, root_tag: str, attrib: Dict[str, str]) -> bytes:
    """
    Constrói um XML indentado a partir de um dict,
    usando como elemento raiz `root_tag` e atributos em `attrib`.
    Retorna bytes UTF-8 com o XML formatado.
    """
    root = ET.Element(root_tag, attrib=attrib)
    dict_to_xml(data, root)
    rough = ET.tostring(root, 'utf-8')
    reparsed = parseString(rough)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")


def xml_response(data: Any, orcid_id: str) -> Response:
    """
    Gera um Response FastAPI com download de XML para os dados fornecidos.
    Lança 404 se `data` vazio, 500 em erro interno.
    """
    if not data:
        raise HTTPException(status_code=404, detail="ORCID não encontrado")
    try:
        xml_bytes = build_pretty_xml(data, 'researcher', {'orcid': orcid_id})
        return Response(
            content=xml_bytes,
            media_type='application/xml',
            headers={'Content-Disposition': f'attachment; filename="{orcid_id}.xml"'}
        )
    except Exception as e:
        logging.exception(f"Erro ao gerar XML para {orcid_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Falha ao gerar XML: {e}")

