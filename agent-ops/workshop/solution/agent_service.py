#!/usr/bin/env python3
"""Agent-as-a-service — reference solution for the agent-ops workshop.

Wraps the harness-eng Pocket-Agent in a production skin: HTTP endpoint,
health check, kill switch, versioned prompts, guardrails, and a JSONL
service log. Stdlib only. Usage:

    python3 agent_service.py            # serves on :8055 (PORT env to change)
    curl localhost:8055/healthz
    curl -s -X POST localhost:8055/task -d '{"task": "..."}'

Expects in the working directory: prompts/v1.txt, prompts/v2.txt and an
`active_version` file naming the live one (e.g. "v1").
"""
import json
import os
import re
import shutil
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    import pocket_agent
except ImportError:
    sys.path.insert(0, str(HERE.parents[2] / "harness-eng" / "workshop" / "solution"))
    import pocket_agent

PORT = int(os.environ.get("PORT", "8055"))
MODEL = os.environ.get("MODEL", "haiku")
MAX_STEPS = int(os.environ.get("MAX_STEPS", "6"))
SERVICE_LOG = "service_log.jsonl"
BASE_SYSTEM = pocket_agent.SYSTEM

# ------------------------------------------------------------- guardrails

SECRET_RE = re.compile(r"(sk-[A-Za-z0-9\-]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,})")
INJECTION_RE = re.compile(
    r"(?i)(ignore (all |any |previous |prior )?(instructions|rules)"
    r"|disregard (the )?system prompt|you are now|exfiltrate)")


def guard_input(task: str) -> list[str]:
    """Flag (don't block) suspicious input — a human reviews flagged traffic."""
    return ["input:injection-pattern"] if INJECTION_RE.search(task) else []


def guard_output(result: str) -> tuple[str, list[str]]:
    """Redact secret-shaped strings from anything leaving the service."""
    if SECRET_RE.search(result):
        return SECRET_RE.sub("[REDACTED]", result), ["output:secret-redacted"]
    return result, []


# ---------------------------------------------------------------- backend


def active_version() -> str:
    return Path("active_version").read_text().strip()


def load_prompt(version: str) -> str:
    return (Path("prompts") / f"{version}.txt").read_text()


def run_task(task: str, version: str, max_steps: int = MAX_STEPS) -> dict:
    """One request through the full path: guards → versioned agent → guards.

    NOTE: this mutates the module-global pocket_agent.SYSTEM to swap prompt
    versions, so it is safe ONLY because the server is single-threaded
    (http.server.HTTPServer, not ThreadingHTTPServer). Under concurrency
    you'd pass the system prompt through explicitly instead of via a global —
    a real seam a production version must close.
    """
    rid = uuid.uuid4().hex[:8]
    flags = guard_input(task)
    pocket_agent.SYSTEM = BASE_SYSTEM + "\n" + load_prompt(version)
    t0 = time.time()
    try:
        result = pocket_agent.run(task, MODEL, max_steps)
        ok = not result.startswith("(stopped:")
    except Exception as e:
        result, ok = f"internal error: {e}", False
    result, out_flags = guard_output(result)
    # We redact the OUTPUT before logging; note the raw task is still logged
    # (truncated) — task inputs can also carry secrets/PII, so a hardened
    # service would run guard_output over the logged task too.
    rec = {"request_id": rid, "ts": round(time.time(), 1), "version": version,
           "ok": ok, "latency_s": round(time.time() - t0, 1),
           "flags": flags + out_flags,
           "task": guard_output(task[:120])[0], "result": result[:200]}
    with open(SERVICE_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


# ---------------------------------------------------------------- service


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/healthz":
            return self._send(404, {"error": "unknown path"})
        problems = []
        if not shutil.which("claude"):
            problems.append("claude CLI not on PATH")
        try:
            v = active_version()
            load_prompt(v)
        except OSError as e:
            v, problems = None, problems + [f"config: {e}"]
        if Path("KILL").exists():
            problems.append("kill switch engaged")
        if problems:
            return self._send(503, {"ok": False, "problems": problems})
        self._send(200, {"ok": True, "version": v, "model": MODEL})

    def do_POST(self):
        if self.path != "/task":
            return self._send(404, {"error": "unknown path"})
        if Path("KILL").exists():   # operator kill switch — fail fast, honestly
            return self._send(503, {"error": "service disabled by operator (KILL file present)"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            task = json.loads(self.rfile.read(n))["task"]
        except (ValueError, KeyError):
            return self._send(400, {"error": "body must be JSON: {\"task\": \"...\"}"})
        rec = run_task(task, active_version())
        self._send(200 if rec["ok"] else 500,
                   {k: rec[k] for k in ("request_id", "version", "ok", "latency_s", "flags", "result")})

    def log_message(self, format, *args):   # access log as JSONL, not stderr noise
        pass


if __name__ == "__main__":
    print(f"agent service on :{PORT}  (model={MODEL}, version={active_version()})")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
