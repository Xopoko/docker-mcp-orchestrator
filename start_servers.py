#!/usr/bin/env python3
import os
import subprocess
import sys
import pathlib
import threading
import signal

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


def _shutdown(signum, frame):
    for p in processes:
        if p.poll() is None:
            p.terminate()
    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    sys.exit(0)


signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)
for srv in servers:
    repo = srv["repo"]
    name = srv.get("name") or pathlib.Path(repo).stem.replace('.git', '')
    dest = BASE_DIR / name
    if not dest.exists():
        subprocess.run(["git", "clone", repo, str(dest)], check=True)
    if (dest / "requirements.txt").exists():
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(dest / "requirements.txt"),
            ],
            check=True,
        )
    if (dest / "setup.py").exists():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(dest)],
            check=True,
        )

    cmd = srv.get("command") or "./start.sh"
    env = os.environ.copy()
    env.update({k: str(v) for k, v in srv.get("env", {}).items()})
    transport = srv.get("transport", "http")
    print(f"Starting {name} ({transport}): {cmd}")
    if transport == "stdio":
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=dest,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        def _forward(src, dst):
            while True:
                data = src.read(1024)
                if not data:
                    try:
                        dst.close()
                    except Exception:
                        pass
                    break
                dst.write(data)
                dst.flush()

        threading.Thread(
            target=_forward,
            args=(sys.stdin.buffer, proc.stdin),
            daemon=True,
        ).start()
        threading.Thread(
            target=_forward,
            args=(proc.stdout, sys.stdout.buffer),
            daemon=True,
        ).start()
    else:
        proc = subprocess.Popen(cmd, shell=True, cwd=dest, env=env)
    processes.append(proc)

for p in processes:
    p.wait()
