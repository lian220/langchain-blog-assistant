from langchain.tools import tool
from typing import Optional
import requests
from app.config import get_settings


@tool
def web_search(query: str) -> str:
    """Search the web for latest information about a given topic.

    This tool is useful for getting current trends, facts, and recent information
    that will help create well-researched blog content.

    Args:
        query: The search query to find information about

    Returns:
        A string containing the search results with relevant information
    """
    print(f">>> Executing Web Search for: {query}")

    # Try to use Tavily API if available
    settings = get_settings()
    tavily_api_key = settings.tavily_api_key

    if tavily_api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(query, max_results=3)

            results = []
            for result in response.get("results", []):
                results.append(f"- {result.get('title', '')}: {result.get('content', '')}")

            return "\n".join(results) if results else "No results found."
        except Exception as e:
            print(f"Tavily API error: {e}")
            return fallback_search(query)
    else:
        return fallback_search(query)


def fallback_search(query: str) -> str:
    """Fallback search when Tavily is not available."""
    # Simulate search results for demonstration
    fallback_results = f"""
    Search results for '{query}':

    - AI-Native Development is a new paradigm focusing on building applications with AI at their core.
    - It emphasizes designing software architecture that integrates AI capabilities from the ground up.
    - Key trends include using LLMs for code generation, AI-powered testing, and intelligent automation.
    - Major tech companies are shifting towards AI-first development practices in 2024-2025.
    - Tools like LangChain, AutoGPT, and GitHub Copilot are enabling this transformation.
    """

    return fallback_results
