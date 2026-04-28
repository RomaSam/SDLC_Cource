"""Cinema MCP server entry point."""

import tools.mcp_tools as mcp_tools
import resources.mcp_resources as mcp_resources
import prompts.mcp_prompts as mcp_prompts

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Cinema")

mcp_tools.register(mcp)
mcp_resources.register(mcp)
mcp_prompts.register(mcp)


if __name__ == "__main__":
    mcp.run()
