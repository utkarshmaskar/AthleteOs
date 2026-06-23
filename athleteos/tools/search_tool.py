from langchain_core.tools import tool
from tavily import TavilyClient

from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)


@tool
def search_fitness_info(query: str) -> str:
    """Search the web for fitness, nutrition, or recovery information."""
    if not TAVILY_API_KEY:
        return "Tavily API key is missing. Set TAVILY_API_KEY in .env."

    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results.get("results", []):
        title = r.get("title", "Untitled")
        content = r.get("content", "")[:250]
        output.append(f"{title}: {content}")
    return "\n\n".join(output) if output else "No results found."
