"""hello_agent.py — Minimal MCP server example for agent.ceo.

This example creates a simple MCP server with one tool that greets
an agent by name. It demonstrates the basic pattern for building
MCP servers with agent-mcp-sdk.

Run:
    python hello_agent.py

Then configure this server in your agent.ceo agent's MCP settings
to make the tool available to your Cyborgenic Organization.
"""

from agent_mcp import AgentMCPServer

# Create a new MCP server
server = AgentMCPServer(
    name="hello-agent",
    description="A minimal MCP server example for agent.ceo",
)


@server.tool()
async def greet_agent(agent_name: str, role: str = "agent") -> dict:
    """Greet an agent in your Cyborgenic Organization.

    Args:
        agent_name: The name of the agent to greet.
        role: The agent's role (e.g., "cto", "devops", "fullstack").

    Returns:
        A greeting message with the agent's name and role.
    """
    return {
        "message": f"Hello, {agent_name}! Welcome to the team as our {role}.",
        "status": "greeted",
    }


@server.tool()
async def get_org_info() -> dict:
    """Get basic information about the Cyborgenic Organization.

    Returns:
        Organization metadata including name and active agent count.
    """
    return {
        "platform": "agent.ceo",
        "org_type": "Cyborgenic Organization",
        "description": "AI agents and humans working together",
        "docs": "https://agent.ceo/docs",
    }


if __name__ == "__main__":
    print("Starting hello-agent MCP server...")
    print("This server exposes tools for agent.ceo integration.")
    print("See https://agent.ceo for more information.")
    server.run()
