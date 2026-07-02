#!/usr/bin/env python3
"""
bash_guard.py — Claude Code PreToolUse hook for the Bash tool.

Purpose: auto-approve Bash commands that are provably safe — read-only, or whose every
write/delete target resolves INSIDE this repo, /tmp scratch, or /dev/null — so working
through the labs (the many `claude -p`, grep, python, mkdir, mcp add/remove steps) does not
prompt on every command. Anything that could modify or delete OUTSIDE the repo (or whose
mutation target can't be statically bounded) gets ASK, so you review it. Reading from
anywhere is permissible.

Decisions (Claude Code PreToolUse protocol, emitted as JSON on stdout):
  - "allow"  : provably safe -> bypass the permission prompt.
  - "ask"    : a mutation we cannot prove is project-confined -> force a prompt (overrides
               broad allow-rules like Bash(curl:*)).
  - "deny"   : a tiny set of catastrophic patterns (rm -rf /, fork bomb, mkfs, dd of=/dev...).
  - (nothing): passthrough -> normal permission flow (existing allow-rules / user prompt).

SAFETY POSTURE: never claim "allow" unless confident. On any parse failure or internal
exception we PASS THROUGH (print nothing, exit 0) so a normal prompt still happens — the hook
can never break a tool call or silently approve something it didn't understand.
"""
from __future__ import annotations
import json
import os
import re
import shlex
import sys

HOME = os.path.expanduser("~")
# Repo root: Claude Code sets CLAUDE_PROJECT_DIR when it runs the hook; fall back
# to two levels up from this file (scripts/hooks/ -> repo root) so it also works
# when invoked by hand.
PROJECT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Roots a command may freely WRITE to / DELETE within without a prompt.
WRITE_ROOTS = [
    os.path.normpath(PROJECT),
    "/tmp", "/private/tmp", "/private/var/folders", "/var/folders",
]
# Sink paths that are always safe write targets.
DEV_SINKS = {"/dev/null", "/dev/stdout", "/dev/stderr"}

# ---- program classification (matched on basename of argv[0]) ----------------

# Shell control-flow keywords. As the FIRST token of a segment these are transparent:
#  - SHELL_SKIP    : structural tokens that execute nothing on their own -> strip / skip.
#  - SHELL_HEADER  : `for x in LIST` / `select x in LIST` / `case x in` — the iteration list is
#                    DATA (globs/strings), no command runs in this segment -> skip it entirely.
#  - SHELL_COND    : followed by a CONDITION command (`while grep ...`, `if [ ... ]`) -> strip the
#                    keyword and classify the rest as a normal command.
SHELL_SKIP = {"do", "then", "else", "fi", "done", "esac", ";;", "time", "!", "{", "}", "(", ")"}
SHELL_HEADER = {"for", "select", "case"}
SHELL_COND = {"while", "until", "if", "elif"}

# Programs that WRITE/DELETE; safe iff every target is confined to WRITE_ROOTS.
WRITE_FAMILY = {
    "rm", "rmdir", "unlink", "mv", "cp", "rsync", "dd", "truncate", "shred",
    "tee", "ln", "link", "install", "mkdir", "mkfifo", "touch",
    "chmod", "chown", "chgrp", "chflags", "setfacl",
    "zip", "unzip", "tar", "gzip", "gunzip", "bzip2", "xz", "patch", "cpio",
}
# Of WRITE_FAMILY, these only WRITE the destination (last path); earlier paths are read-sources
# that may live anywhere (a copy/link/install doesn't mutate its source).
DEST_ONLY = {"cp", "ln", "link", "install", "rsync"}

# Always force ASK: privileged / opaque / network-mutating / process-control.
ALWAYS_ASK = {
    "sudo", "su", "doas", "mkfs", "fdisk", "gdisk", "diskutil", "format", "newfs",
    "launchctl", "systemctl", "service", "crontab", "at", "batch",
    "pmset", "nvram", "scutil", "networksetup", "dscl", "defaults",
    "security", "kextload", "kextunload", "csrutil", "spctl", "codesign",
    "kill", "killall", "pkill", "reboot", "shutdown", "halt", "poweroff",
    "scp", "sftp", "rsync_remote",  # rsync handled in write-family for local; ssh below
    "ssh", "eval", "exec", "source", ".", "osascript", "automator",
    "chsh", "passwd", "visudo", "mount", "umount", "ifconfig", "route",
}

# Command wrappers that just run another command — unwrapped so the inner command is classified.
WRAPPERS = {"timeout", "nohup", "time", "nice", "ionice", "stdbuf", "xargs", "watch",
            "parallel", "env", "setsid", "script"}

METACHAR = re.compile(r"[\*\?\[\]\{\}~]")
_META_FIRST = re.compile(r"[$`*?\[\]{}~]")          # first unbounded char in a path
_VAR_REF = re.compile(r"\$\{(\w+)\}|\$(\w+)")       # $VAR / ${VAR}
_ASSIGN = re.compile(r"^([A-Za-z_]\w*)=(.*)$")      # VAR=value token


def _collect_vars(masked: str) -> "dict[str, str]":
    """Capture leading `VAR=literal` assignments across the command so a later `$VAR` in a write
    target can be resolved (e.g. `RAW=external/x; curl -o "$RAW/f"`). Only literal values (no nested
    $/backtick) are kept; this is an over-approximation toward ALLOW, which is the danger-model bias."""
    varmap: "dict[str, str]" = {}
    for seg in split_segments(masked):
        try:
            toks = shlex.split(_extract_redirects(seg)[0], comments=False, posix=True)
        except ValueError:
            continue
        for t in toks:
            if t == "export":
                continue
            m = _ASSIGN.match(t)
            if m and "$" not in m.group(2) and "`" not in m.group(2):
                varmap[m.group(1)] = m.group(2)
            else:
                break  # only leading assignments bind; first real arg ends the assignment run
    return varmap


def _expand_vars(path: str, varmap: "dict[str, str] | None") -> str:
    if not varmap or "$" not in path:
        return path
    return _VAR_REF.sub(lambda m: varmap.get(m.group(1) or m.group(2), m.group(0)), path)


def _strip_heredocs(cmd: str) -> str:
    """Remove here-doc BODY lines (and let the `<<WORD` operator line stay). A here-doc body is fixed
    DATA fed to a program's stdin — NOT shell code — so parsing it as commands/redirects causes
    spurious asks (e.g. `python3 <<'PY' ... print(f"{x>y}") ... PY`). Here-strings (`<<<`) have no
    body and are left intact. Catastrophic/pipe-to-shell checks run on the RAW command beforehand, so
    dropping the body here doesn't weaken the deny backstop."""
    if "<<" not in cmd:
        return cmd
    out, queue = [], []
    for line in cmd.split("\n"):
        if queue:                                   # inside a here-doc body -> drop the line
            if line.strip() == queue[0]:
                queue.pop(0)                        # terminator reached
            continue
        for m in re.finditer(r"<<-?\s*([\"']?)([A-Za-z_]\w*)\1", line):
            if m.start() > 0 and line[m.start() - 1] == "<":
                continue                            # `<<<` here-string, not a here-doc
            queue.append(m.group(2))
        out.append(line)
    return "\n".join(out)


def _norm(path: str, cwd: "str | None"):
    if path.startswith("~"):
        path = HOME + path[1:]
    if not os.path.isabs(path):
        if cwd is None:
            return None  # relative path with an unknown cwd -> cannot bound
        path = os.path.join(cwd, path)
    return os.path.normpath(path)


def _under_root(p: "str | None") -> bool:
    if p is None:
        return False
    return any(p == root or p.startswith(root + os.sep) for root in WRITE_ROOTS)


def _confined(path: str, cwd: "str | None", varmap: "dict[str, str] | None" = None):
    """Return True (inside write roots), False (outside), or None (undeterminable).

    Resolves known `$VAR` assignments first. If a path still carries a variable/glob/substitution we
    fall back to its LITERAL leading directory (the part before the first unbounded char, cut at the
    last '/'): if that directory is inside a write root and the path has no literal `..`, the write is
    confined (e.g. `/tmp/$c.o`, `build/*.tmp`). A bare leading `$VAR`/glob (no literal prefix, e.g.
    `$TARGET/build`) stays undeterminable -> ask."""
    if not path:
        return None
    if path in DEV_SINKS:
        return True
    path = _expand_vars(path, varmap)
    if path in DEV_SINKS:
        return True
    m = _META_FIRST.search(path)
    if m:                                            # still unbounded after expansion
        if ".." in path.split("/"):
            return None                             # literal parent-traversal -> can't bound
        prefix = path[:m.start()]
        cut = prefix.rfind("/")
        if cut >= 0 and _under_root(_norm(prefix[:cut + 1], cwd)):
            return True                             # literal leading dir is inside a write root
        return None
    p = _norm(path, cwd)
    if p is None:
        return None
    return True if _under_root(p) else False


def _basename(prog: str) -> str:
    return os.path.basename(prog)


def _catastrophic(cmd: str) -> bool:
    c = cmd.strip()
    pats = [
        r"\brm\s+(-[a-zA-Z]*\s+)*(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+/(\s|$|\*)",
        r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:",          # fork bomb
        r"\bmkfs\b", r"\bdd\b[^\n]*\bof=/dev/",
        r">\s*/dev/(disk|sd|rdisk|nvme)", r"\bchmod\b[^\n]*\s/(\s|$)",
    ]
    return any(re.search(p, c) for p in pats)


def _strip_env_and_wrappers(tokens):
    """Drop leading VAR=val assignments and simple command wrappers; return inner tokens."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            i += 1
            continue
        base = _basename(t)
        if base == "env" and i + 1 < len(tokens) and "=" in tokens[i + 1]:
            i += 1
            continue
        break
    return tokens[i:], (i > 0 and any(_basename(t) in WRAPPERS for t in tokens[:i]))


def split_segments(cmd: str):
    """Split a compound command into simple commands on top-level ; && || | & and newlines,
    respecting quotes and $( ) depth. Backticks are flagged separately as substitution."""
    segs, buf = [], ""
    i, n, quote, depth = 0, len(cmd), None, 0
    while i < n:
        c = cmd[i]
        if quote:
            buf += c
            if c == quote and (quote == "'" or cmd[i - 1] != "\\"):
                quote = None
            i += 1
            continue
        if c in "'\"":
            quote = c
            buf += c
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            buf += c + cmd[i + 1]
            i += 2
            continue
        if c == "$" and i + 1 < n and cmd[i + 1] == "(":
            depth += 1
            buf += "$("
            i += 2
            continue
        if depth > 0:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            buf += c
            i += 1
            continue
        if cmd.startswith("&&", i) or cmd.startswith("||", i):
            segs.append(buf)
            buf = ""
            i += 2
            continue
        if c == "&":
            # '&' is a background-job separator ONLY as a standalone control operator. When it is
            # part of a redirection — fd-dup '>&'/'<&' (e.g. 2>&1, 1>&2) or 'redirect-both' '&>'/'&>>'
            # — it is NOT a separator; splitting there would strip the redirect's target and leave a
            # dangling '2>' that looks like an unbounded write (spurious "ask"). Keep those together.
            prev = buf[-1] if buf else ""
            nxt = cmd[i + 1] if i + 1 < n else ""
            if prev in "<>" or nxt == ">":
                buf += c
                i += 1
                continue
        if c in ";\n|&":
            segs.append(buf)
            buf = ""
            i += 1
            continue
        buf += c
        i += 1
    segs.append(buf)
    return [s.strip() for s in segs if s.strip()]


SUBST_TOKEN = "$SUBST"  # placeholder for a command substitution; the $ keeps it unbounded as a path


def _extract_substitutions(cmd: str):
    """Pull the inner command strings out of top-level command/process substitutions
    ($( ), backticks, <( ), >( )) and return (bodies, masked) where each substitution in `cmd`
    is replaced by SUBST_TOKEN. Single-quoted text is literal (no substitution) and left intact.
    The mask lets shlex parse the rest cleanly; the bodies are classified recursively so a
    read-only $(grep ...) is allowed but $(rm ...) still asks/denies."""
    bodies, out = [], ""
    i, n, quote = 0, len(cmd), None
    while i < n:
        c = cmd[i]
        if quote:
            out += c
            if c == quote and (quote == "'" or cmd[i - 1] != "\\"):
                quote = None
            i += 1
            continue
        if c in "'\"":
            quote = c
            out += c
            i += 1
            continue
        # $( ... )  command substitution (depth-aware)
        if c == "$" and i + 1 < n and cmd[i + 1] == "(":
            depth, j, body = 1, i + 2, ""
            while j < n and depth:
                if cmd[j] == "(":
                    depth += 1
                elif cmd[j] == ")":
                    depth -= 1
                if depth:
                    body += cmd[j]
                j += 1
            bodies.append(body)
            out += SUBST_TOKEN
            i = j
            continue
        # <( ... ) / >( ... )  process substitution (also runs a command)
        if c in "<>" and i + 1 < n and cmd[i + 1] == "(":
            depth, j, body = 1, i + 2, ""
            while j < n and depth:
                if cmd[j] == "(":
                    depth += 1
                elif cmd[j] == ")":
                    depth -= 1
                if depth:
                    body += cmd[j]
                j += 1
            bodies.append(body)
            out += SUBST_TOKEN
            i = j
            continue
        # `...`  backtick substitution
        if c == "`":
            j, body = i + 1, ""
            while j < n and cmd[j] != "`":
                body += cmd[j]
                j += 1
            bodies.append(body)
            out += SUBST_TOKEN
            i = j + 1
            continue
        out += c
        i += 1
    return bodies, out


def _curl_targets(tokens):
    """Targets a curl/wget invocation writes to. Empty list == writes to stdout only."""
    targets, out_dir, writes_cwd = [], None, False
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("-o", "--output") and i + 1 < len(tokens):
            targets.append(tokens[i + 1])
            i += 2
            continue
        if t.startswith("--output=") or t.startswith("--output-document="):
            targets.append(t.split("=", 1)[1])
            i += 1
            continue
        if t in ("-O", "--remote-name", "--output-document"):
            writes_cwd = True
            i += 1
            continue
        if t in ("--output-dir", "-P", "--directory-prefix") and i + 1 < len(tokens):
            out_dir = tokens[i + 1]
            i += 1
            continue
        i += 1
    base = _basename(tokens[0])
    if base == "wget" and not targets and not writes_cwd:
        writes_cwd = True  # wget defaults to writing into cwd
    if writes_cwd:
        targets.append(os.path.join(out_dir, "x") if out_dir else "x")  # representative cwd-relative path
    elif out_dir and targets:
        targets = [os.path.join(out_dir, os.path.basename(t)) for t in targets]
    return targets


# ---- DANGER-MODEL helpers (default-ALLOW; ASK only on the enumerated danger set) ----------------
# Non-destructive filesystem creators: never overwrite/delete data, so an unbounded/outside target is
# harmless -> never a reason to prompt.
NON_DESTRUCTIVE_CREATE = {"mkdir", "mkfifo", "touch"}

# Reading these well-known credential/secret paths warrants a prompt (possible exfil prep).
_SECRET_RE = re.compile(
    r"(?:^|/)\.(?:ssh|aws|gnupg|kube|docker|kaggle)(?:/|$)"
    r"|\bid_(?:rsa|dsa|ecdsa|ed25519)\b"
    r"|(?:^|/)\.(?:netrc|pgpass|pypirc|npmrc)\b"
    r"|(?:^|/)\.env(?:\.[\w.]+)?$", re.I)

# Pipe-to-shell / execute-downloaded-content (remote code execution) patterns.
_DL = r"(?:curl|wget|fetch)"
_SHELLS = r"(?:sh|bash|zsh|dash|ksh|python3?|perl|ruby|node)"
# `download | interpreter` is RCE only when the interpreter EXECUTES STDIN as code. A fixed inline
# script (-c CMD / -m MOD / -e CODE) makes the piped download mere DATA on stdin (e.g.
# `curl ... | python3 -c "json.load(sys.stdin)"`), which is NOT code execution -> don't flag it.
_PIPE_TO_SHELL = re.compile(
    rf"{_DL}\b[^|;&\n]*\|\s*(?:sudo\s+)?{_SHELLS}\b(?!\s+-(?:c|m|e)\b)", re.I)
_PROCSUB_SHELL = re.compile(rf"\b{_SHELLS}\b\s+(?:-\S+\s+)*<\(\s*{_DL}\b", re.I)
_DLEXEC = re.compile(rf"\b(?:sh|bash|zsh|dash|eval)\b[^\n]*\$\([^)]*{_DL}\b", re.I)

# Quote-aware redirect operator scanner (used on the RAW segment, NOT on quote-stripped tokens).
_REDIR_RE = re.compile(r"&>>|&>|\d*>>|\d*>&|\d*>\||\d*>|\d*<&|\d*<<<|\d*<<|\d*<")


def _pipe_to_shell(cmd: str) -> bool:
    return bool(_PIPE_TO_SHELL.search(cmd) or _PROCSUB_SHELL.search(cmd) or _DLEXEC.search(cmd))


def _secret_paths(args) -> bool:
    return any(_SECRET_RE.search(a) for a in args)


def _extract_redirects(seg: str):
    """Quote-aware: pull shell redirections out of a RAW segment string. Returns (cleaned, write_targets).
    Only UNQUOTED operators are redirects — a quoted '>foo' (e.g. a grep regex ">[A-Z]+<") is DATA and
    is left in place. fd-dups ('>&1', '2>&1') and read redirects ('<','<<') yield NO write target. An
    operator with no parseable target is dropped without a target (fail open)."""
    out, targets = [], []
    i, n, quote, depth = 0, len(seg), None, 0
    while i < n:
        c = seg[i]
        if quote:
            out.append(c)
            if c == quote and (quote == "'" or seg[i - 1] != "\\"):
                quote = None
            i += 1
            continue
        if c in "'\"":
            quote = c; out.append(c); i += 1; continue
        if c == "\\" and i + 1 < n:
            out.append(c + seg[i + 1]); i += 2; continue
        if c == "(":
            depth += 1; out.append(c); i += 1; continue
        if c == ")" and depth > 0:
            depth -= 1; out.append(c); i += 1; continue
        if depth == 0 and c in "<>&0123456789":
            m = _REDIR_RE.match(seg, i)
            if m and (">" in m.group(0) or "<" in m.group(0)):
                op = m.group(0)
                i = m.end()
                is_write = ">" in op
                is_dup = ">&" in op or "<&" in op
                while i < n and seg[i] in " \t":   # skip spaces before the target word
                    i += 1
                tq, tgt = None, []
                while i < n:                       # read the target word (quote-aware)
                    ch = seg[i]
                    if tq:
                        if ch == tq and (tq == "'" or seg[i - 1] != "\\"):
                            tq = None
                        else:
                            tgt.append(ch)
                        i += 1
                        continue
                    if ch in "'\"":
                        tq = ch; i += 1; continue
                    if ch in " \t<>|&;\n":
                        break
                    tgt.append(ch); i += 1
                target = "".join(tgt)
                if is_write and not is_dup and target and not target.startswith("&"):
                    targets.append(target)
                continue
        out.append(c); i += 1
    return "".join(out), targets


def classify(cmd: str, cwd: str, _depth: int = 0):
    """Return (decision, reason). decision in {'allow','ask','deny'}.

    DANGER model (default-ALLOW): DENY catastrophic patterns; ASK only on an enumerated danger set —
    writes/deletes to a path outside the project or an unbounded target, pipe-to-shell / exec of
    downloaded content, credential/secret reads, privileged/opaque commands, git push. Everything
    else (read-only tools, in-project mutations, network GETs, interpreters, unparsed-but-benign)
    ALLOWS. Tradeoff: an interpreter call's INTERNAL behavior isn't introspected — the catastrophic
    DENY layer is the backstop."""
    if _catastrophic(cmd):
        return "deny", "matches a catastrophic destructive pattern (e.g. rm -rf /, mkfs, dd of=/dev)"

    # RCE: download piped into / executed by a shell.
    if _pipe_to_shell(cmd):
        return "ask", "downloads content and pipes/execs it through a shell (review)"

    # Here-doc bodies are stdin DATA, not shell code — drop them so their text isn't mis-parsed as
    # commands/redirects (the catastrophic + pipe-to-shell scans above already ran on the raw command).
    cmd = _strip_heredocs(cmd)

    # Command/process substitutions run their own commands — classify each recursively so a dangerous
    # $(...) still surfaces (a catastrophic body denies, a risky one asks). Benign bodies are fine.
    bodies, masked = _extract_substitutions(cmd)
    varmap = _collect_vars(masked)  # VAR=literal assignments -> resolve later `$VAR` write targets
    for b in bodies:
        if not b.strip():
            continue
        if _depth >= 6:
            return "ask", "command substitution nests too deeply to analyze (review)"
        d, r = classify(b, cwd, _depth + 1)
        if d in ("deny", "ask"):
            return d, f"inside a command substitution: {r}"

    cwd_cur = cwd
    for seg in split_segments(masked):
        # Quote-aware redirect extraction FIRST: a quoted '>' (e.g. a grep regex ">[A-Z]+<") is DATA,
        # not a redirection. Only a WRITE redirect to a path outside the project / unbounded is risky.
        seg, redir_targets = _extract_redirects(seg)
        for tgt in redir_targets:
            if _confined(tgt, cwd_cur, varmap) is not True:
                return "ask", f"redirects output to a path outside the project (review): {tgt}"
        try:
            toks = shlex.split(seg, comments=False, posix=True)
        except ValueError:
            continue  # unparseable -> fail OPEN (bash parses it; we don't block weird-but-benign)
        if not toks:
            continue
        toks, _ = _strip_env_and_wrappers(toks)
        if not toks:
            continue

        # transparent shell control-flow: strip structural keywords; loop/case headers run nothing
        while toks and toks[0] in SHELL_SKIP:
            toks = toks[1:]
        if not toks:
            continue
        if toks[0] in SHELL_HEADER:
            continue  # `for x in LIST` / `case x in` — iteration list is data, no command executes
        if toks[0] in SHELL_COND:
            toks = toks[1:]  # `while`/`if`/`elif` <condition-command> — classify the condition
            if not toks:
                continue

        prog = _basename(toks[0])
        rest = toks[1:]

        if prog == "cd":   # track cd for relative-path resolution in later segments
            tgt = rest[0] if rest else HOME
            cwd_cur = _norm(tgt, cwd_cur) if _confined(tgt, cwd_cur, varmap) is True else None
            continue

        # ---- DANGER SET — anything NOT flagged below falls through to the default ALLOW ----
        if prog in ALWAYS_ASK:
            return "ask", f"privileged/opaque command (review): {prog}"
        if _secret_paths(rest):
            return "ask", f"reads a credential/secret path (review): {prog}"
        if prog == "git":
            sub = next((a for a in rest if not a.startswith("-")), "")
            if sub == "push":
                return "ask", "git push publishes to a remote (review)"
            continue
        if prog == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok", "-okdir",
                                        "-fprint", "-fprintf", "-fls") for a in rest):
            roots = [a for a in rest if not a.startswith("-")] or ["."]
            if any(_confined(r, cwd_cur, varmap) is not True for r in roots):
                return "ask", "find -delete/-exec over a path outside the project (review)"
            continue
        if prog in ("curl", "wget"):
            # Network fetch is fine (GET/POST to stdout); ASK only if it WRITES to a path outside the
            # project / unbounded (a download can clobber a file). Pipe-to-shell is caught earlier.
            for tgt in _curl_targets(toks):
                if _confined(tgt, cwd_cur, varmap) is not True:
                    return "ask", f"{prog} writes a download to a path outside the project (review): {tgt}"
            continue
        if prog in NON_DESTRUCTIVE_CREATE:
            continue  # mkdir / mkfifo / touch never overwrite or delete data -> allow any target
        if prog in WRITE_FAMILY or (prog == "sed" and any(a.startswith("-i") for a in rest)):
            # Destructive (rm/mv/cp/dd/tee/sed -i/chmod/tar/...). ASK only when it writes or deletes a
            # path OUTSIDE the project or an UNBOUNDED target — the irreversible class. Confined -> allow.
            if cwd_cur is None:
                return "ask", f"{prog} after a 'cd' to an unbounded location (review)"
            paths = [a for a in rest if not a.startswith("-")]
            if prog == "dd":
                paths = [a.split("=", 1)[1] for a in rest if a.startswith("of=")]
            elif prog == "sed":
                paths = paths[1:] or paths            # drop the script arg; the rest are edited in place
            elif prog in DEST_ONLY and len(paths) > 1:
                paths = paths[-1:]                    # only the destination is written
            if any(_confined(p, cwd_cur, varmap) is not True for p in paths):
                return "ask", f"{prog} writes/deletes a path outside the project or unbounded (review)"
            continue

        # default: ALLOW — read-only tools, in-project mutations, network GETs, interpreters, unknowns.

    return "allow", "no dangerous operation detected"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        return 0
    cwd = data.get("cwd") or PROJECT
    try:
        decision, reason = classify(cmd, cwd)
    except Exception:
        return 0  # fail open: never break a tool call
    if not decision:
        return 0  # passthrough
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"bash_guard: {reason}",
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
