# Docker MCP Orchestrator

This project provides a simple Docker image that launches multiple MCP servers inside one container. The list of servers and their configuration is stored in a TOML file.

## Configuration

The container reads `/opt/mcps/mcp_config.toml` by default. You can override the path by setting the `MCP_CONFIG_FILE` environment variable.

Each entry in the file describes a repository to clone and the command to run. Environment variables required by the server can also be specified.

```toml
[[server]]
repo = "https://github.com/agency-ai-solutions/openai-codex-mcp.git"
command = "./setup_and_run.sh"

[[server]]
repo = "https://github.com/tavily-ai/tavily-mcp.git"
command = "npx -y tavily-mcp@0.2.1 serve"
# env = { TAVILY_API_KEY = "your-key" }
```

## Build

```bash
docker build -t mcp-archestrator .
```

## Run

```bash
docker run --rm -p 8000:8000 -p 8001:8001 mcp-archestrator
```
```powershell
docker build -t mcp-archestrator .; docker run --rm -p 8000:8000 -p 8001:8001 mcp-archestrator
```

Adjust the ports for your servers as needed. To supply a custom config file:

```bash
docker run --rm \
  -e MCP_CONFIG_FILE=/config.toml \
  -e TAVILY_API_KEY=your-key \
  -v $(pwd)/config.toml:/config.toml \
  mcp-archestrator
```

This allows you to easily add additional MCP servers with their required environment variables.