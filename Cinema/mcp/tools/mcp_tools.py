"""Cinema MCP tools — each function maps to one Cinema API operation."""

from mcp.server.fastmcp import FastMCP
import client


def register(mcp: FastMCP) -> None:
    """Attach all tools to the MCP server instance."""

    @mcp.tool()
    def list_screenings(
        genre: str | None = None,
        date: str | None = None,
        hall: str | None = None,
    ) -> list[dict]:
        """Return all screenings, optionally filtered by genre, date (YYYY-MM-DD), or hall."""
        return client.list_screenings(genre=genre, date=date, hall=hall)

    @mcp.tool()
    def get_screening(screening_id: int) -> dict:
        """Return a single screening by its ID."""
        return client.get_screening(screening_id)

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
        return client.create_screening({
            "name": name,
            "genre": genre,
            "duration_minutes": duration_minutes,
            "screening_date": screening_date,
            "begins_at": begins_at,
            "hall": hall,
            "seats": seats,
        })

    @mcp.tool()
    def replace_screening(screening_id: int, name: str, genre: str, duration_minutes: int,
                          screening_date: str, begins_at: str, hall: str, seats: int) -> dict:
        """Fully replace an existing screening (PUT)."""
        return client.replace_screening(screening_id, {
            "name": name,
            "genre": genre,
            "duration_minutes": duration_minutes,
            "screening_date": screening_date,
            "begins_at": begins_at,
            "hall": hall,
            "seats": seats,
        })

    @mcp.tool()
    def patch_screening(
        screening_id: int,
        name: str | None = None,
        genre: str | None = None,
        duration_minutes: int | None = None,
        screening_date: str | None = None,
        begins_at: str | None = None,
        hall: str | None = None,
        seats: int | None = None,
    ) -> dict:
        """Partially update a screening (PATCH). Only provided fields are changed."""
        fields = {
            k: v for k, v in {
                "name": name,
                "genre": genre,
                "duration_minutes": duration_minutes,
                "screening_date": screening_date,
                "begins_at": begins_at,
                "hall": hall,
                "seats": seats,
            }.items() if v is not None
        }
        return client.patch_screening(screening_id, fields)

    @mcp.tool()
    def delete_screening(screening_id: int) -> str:
        """Delete a screening by ID. Returns a confirmation message."""
        client.delete_screening(screening_id)
        return f"Screening {screening_id} deleted."
