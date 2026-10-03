import re
import time
from typing import List, Dict, Any
from langchain_core.tools import tool
from Bio import Entrez

import os
import json
import asyncio
from urllib.parse import quote

import requests
GOOGLE_CSE_API_KEY = ""
GOOGLE_CSE_CX = ""

Entrez.email = ""
Entrez.tool = "MyTool"
Entrez.api_key = ""
Entrez.max_tries = 3
Entrez.sleep_between_tries = 2

PUBMED_SEMAPHORE = asyncio.Semaphore(8)


@tool(parse_docstring=True)
async def query_pubmed(query: str, max_papers: int = 5) -> str:
    """Query PubMed for papers based on the provided search query
    
    Args:
        query: PubMed search query
        max_papers: Maximum number of papers to retrieve
    
    Returns:
        JSON object of literature search results
    """
    # query = '("1900/01/01"[Date - Entry] : "2026/04/30"[Date - Entry]) AND' + query
    query = '("1900/01/01"[Date - Entry] : "2025/12/31"[Date - Entry]) AND' + query

    try:
        async with PUBMED_SEMAPHORE:
            papers = await asyncio.to_thread(_query_pubmed, query, max_papers)
    except Exception as e:
        papers = f"Error querying PubMed: {e}"

    if isinstance(papers, list):
        results = []
        for paper in papers:
            results.append({
                'content': {
                    'title': paper['title'],
                    'abstract': paper['abstract'],
                },
                'reference': {
                    'text': f'{paper["publication_date"]}. *{paper["journal"]}*. {paper["title"]}',
                    'link': f'https://pubmed.ncbi.nlm.nih.gov/{paper["pmid"]}/'
                }
            })
    else:
        results = papers  # Return error message

    return results

@tool(parse_docstring=True)
async def query_google_scholar(query: str, max_papers: int = 5) -> str:
    """Query Google Scholar via Google Custom Search JSON API.

    Args:
        query: Search query
        max_papers: Maximum number of papers to retrieve

    Returns:
        JSON object of literature search results
    """
    api_key = GOOGLE_CSE_API_KEY
    cx = GOOGLE_CSE_CX

    if not api_key or not cx:
        return (
            "Error querying Google Scholar: missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_CX. "
            "Set them as environment variables."
        )

    try:
        items = await asyncio.to_thread(_query_google_scholar_cse, query, max_papers, api_key, cx)
    except Exception as e:
        return f"Error querying Google Scholar: {e}"

    results = []
    for it in items:
        title = it.get("title") or ""
        snippet = it.get("snippet") or ""
        link = it.get("link") or ""

        results.append({
            "content": {
                "title": title,
                "abstract": snippet,  
            },
            "reference": {
                "text": f"*Google Scholar*. {title}",
                "link": link
            }
        })

    return results


def _query_google_scholar_cse(
    query: str,
    max_papers: int,
    api_key: str,
    cx: str
) -> List[Dict[str, Any]]:
    q = f"site:scholar.google.com {query}".strip()

    out: List[Dict[str, Any]] = []
    start = 1

    while len(out) < max_papers and start <= 91:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": q,
            "start": start,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        items = data.get("items") or []
        for it in items:
            out.append({
                "title": it.get("title"),
                "snippet": it.get("snippet"),
                "link": it.get("link"),
            })
            if len(out) >= max_papers:
                break

        if not items:
            break

        start += 10

    return out[:max_papers]


def _query_pubmed(query: str, max_papers: int = 5) -> List[Dict[str, Any]]:
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_papers)
    record = Entrez.read(handle)
    id_list = record["IdList"]
    handle.close()
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
    medline_data = handle.read()
    handle.close()

    papers = []
    records = re.findall(r'(PMID-.*?)(?=\n\n|\Z)', medline_data, re.DOTALL)
    for record in records:
        title_match = re.compile(r'\nTI\s*-\s*(.*?)(?=\n[A-Z]|\Z)', re.DOTALL).search(record)
        abstract_match = re.compile(r'\nAB\s*-\s*(.*?)(?=\n[A-Z]|\Z)', re.DOTALL).search(record)
        date_match = re.compile(r'\nEDAT\s*-\s*(.*?)(?=\n[A-Z]|\Z)', re.DOTALL).search(record)
        pmid_match = re.compile(r'PMID-\s*(\d+)').search(record)
        journal_match = re.compile(r'\nJT\s*-\s*(.*?)(?=\n[A-Z]|\Z)', re.DOTALL).search(record)

        title = re.sub(r'\s+', ' ', title_match.group(1)).strip() if title_match else None
        abstract = re.sub(r'\s+', ' ', abstract_match.group(1)).strip() if abstract_match else None
        publication_date = date_match.group(1).strip().split(' ')[0] if date_match else None
        pmid = pmid_match.group(1).strip() if pmid_match else None
        journal = re.sub(r'\s+', ' ', journal_match.group(1)).strip() if journal_match else None

        if abstract and abstract.endswith('.'):
            papers.append({
                'title': title,
                'abstract': abstract,
                'publication_date': publication_date,
                'pmid': pmid,
                'journal': journal,
            })

    return papers

@tool(parse_docstring=True)
async def query_biorxiv(query: str, max_papers: int = 5) -> str:
    """Query bioRxiv for papers based on the provided search query

    Args:
        query: bioRxiv search query (keywords)
        max_papers: Maximum number of papers to retrieve

    Returns:
        JSON object of literature search results
    """
    try:
        papers = await asyncio.to_thread(_query_biorxiv, query, max_papers)
    except Exception as e:
        return f"Error querying bioRxiv: {e}"

    results = []
    for p in papers:
        title = p.get("title") or ""
        abstract = p.get("abstract") or ""
        date = p.get("date") or ""
        server = p.get("server") or "biorxiv"
        doi = p.get("doi") or ""
        url = p.get("url") or (f"https://doi.org/{doi}" if doi else "")

        results.append({
            "content": {
                "title": title,
                "abstract": abstract,
            },
            "reference": {
                "text": f'{date}. *{server}*. {title}' if date else f'*{server}*. {title}',
                "link": url
            }
        })

    return results


def _query_biorxiv(query: str, max_papers: int = 5) -> List[Dict[str, Any]]:
    """
    bioRxiv API docs endpoint example:
    https://api.biorxiv.org/details/biorxiv/2020-01-01/2020-12-31/0
    Returns batches of papers; we filter by keyword locally.
    """

    start = "1900-01-01"
    end = "2100-01-01"
    cursor = 0
    batch_size = 100  

    q = (query or "").strip().lower()
    if not q:
        return []

    hits: List[Dict[str, Any]] = []

    for _ in range(10):
        url = f"https://api.biorxiv.org/details/biorxiv/{start}/{end}/{cursor}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()

        collection = data.get("collection") or []
        if not collection:
            break

        for item in collection:
            title = (item.get("title") or "").lower()
            abstract = (item.get("abstract") or "").lower()
            if q in title or q in abstract:
                hits.append({
                    "title": item.get("title"),
                    "abstract": item.get("abstract"),
                    "date": item.get("date"),
                    "server": item.get("server", "biorxiv"),
                    "doi": item.get("doi"),
                    "url": item.get("url") or (f"https://doi.org/{item.get('doi')}" if item.get("doi") else ""),
                })
                if len(hits) >= max_papers:
                    return hits

        cursor += batch_size

    return hits[:max_papers]


literature_tools = {
    "query_pubmed": query_pubmed,
    # "query_biorxiv": query_biorxiv,
    # "query_google_scholar": query_google_scholar,
}
