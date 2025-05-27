# Docker MCP Orchestrator

Docker MCP Orchestrator provides a lightweight way to run multiple **MCP servers** in a single container.  The orchestrator clones each server repository, installs any required dependencies and launches the commands described in a simple TOML configuration file.  Both HTTP servers and those that communicate over STDIO are supported.

## How it works

1. `start_servers.py` reads the configuration file located at `/opt/mcps/mcp_config.toml` (or the path defined by `MCP_CONFIG_FILE`).
2. Each server entry is cloned into `/opt/mcps/repos/<name>` if it is not already present.
3. If `requirements.txt` or `setup.py` is found in the repository, those dependencies are installed.
4. The configured command is started.  When `transport = "stdio"` the container's STDIN/STDOUT are piped to the process.
5. All subprocesses are terminated cleanly when the container receives `SIGTERM` or `SIGINT`.

## Configuration file

`mcp_config.toml` defines the list of servers.  An example is included in this repository:

```toml
[[server]]
repo = "https://github.com/agency-ai-solutions/openai-codex-mcp.git"
command = "./setup_and_run.sh"
env = { OPENAI_API_KEY = "your-openai-key" }
transport = "stdio"

[[server]]
repo = "https://github.com/tavily-ai/tavily-mcp.git"
command = "npx -y tavily-mcp@0.2.1 serve"
# env = { TAVILY_API_KEY = "your-key" }
# transport defaults to "http"
```

Field description:

- **repo** – Git repository to clone.
- **command** – Command executed to start the server.
- **env** – Optional environment variables passed to the process.
- **transport** – Either `"http"` (default) or `"stdio"`.

## Building the image

```bash
docker build -t mcp-orchestrator .
```

## Running

Expose the ports used by your servers and start the container:

```bash
docker run --rm -p 8000:8000 -p 8001:8001 mcp-orchestrator
```

On Windows PowerShell:

```powershell
docker build -t mcp-orchestrator .; docker run --rm -p 8000:8000 -p 8001:8001 mcp-orchestrator
```

To supply a custom configuration file and API keys:

```bash
docker run --rm \
  -e MCP_CONFIG_FILE=/config.toml \
  -e OPENAI_API_KEY=your-openai-key \
  -e TAVILY_API_KEY=your-key \
  -v $(pwd)/config.toml:/config.toml \
  mcp-orchestrator
```

This approach makes it easy to extend the container with additional MCP servers without altering the image itself.

## JSON-RPC control server

`json_rpc_server.py` provides a minimal [JSON-RPC 2.0](https://www.jsonrpc.org/specification) implementation. It exposes the standard `initialize`, `shutdown` and `exit` handlers so external tools can configure and gracefully stop the orchestrator.

Run the server on port `4000` (or any other port) with:

```bash
python json_rpc_server.py 4000
```

## Using docker compose

Alternatively you can run the orchestrator with [Docker Compose](https://docs.docker.com/compose/).
Create a `docker-compose.yml` file like the following and run `docker compose up --build`:

```yaml
version: "3.9"
services:
  orchestrator:
    build: .
    ports:
      - "8000:8000"
      - "8001:8001"
    environment:
      MCP_CONFIG_FILE: /config.toml
      OPENAI_API_KEY: your-openai-key
      TAVILY_API_KEY: your-key
    volumes:
      - ./config.toml:/config.toml
```
