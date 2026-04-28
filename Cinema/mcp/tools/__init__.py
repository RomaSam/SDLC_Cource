"""Cinema MCP tools — each function maps to one Cinema API operation."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Attach all tools to the MCP server instance."""

    @mcp.tool()
    def list_screenings(
        genre: str | None = None,
        date: str | None = None,
        hall: str | None = None,
    ) -> list[dict]:
        """Return all screenings, optionally filtered by genre, date (YYYY-MM-DD), or hall."""
        # TODO: implement
        raise NotImplementedError

    @mcp.tool()
    def get_screening(screening_id: int) -> dict:
        """Return a single screening by its ID."""
        # TODO: implement
        raise NotImplementedError

    @mcp.tool()
    def create_screening(
        name: str,
        genre: str,
        duration_minutes: int,
        screening_date: str,
        begins_at: str,
        hall: str,
        seats: int,
    ) -> dict:
        """Create a new screening. Returns the created record."""
        # TODO: implement
        raise NotImplementedError

    @mcp.tool()
    def replace_screening(screening_id: int, name: str, genre: str, duration_minutes: int,
                          screening_date: str, begins_at: str, hall: str, seats: int) -> dict:
        """Fully replace an existing screening (PUT)."""
        # TODO: implement
        raise NotImplementedError

    @mcp.tool()
    def patch_screening(screening_id: int, **fields) -> dict:
        """Partially update a screening (PATCH). Only provided fields are changed."""
        # TODO: implement
        raise NotImplementedError

    @mcp.tool()
    def delete_screening(screening_id: int) -> str:
        """Delete a screening by ID. Returns a confirmation message."""
        # TODO: implement
        raise NotImplementedError
