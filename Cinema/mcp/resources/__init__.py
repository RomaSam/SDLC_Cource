"""Cinema MCP resources — structured, URI-addressable data for LLM context."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Attach all resources to the MCP server instance."""

    @mcp.resource("cinema://screenings")
    def screenings_list() -> str:
        """All screenings as a structured text block for LLM context."""
        # TODO: implement — call client.list_screenings() and format as text/JSON
        raise NotImplementedError

    @mcp.resource("cinema://screenings/{screening_id}")
    def screening_detail(screening_id: str) -> str:
        """A single screening record addressed by ID."""
        # TODO: implement — call client.get_screening(int(screening_id))
        raise NotImplementedError

    @mcp.resource("cinema://genres")
    def genres_list() -> str:
        """Distinct genre values present in the current screenings catalogue."""
        # TODO: implement — derive from client.list_screenings()
        raise NotImplementedError

    @mcp.resource("cinema://halls")
    def halls_list() -> str:
        """Distinct hall identifiers present in the current screenings catalogue."""
        # TODO: implement — derive from client.list_screenings()
        raise NotImplementedError
