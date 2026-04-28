"""Cinema MCP prompts — reusable AI command templates."""

from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage


def register(mcp: FastMCP) -> None:
    """Attach all prompts to the MCP server instance."""

    @mcp.prompt()
    def find_movie(genre: str, date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to recommend screenings for a genre and date."""
        # TODO: implement — build and return PromptMessage list
        raise NotImplementedError

    @mcp.prompt()
    def summarise_schedule(date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to summarise all screenings on a given date."""
        # TODO: implement
        raise NotImplementedError

    @mcp.prompt()
    def hall_availability(hall: str, date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to report seat availability for a hall on a date."""
        # TODO: implement
        raise NotImplementedError