import json
from datetime import date

from mcp.server.fastmcp import FastMCP

import client


def _fmt(data) -> str:
    return json.dumps(data, indent=2)


def register(mcp: FastMCP) -> None:
    """Attach all resources to the MCP server instance."""

    @mcp.resource("cinema://screenings")
    def screenings_list() -> str:
        """All screenings as a structured text block for LLM context."""
        return _fmt(client.list_screenings())

    @mcp.resource("cinema://screenings/{screening_id}")
    def screening_detail(screening_id: str) -> str:
        """A single screening record addressed by ID."""
        return _fmt(client.get_screening(int(screening_id)))

    @mcp.resource("cinema://genres")
    def genres_list() -> str:
        """Distinct genre values present in the current screenings catalogue."""
        screenings = client.list_screenings()
        genres = sorted({s["genre"] for s in screenings if s.get("genre")})
        return _fmt(genres)

    @mcp.resource("cinema://halls")
    def halls_list() -> str:
        """Distinct hall identifiers present in the current screenings catalogue."""
        screenings = client.list_screenings()
        halls = sorted({s["hall"] for s in screenings if s.get("hall")})
        return _fmt(halls)

    @mcp.resource("cinema://todays_screenings")
    def todays_screenings() -> str:
        """All screenings scheduled for today."""
        today = date.today().isoformat()
        return _fmt(client.list_screenings(date=today))
