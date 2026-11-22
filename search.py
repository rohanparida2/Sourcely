import os

from tavily import TavilyClient


class SearchError(Exception):
    """Raised when web search cannot be completed."""


def search_web(query: str) -> list[dict[str, str]]:
    """Search the web and return up to five concise source records."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise SearchError(
            "Tavily is not configured. Add TAVILY_API_KEY to your .env file."
        )

    try:
        response = TavilyClient(api_key=api_key).search(query, max_results=5)
    except Exception as error:
        raise SearchError(
            "Web search failed. Check your Tavily API key and internet connection."
        ) from error

    results = response.get("results", [])
    return [
        {
            "title": str(result.get("title", "Untitled source")),
            "url": str(result.get("url", "")),
            "content": str(result.get("content", "")),
        }
        for result in results
        if result.get("url")
    ]
