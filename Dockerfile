FROM python:3.12-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/mcps

# Copy orchestrator scripts and default config
COPY start_servers.sh /usr/local/bin/start_servers.sh
COPY start_servers.py /usr/local/bin/start_servers.py
COPY mcp_config.toml /opt/mcps/mcp_config.toml
RUN chmod +x /usr/local/bin/start_servers.sh /usr/local/bin/start_servers.py

ENTRYPOINT ["/usr/local/bin/start_servers.sh"]
