"""Plain Python plumbing for the arXiv API. No LLM in here: just HTTP and XML.

Every successful response is cached in .cache/, and the cache is used when the
network is down, so a query you have run before still works offline.
"""
import hashlib
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

try:  # under the MCP server, a ToolError's message is shown to the model
    from mcp.server.mcpserver.exceptions import ToolError as _Base
except ImportError:  # used on its own (mini_agent.py), a plain exception will do
    _Base = Exception


class ArxivError(_Base):
    """A failure worth explaining to whoever called us."""


API = "https://export.arxiv.org/api/query?"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
CACHE = pathlib.Path(__file__).parent / ".cache"


def _get(params: dict) -> list[dict]:
    url = API + urllib.parse.urlencode(params)
    cached = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "workshop-demo"})
        with urllib.request.urlopen(request, timeout=15) as response:
            papers = [_paper(entry) for entry in ET.fromstring(response.read()).findall("a:entry", ATOM)]
        CACHE.mkdir(exist_ok=True)
        cached.write_text(json.dumps(papers))
        return papers
    except urllib.error.HTTPError as error:  # arXiv answered, and said no
        raise ArxivError(f"arXiv rejected the request (HTTP {error.code}). Use plain keywords in the query.")
    except OSError as error:  # no answer at all: fall back to the cache
        if cached.exists():
            return json.loads(cached.read_text())
        raise ArxivError(f"arXiv is unreachable and this query is not cached ({error})")


def _paper(entry: ET.Element) -> dict:
    def text(tag: str) -> str:
        return " ".join((entry.findtext(tag, "", ATOM)).split())

    return {
        "id": re.sub(r"v\d+$", "", text("a:id").rsplit("/abs/", 1)[-1]),
        "title": text("a:title"),
        "authors": [" ".join(name.text.split()) for name in entry.findall("a:author/a:name", ATOM)],
        "published": text("a:published")[:10],
        "abstract": text("a:summary"),
    }


def search(query: str, max_results: int = 5, newest_first: bool = False) -> list[dict]:
    """Search all fields. Returns short records, without abstracts."""
    papers = _get({
        "search_query": " AND ".join(f"all:{word}" for word in query.split()),
        "max_results": max(1, min(max_results, 20)),
        "sortBy": "submittedDate" if newest_first else "relevance",
        "sortOrder": "descending",
    })
    for paper in papers:
        del paper["abstract"]
        if len(paper["authors"]) > 3:
            paper["authors"] = paper["authors"][:3] + ["et al."]
    return papers


def fetch(arxiv_id: str) -> dict:
    """One paper, with its abstract."""
    papers = _get({"id_list": arxiv_id.strip().removeprefix("arXiv:")})
    if not papers or not papers[0]["title"]:
        raise ArxivError(f"No arXiv paper with id {arxiv_id!r}")
    return papers[0] | {"url": f"https://arxiv.org/abs/{papers[0]['id']}"}


if __name__ == "__main__":  # quick manual check: python3 arxiv_api.py topological insulators
    import sys

    for paper in search(" ".join(sys.argv[1:]) or "topological insulators", newest_first=True):
        print(paper["id"], paper["published"], paper["title"][:70])
