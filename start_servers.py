#!/usr/bin/env python3
import os
import subprocess
import sys
import pathlib

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

CONFIG_FILE = os.environ.get("MCP_CONFIG_FILE", "/opt/mcps/mcp_config.toml")
BASE_DIR = pathlib.Path("/opt/mcps/repos")
BASE_DIR.mkdir(parents=True, exist_ok=True)

if not pathlib.Path(CONFIG_FILE).exists():
    print(f"Config file {CONFIG_FILE} not found", file=sys.stderr)
    sys.exit(1)

with open(CONFIG_FILE, "rb") as f:
    data = tomllib.load(f)

servers = data.get("server") or data.get("servers") or []
if isinstance(servers, dict):
    servers = [servers]

processes = []
for srv in servers:
    repo = srv["repo"]
    name = srv.get("name") or pathlib.Path(repo).stem.replace('.git', '')
    dest = BASE_DIR / name
    if not dest.exists():
        subprocess.run(["git", "clone", repo, str(dest)], check=True)
    if (dest / "requirements.txt").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(dest / "requirements.txt")], check=True)
    if (dest / "setup.py").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(dest)], check=True)

    cmd = srv.get("command") or "./start.sh"
    env = os.environ.copy()
    env.update({k: str(v) for k, v in srv.get("env", {}).items()})
    print(f"Starting {name}: {cmd}")
    processes.append(subprocess.Popen(cmd, shell=True, cwd=dest, env=env))

for p in processes:
    p.wait()
