#!/usr/bin/env python3
"""Pocket-Agent — reference solution for the harness-eng workshop.

A complete agent harness in ~130 lines around `claude -p` used as a bare
model: control loop, tool registry, permission gate, context budget,
JSONL traces. Usage:

    python3 pocket_agent.py "your task" [--model haiku] [--max-steps 6]
"""
import argparse
import json
import os
import re
import subprocess
import time

# ---------------------------------------------------------------- tools

ALLOWED_CMDS = {"ls", "cat", "wc", "grep", "echo", "head"}
MAX_OBS = 1500      # context budget: max chars per observation
MAX_TURNS = 10      # context budget: history entries kept


def list_dir(path=".") -> str:
    return "\n".join(sorted(os.listdir(path)))


def read_file(path) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def run_cmd(command) -> str:
    prog = command.strip().split()[0] if command.strip() else ""
    if prog not in ALLOWED_CMDS:                       # permission gate
        return (f"blocked by policy: '{prog}'. Allowed commands: "
                f"{', '.join(sorted(ALLOWED_CMDS))}; or ask the human.")
    proc = subprocess.run(command, shell=True, capture_output=True,
                          text=True, timeout=30)
    return (proc.stdout + proc.stderr).strip() or "(no output)"


TOOLS = {"list_dir": list_dir, "read_file": read_file, "run_cmd": run_cmd}

SYSTEM = """You are an agent that completes tasks step by step using tools.
Reply ONLY with one JSON object, no prose, no code fences:
{"thought": "<brief reasoning>", "action": "<one of: list_dir, read_file, run_cmd, finish>", "args": {...}}

Tools:
- list_dir  args {"path": "."}          — list a directory. Use to explore.
- read_file args {"path": "file.txt"}   — read one file. Prefer specific files over big ones.
- run_cmd   args {"command": "wc -l x"} — run a shell command (ls, cat, wc, grep, echo, head only).
- finish    args {"result": "<answer>"} — REQUIRED final step: give the answer.

Rules: one action per reply; use observations, don't guess; finish as soon
as you can answer. EVERY reply must be exactly one JSON object — even if
you can answer immediately, reply with the finish action, never prose."""

# ---------------------------------------------------------------- model


def call_model(prompt: str, model: str) -> str:
    # The JSON contract goes in the SYSTEM channel (--append-system-prompt):
    # instructions in user text lose to the host's own system prompt.
    proc = subprocess.run(
        ["claude", "-p", "--model", model, "--allowedTools", "",
         "--append-system-prompt", SYSTEM, prompt],
        capture_output=True, text=True, timeout=180)
    return proc.stdout.strip()


def parse_action(text: str):
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# ----------------------------------------------------------------- loop


def truncate(obs: str) -> str:
    if len(obs) > MAX_OBS:
        cut = len(obs) - MAX_OBS
        obs = obs[:MAX_OBS] + f"...[truncated {cut} chars — read a more specific target]"
    return obs


def run(task: str, model: str, max_steps: int) -> str:
    history: list[str] = []
    with open("traces.jsonl", "a") as log:
        for step in range(1, max_steps + 1):
            prompt = f"TASK: {task}\n\n" + "\n".join(history[-MAX_TURNS:])
            t0 = time.time()
            reply = call_model(prompt, model)
            act = parse_action(reply)
            if act is None:
                history.append("OBSERVATION: invalid JSON. Reply with ONLY one JSON object.")
                log.write(json.dumps({"step": step, "action": "parse_error",
                                      "ok": False,
                                      "latency_s": round(time.time() - t0, 1)}) + "\n")
                continue
            history.append(f"ASSISTANT: {json.dumps(act)}")
            name, args = act.get("action"), act.get("args", {}) or {}
            if name == "finish":
                result = str(args.get("result", ""))
                log.write(json.dumps({"step": step, "action": "finish",
                                      "ok": True,
                                      "latency_s": round(time.time() - t0, 1)}) + "\n")
                return result
            fn = TOOLS.get(name)
            if fn is None:
                obs, ok = f"unknown action '{name}'. Use one of: {', '.join(TOOLS)}, finish.", False
            else:
                try:
                    obs, ok = truncate(str(fn(**args))), True
                except Exception as e:  # bad args, missing files, timeouts
                    obs, ok = f"tool error: {e}. Adjust args and retry.", False
            history.append(f"OBSERVATION: {obs}")
            log.write(json.dumps({"step": step, "action": name, "args": args,
                                  "ok": ok,
                                  "latency_s": round(time.time() - t0, 1)}) + "\n")
    return "(stopped: max steps reached)"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--max-steps", type=int, default=6)
    a = ap.parse_args()
    print(run(a.task, a.model, a.max_steps))
