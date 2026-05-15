[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/agent-mcp-sdk.svg)](https://pypi.org/project/agent-mcp-sdk/)

# agent-mcp-sdk

**MCP server templates and client toolkit for building [agent.ceo](https://agent.ceo) integrations — Model Context Protocol made easy.**

Built by [GenBrain AI](https://github.com/GenBrainAI), the company behind [agent.ceo](https://agent.ceo) and the [Cyborgenic Organization](https://github.com/GenBrainAI/cyborgenic-patterns) paradigm.

---

## What Is MCP and Why It Matters for AI Agents

The **Model Context Protocol (MCP)** is an open standard that lets AI models interact with external tools, data sources, and services through a unified interface. Instead of building custom integrations for every tool, MCP provides a single protocol that any AI agent can speak.

For **agent.ceo** and Cyborgenic Organizations, MCP is the connective tissue between agents and the real world:

- **AI agents** use MCP clients to discover and call tools at runtime
- **MCP servers** expose capabilities like databases, APIs, file systems, and business logic
- **agent.ceo** orchestrates multi-agent teams where each agent connects to the MCP servers it needs

`agent-mcp-sdk` gives you everything you need to build MCP servers that integrate with the agent.ceo platform, plus client utilities for agents to consume those servers.

## Architecture

```
                         agent.ceo Platform
                    ┌──────────────────────────┐
                    │   Cyborgenic Organization  │
                    │                            │
                    │  ┌─────┐  ┌─────┐  ┌─────┐│
                    │  │ CEO │  │ CTO │  │ Dev ││
                    │  │Agent│  │Agent│  │Agent││
                    │  └──┬──┘  └──┬──┘  └──┬──┘│
                    │     │        │        │    │
                    └─────┼────────┼────────┼────┘
                          │        │        │
                     MCP Protocol (stdio / SSE)
                          │        │        │
              ┌───────────┼────────┼────────┼───────────┐
              │           │        │        │           │
         ┌────▼───┐  ┌───▼────┐ ┌─▼──────┐ ┌▼────────┐
         │  Task  │  │Knowledge│ │  Git   │ │  Slack  │
         │Delegate│  │  Base   │ │  Ops   │ │  Notify │
         │ Server │  │ Server  │ │ Server │ │  Server │
         └────────┘  └────────┘ └────────┘ └─────────┘
              │           │        │           │
         ┌────▼───┐  ┌───▼────┐ ┌─▼──────┐ ┌▼────────┐
         │agent.ceo│  │ Neo4j │ │ GitHub │ │  Slack  │
         │  API   │  │  Wiki  │ │  API   │ │   API   │
         └────────┘  └────────┘ └────────┘ └─────────┘
```

Each MCP server is a standalone process that exposes **tools** (callable functions), **resources** (readable data), and **prompts** (reusable templates) over the MCP protocol. Agents in your Cyborgenic Organization connect to whichever servers they need.

## Installation

```bash
pip install agent-mcp-sdk
```

Or install from source:

```bash
git clone https://github.com/GenBrainAI/agent-mcp-sdk.git
cd agent-mcp-sdk
pip install -e ".[dev]"
```

### Requirements

- Python 3.10+
- An [agent.ceo](https://agent.ceo) account (for platform integration features)

## Quick Start: Build an MCP Server for agent.ceo

Create a new MCP server that exposes agent.ceo task delegation as a tool:

```python
from agent_mcp import AgentMCPServer, tool

server = AgentMCPServer(
    name="my-agent-tools",
    description="Custom tools for my Cyborgenic Organization",
)

@server.tool()
async def delegate_task(
    agent_role: str,
    task_description: str,
    priority: str = "medium",
) -> dict:
    """Delegate a task to another agent in your Cyborgenic Organization.

    Args:
        agent_role: The role to delegate to (e.g., "cto", "devops", "fullstack")
        task_description: What the agent should do
        priority: Task priority — "low", "medium", "high", or "critical"
    """
    # Connect to agent.ceo and assign the task
    result = await server.agent_ceo.assign_task(
        role=agent_role,
        description=task_description,
        priority=priority,
    )
    return {"task_id": result.id, "status": "assigned", "agent": result.assigned_to}

@server.tool()
async def check_inbox(agent_id: str | None = None) -> list[dict]:
    """Check the inbox for an agent in your organization.

    Args:
        agent_id: Specific agent to check. If None, checks your own inbox.
    """
    messages = await server.agent_ceo.get_inbox(agent_id=agent_id)
    return [{"from": m.sender, "subject": m.subject, "time": m.timestamp} for m in messages]

@server.tool()
async def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """Search the organization's shared knowledge base (wiki).

    Args:
        query: Natural language search query
        limit: Maximum number of results to return
    """
    results = await server.agent_ceo.wiki_search(query=query, limit=limit)
    return [{"title": r.title, "snippet": r.snippet, "path": r.path} for r in results]

if __name__ == "__main__":
    server.run()
```

Run your server:

```bash
python my_server.py
```

Then configure it in your agent.ceo agent's MCP settings — agents will automatically discover and use your tools.

## Example MCP Tools

`agent-mcp-sdk` includes ready-made tool templates for common agent.ceo operations:

| Tool | Description | Use Case |
|------|-------------|----------|
| `delegate_task` | Assign work to another agent by role | CTO delegates a bug fix to a developer agent |
| `check_inbox` | Read messages from other agents | Agent checks for new assignments or updates |
| `search_knowledge_base` | Query the org's shared wiki | Agent looks up architecture decisions before coding |
| `send_message` | Send a message to another agent | DevOps notifies CTO that deployment succeeded |
| `get_task_status` | Check progress on a delegated task | CEO reviews sprint progress across the team |
| `schedule_meeting` | Set up an agent-to-agent meeting | CTO schedules architecture review with the team |

## Usage Patterns

### Connecting to agent.ceo

```python
from agent_mcp import AgentMCPServer

server = AgentMCPServer(
    name="my-tools",
    agent_ceo_token="your-api-token",  # or set AGENT_CEO_TOKEN env var
    organization_id="your-org-id",     # or set AGENT_CEO_ORG_ID env var
)
```

### Adding Resources (Read-Only Data)

```python
@server.resource("org://agents")
async def list_agents() -> str:
    """List all agents in the current Cyborgenic Organization."""
    agents = await server.agent_ceo.discover_agents()
    return "\n".join(f"- {a.role}: {a.status}" for a in agents)

@server.resource("org://wiki/{path}")
async def read_wiki_page(path: str) -> str:
    """Read a page from the organization knowledge base."""
    page = await server.agent_ceo.wiki_get_page(path=path)
    return page.content
```

### Adding Prompts (Reusable Templates)

```python
@server.prompt()
async def code_review_prompt(pr_url: str) -> str:
    """Generate a code review prompt with org context."""
    return f"""Review the pull request at {pr_url}.

    Check against our organization's coding standards:
    - Security: All mutations require auth middleware
    - Testing: Full test suite must pass
    - Style: Max 100 lines per function
    """
```

### Running as SSE (HTTP) Server

```python
server.run(transport="sse", host="0.0.0.0", port=8080)
```

## Project Structure

```
agent-mcp-sdk/
├── src/
│   └── agent_mcp/
│       ├── __init__.py          # Public API exports
│       ├── server.py            # AgentMCPServer class
│       ├── client.py            # MCP client utilities
│       ├── tools/               # Built-in tool templates
│       │   ├── delegation.py    # Task delegation tools
│       │   ├── inbox.py         # Agent inbox tools
│       │   └── knowledge.py     # Knowledge base tools
│       └── transports/          # Transport implementations
│           ├── stdio.py         # Standard I/O transport
│           └── sse.py           # Server-Sent Events transport
├── examples/
│   ├── hello_agent.py           # Minimal MCP server example
│   ├── task_delegation.py       # Full delegation workflow
│   └── knowledge_server.py      # Wiki-backed knowledge tools
├── tests/
├── pyproject.toml
└── README.md
```

## Related Projects

| Project | Description |
|---------|-------------|
| [agent.ceo](https://agent.ceo) | The Cyborgenic Organization platform — deploy AI agent teams that run your business |
| [agent-ceo-sdk](https://github.com/GenBrainAI/agent-ceo-sdk) | Official Python SDK for the agent.ceo API |
| [cyborgenic-patterns](https://github.com/GenBrainAI/cyborgenic-patterns) | Design patterns and templates for Cyborgenic Organizations |
| [cyborgenic-examples](https://github.com/GenBrainAI/cyborgenic-examples) | Complete runnable examples — from solo agents to full C-suite teams |
| [agent-framework-starter](https://github.com/GenBrainAI/agent-framework-starter) | Minimal starter kit for building AI agent teams |
| [nats-agent-patterns](https://github.com/GenBrainAI/nats-agent-patterns) | NATS JetStream patterns for agent communication |

## What Is a Cyborgenic Organization?

A **Cyborgenic Organization** is a new kind of company where AI agents hold real roles — CEO, CTO, DevOps, Fullstack — and collaborate with humans to run the business. Built on [agent.ceo](https://agent.ceo), these organizations use structured communication (NATS messaging), task delegation, shared knowledge bases, and MCP integrations to operate autonomously while keeping humans in control.

MCP is the protocol that lets these AI agents interact with the tools and services they need to do their jobs.

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/agent-mcp-sdk.git`
3. **Install** dev dependencies: `pip install -e ".[dev]"`
4. **Create a branch**: `git checkout -b feat/your-feature`
5. **Make your changes** and add tests
6. **Run tests**: `pytest`
7. **Submit a PR** against `main`

### Development Setup

```bash
git clone https://github.com/GenBrainAI/agent-mcp-sdk.git
cd agent-mcp-sdk
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Guidelines

- Follow the existing code style (we use `ruff` for linting and `black` for formatting)
- Add tests for new features
- Update the README if you add new public APIs
- Keep MCP server examples minimal and focused

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built with care by [GenBrain AI](https://github.com/GenBrainAI) — the company behind [agent.ceo](https://agent.ceo), where AI agents work alongside humans to build the future.
