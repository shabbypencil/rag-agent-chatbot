from tavily import TavilyClient
from backend.core.config import TAVILY_API_KEY, TAVILY_MAX_RESULTS


def get_tavily_client() -> TavilyClient:
    if not TAVILY_API_KEY:
        raise RuntimeError("No Tavily API key set. Set TAVILY_API_KEY.")
    return TavilyClient(api_key=TAVILY_API_KEY)


def search_web_tavily(query: str, max_results: int = TAVILY_MAX_RESULTS) -> list[dict]:
    client = get_tavily_client()

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_answer=False,
        include_raw_content=True,
    )

    results = []
    for i, item in enumerate(response.get("results", []), start=1):
        snippet = item.get("content", "") or ""
        full_text = item.get("raw_content") or snippet

        results.append({
            "source_id": f"web_{i}",
            "title": item.get("title", "Untitled"),
            "snippet": snippet[:300],
            "full_text": full_text[:4000],
            "url": item.get("url", ""),
            "distance": None,
            "source_type": "web",
        })

    return results

# Filtering step: Check if the results have a URL and full_text, and filter out any that don't
def filter_web_results(results: list[dict]) -> list[dict]:
    filtered = []
    for item in results:
        if not item.get("url"):
            continue
        if not item.get("full_text"):
            continue
        filtered.append(item)
    return filtered