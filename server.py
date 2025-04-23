from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from dataclasses import dataclass
from dotenv import load_dotenv
import httpx
import asyncio
import os
import typing

load_dotenv()

@dataclass
class SearXNGContext:
    client: httpx.AsyncClient
    base_url: str

@asynccontextmanager
async def searxng_lifespan(server: FastMCP):
    base_url = os.getenv("SEARXNG_BASE_URL", "http://172.17.0.1:32768")
    client = httpx.AsyncClient(base_url=base_url)
    try:
        yield SearXNGContext(client=client, base_url=base_url)
    finally:
        await client.aclose()

mcp = FastMCP(
    "mcp-searxng",
    description="MCP server to search the web using SearXNG instance",
    lifespan=searxng_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "32769"))
)

@mcp.tool()
async def search(
    ctx: Context,
    q: str,
    categories: typing.Optional[str] = None,
    engines: typing.Optional[str] = None,
    language: typing.Optional[str] = None,
    page: int = 1,
    time_range: typing.Optional[str] = None,
    format: str = "json",
    results_on_new_tab: typing.Optional[int] = None,
    image_proxy: typing.Optional[bool] = None,
    autocomplete: typing.Optional[str] = None,
    safesearch: typing.Optional[int] = None,
    theme: typing.Optional[str] = None,
    enabled_plugins: typing.Optional[str] = None,
    disabled_plugins: typing.Optional[str] = None,
    enabled_engines: typing.Optional[str] = None,
    disabled_engines: typing.Optional[str] = None,
) -> str:
    """
    Perform a search using SearXNG with all supported parameters.
    """
    params = {"q": q, "page": page, "format": format}
    if categories is not None:
        params["categories"] = categories
    if engines is not None:
        params["engines"] = engines
    if language is not None:
        params["language"] = language
    if time_range is not None:
        params["time_range"] = time_range
    if results_on_new_tab is not None:
        params["results_on_new_tab"] = results_on_new_tab
    if image_proxy is not None:
        params["image_proxy"] = str(image_proxy).lower()
    if autocomplete is not None:
        params["autocomplete"] = autocomplete
    if safesearch is not None:
        params["safesearch"] = safesearch
    if theme is not None:
        params["theme"] = theme
    if enabled_plugins is not None:
        params["enabled_plugins"] = enabled_plugins
    if disabled_plugins is not None:
        params["disabled_plugins"] = disabled_plugins
    if enabled_engines is not None:
        params["enabled_engines"] = enabled_engines
    if disabled_engines is not None:
        params["disabled_engines"] = disabled_engines

    searxng_ctx: SearXNGContext = ctx.request_context.lifespan_context
    try:
        resp = await searxng_ctx.client.get("/search", params=params, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Error querying SearXNG: {str(e)}"

async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == "sse":
        await mcp.run_sse_async()
    else:
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
