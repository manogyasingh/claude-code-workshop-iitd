# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2,<3"]
# ///
from mcp.server import MCPServer

import arxiv_api

mcp = MCPServer("arxiv")


@mcp.tool()
def search_papers(query: str, max_results: int = 5,
                  newest_first: bool = False) -> list[dict]:
    """Search arXiv by plain keywords. Returns id, title, authors and date."""
    return arxiv_api.search(query, max_results, newest_first)


@mcp.tool()
def get_abstract(arxiv_id: str) -> dict:
    """Fetch one paper's abstract and metadata by arXiv id, e.g. 2401.01234."""
    return arxiv_api.fetch(arxiv_id)


if __name__ == "__main__":
    mcp.run()  # stdio transport: Claude Code starts this file as a subprocess
