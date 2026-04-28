"""Cinema MCP server entry point."""

import tools
import resources
import prompts

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Cinema")

tools.register(mcp)
resources.register(mcp)
prompts.register(mcp)


if __name__ == "__main__":
    mcp.run()
