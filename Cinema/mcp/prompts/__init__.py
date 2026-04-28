"""Cinema MCP prompts — reusable AI command templates."""

from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent


def register(mcp: FastMCP) -> None:
    """Attach all prompts to the MCP server instance."""

    @mcp.prompt()
    def find_movie(genre: str, date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to recommend screenings for a genre and date."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Use the list_screenings tool to fetch all {genre} screenings on {date}. "
                        "Then recommend the best options, highlighting the movie title, start time, "
                        "hall, and number of available seats for each. "
                        "If no screenings are found, say so clearly."
                    ),
                ),
            )
        ]

    @mcp.prompt()
    def summarise_schedule(date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to summarise all screenings on a given date."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Use the list_screenings tool to fetch all screenings on {date}. "
                        "Provide a concise summary: list each screening with its title, genre, "
                        "hall, start time, duration, and seat count. "
                        "Group by hall and sort by start time within each group. "
                        "End with the total number of screenings for the day."
                    ),
                ),
            )
        ]

    @mcp.prompt()
    def hall_availability(hall: str, date: str) -> list[PromptMessage]:
        """Generate a prompt that asks the AI to report seat availability for a hall on a date."""
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Use the list_screenings tool with hall='{hall}' and date='{date}' "
                        f"to fetch all screenings in hall {hall} on {date}. "
                        "Report each screening's title, start time, and seat count. "
                        "Calculate and show the total seats available across all screenings in that hall. "
                        "If the hall has no screenings on that date, say so clearly."
                    ),
                ),
            )
        ]
