from tavily import TavilyClient
import os
import requests
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(user_query: str):
    response = client.search(
        query=user_query,
        max_results=5
    )
    results = []

    for r in response.get("results", []):
        title = r.get("title", "No Title")
        snippet = (r.get("content") or r.get("snippet") or "No Snippet").strip()
        url = r.get("url", "No URL")
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(' ', 1)[0] + '...'
        result_info = {"title": title, "snippet": snippet, "url": url}
        results.append(result_info)
    return "\n\n".join([f"**{r['title']}**\n{r['snippet']}\n[{r['url']}]({r['url']})" for r in results])