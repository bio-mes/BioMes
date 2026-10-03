# search_tools.py

from typing import Any, Dict, List, Optional
from asyncio import to_thread
import time
import requests

from langchain_core.tools import tool
from langchain_tavily import TavilySearch



class TavilySearchEngine:
    def __init__(self, api_key: str) -> None:
        self.tavily_tool = TavilySearch(
            tavily_api_key=api_key,
            max_results=5,
            topic="general",
            include_answer=True,
        )

    def run(self, query: str) -> Any:

        return self.tavily_tool.invoke(query)


class JinaSearchEngine:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def run(self, query: str) -> Dict[str, Any]:
        chance = 3
        current_try = 0
        last_error: Optional[Exception] = None

        url = "https://deepsearch.jina.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        while current_try < chance:
            try:
                data = {
                    "model": "jina-deepsearch-v1",
                    "messages": [
                        {"role": "user", "content": "Hi!"},
                        {"role": "assistant", "content": "Hi, how can I help you?"},
                        {"role": "user", "content": query},
                    ],
                    "stream": False,
                    "reasoning_effort": "low",
                    "max_attempts": 1,
                    "no_direct_answer": False,
                }

                response = requests.post(
                    url, headers=headers, json=data, timeout=(30, 300)
                )
                if response.status_code != 200:
                    raise ValueError(f"API response error: {response.status_code}")

                result_json = response.json()
                if result_json is None:
                    raise ValueError("Failed to get deep search results")

                choice0 = result_json["choices"][0]
                delta_content = choice0.get("delta") or choice0.get("message", {})
                search_result: str = delta_content.get("content", "")
                annotations = delta_content.get("annotations", [])

                citations: List[Dict[str, Any]] = []
                for i, item in enumerate(annotations):
                    try:
                        url_cit = item["url_citation"]
                        text = url_cit.get("exactQuote", "")
                        citations.append(
                            {
                                "index": i + 1,
                                "link": url_cit.get("url", ""),
                                "title": url_cit.get("title", ""),
                                "snippet": text,
                                "content": text,
                                "full_content": text,
                            }
                        )
                    except Exception:
                        continue

                return {
                    "answer": search_result,
                    "citations": citations,
                }

            except Exception as e:
                last_error = e
                current_try += 1
                time.sleep(60)

        raise RuntimeError(f"Jina search failed after {chance} attempts: {last_error}")



_tavily_engine: Optional[TavilySearchEngine] = None
_jina_engine: Optional[JinaSearchEngine] = None


def initialize_search_engines(config: Dict[str, Any]) -> None:

    global _tavily_engine, _jina_engine

    tavily_key = config.get("tavily_api_key")
    if tavily_key:
        _tavily_engine = TavilySearchEngine(tavily_key)
    else:
        _tavily_engine = None

    jina_key = config.get("jina_api_key")
    if jina_key:
        _jina_engine = JinaSearchEngine(jina_key)
    else:
        _jina_engine = None


def get_tavily_engine() -> Optional[TavilySearchEngine]:
    return _tavily_engine


def get_jina_engine() -> Optional[JinaSearchEngine]:
    return _jina_engine



@tool(parse_docstring=True)
async def tavily_search(query: str) -> Any:
    """
    Run the Tavily search engine with a given query.

    Args:
        query: Natural language search query.

    Returns:
        TavilySearch result dict, typically containing:
        - "answer": synthesized answer
        - "results": list of retrieved documents with titles, URLs, snippets, etc.
    """
    engine = get_tavily_engine()
    if engine is None:
        return {"error": "Tavily API key is not configured."}

    try:
        results = await to_thread(engine.run, query)
        return results
    except Exception as e:
        return {
            "error": f"Tool tavily_search execution failed for query: {query}, error: {str(e)}"
        }


@tool(parse_docstring=True)
async def jina_search(query: str) -> Any:
    """
    Run the Jina DeepSearch engine with a given query.

    Args:
        query: Natural language search query.

    Returns:
        A dictionary with:
        - "answer": the synthesized answer text
        - "citations": list of citation objects with fields
          index, link, title, snippet, content, full_content
    """
    engine = get_jina_engine()
    if engine is None:
        return {"error": "Jina API key is not configured."}

    try:
        results = await to_thread(engine.run, query)
        return results
    except Exception as e:
        return {
            "error": f"Tool jina_search execution failed for query: {query}, error: {str(e)}"
        }



search_tools = {
    "tavily_search": tavily_search,
    "jina_search": jina_search,
}
