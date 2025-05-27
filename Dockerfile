FROM python:3.12-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git bash dos2unix nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/mcps

# Copy orchestrator scripts and default config
COPY start_servers.sh /usr/local/bin/start_servers.sh
COPY start_servers.py /usr/local/bin/start_servers.py
RUN dos2unix /usr/local/bin/start_servers.sh /usr/local/bin/start_servers.py
# Install OpenAI Codex CLI
RUN npm install -g @openai/codex

# Install Python server CLI and ensure npx/tavily-mcp are available
RUN pip install uvicorn uv
RUN npm install -g npx tavily-mcp
COPY mcp_config.toml /opt/mcps/mcp_config.toml
RUN chmod +x /usr/local/bin/start_servers.sh /usr/local/bin/start_servers.py

ENTRYPOINT ["/usr/local/bin/start_servers.sh"]
