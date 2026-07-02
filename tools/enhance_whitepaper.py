#!/usr/bin/env python3
"""Convert a course whitepaper PDF to clean, structured markdown.

Pipeline (repeatable — run any time a PDF is added or updated):
  1. markitdown          PDF -> raw markdown (plain text extraction)
  2. de-noise            strip running headers / "May 2026 <page>" footers,
                         including headers glued onto content lines
                         (both detected empirically by frequency)
  3. structure           read the PDF bookmark outline (PyMuPDF) — fall back
                         to parsing the printed Table of Contents — and
                         promote matching body lines to ##/###/#### headings;
                         the flattened TOC block is rebuilt as a nested list
  4. figures & tables    locate "Figure N:" / "Table N:" captions in the PDF,
                         render the region above each caption to PNG under an
                         assets dir, and embed it before the caption so
                         diagrams and tables are not lost
  5. mermaid check       every ```mermaid block in the output is validated
                         with mermaid-cli (mmdc) if available
  6. sanity report       headings promoted, unmatched outline entries,
                         captions without images, mermaid pass/fail,
                         leftover per-page noise

Usage:
  python enhance_whitepaper.py input.pdf [-o out.md] [--assets DIR]
                               [--markitdown BIN] [--no-images] [--zoom 2.0]

Requires: markitdown[pdf], pymupdf  (see tools/requirements.txt)
Optional: mmdc (npm i -g @mermaid-js/mermaid-cli) for mermaid validation.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

MONTH = (r"(January|February|March|April|May|June|July|August|September|"
         r"October|November|December)")
FOOTER_RE = re.compile(rf"^{MONTH} 20\d\d ?\d*$")
TOC_ENTRY_RE = re.compile(r"^(?P<title>.+?)\s+(?P<page>\d{1,3})$")
CAPTION_RE = re.compile(r"^(Figure|Table) (\d+)\s*:")
MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.S)

norm = lambda s: re.sub(r"\s+", " ", s.strip())


def run_markitdown(pdf: Path, binary: str) -> str:
    proc = subprocess.run([binary, str(pdf)], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"markitdown failed on {pdf}:\n{proc.stderr}")
    return proc.stdout


# ---------------------------------------------------------------- de-noise

def detect_running_headers(lines: list[str]) -> tuple[list[str], list[str]]:
    """Find per-page noise empirically.

    Returns (exact_headers, glued_prefixes):
      exact_headers  — full lines repeated on many pages (the paper title)
      glued_prefixes — 'Title<Month> <year>' stuck to the start of content
                       lines, detected by prefix frequency
    """
    exact = Counter(s for ln in lines if (s := ln.strip()) and len(s) < 90)
    glued = Counter()
    glued_re = re.compile(rf"^(.{{3,85}}?){MONTH} 20\d\d")
    for ln in lines:
        m = glued_re.match(ln.strip())
        if m:
            glued[m.group(1)] += 1
    exact_headers = [s for s, n in exact.items()
                     if n >= 8 and not TOC_ENTRY_RE.match(s)]
    glued_prefixes = [p for p, n in glued.items() if n >= 5]
    return exact_headers, glued_prefixes


def denoise(lines: list[str]) -> tuple[list[str], int, str | None]:
    """Remove running headers/footers.

    Returns (lines, removed_count, header_title) where header_title is the
    document title inferred from the running header, if one was detected.
    """
    exact_headers, glued_prefixes = detect_running_headers(lines)
    header_title = max(glued_prefixes + exact_headers, key=len, default=None)
    if header_title:  # exact headers can carry the date stamp, e.g. "...May 2026"
        header_title = re.sub(rf"\s*{MONTH} ?20\d\d$", "", header_title).strip()
    glued_res = [re.compile(rf"^{re.escape(p)}{MONTH} 20\d\d")
                 for p in glued_prefixes]
    out, removed = [], 0
    exact = set(exact_headers)
    for ln in lines:
        s = ln.strip()
        if FOOTER_RE.match(s) or s in exact:
            removed += 1
            continue
        for rx in glued_res:
            m = rx.match(s)
            if m:
                removed += 1
                s = s[m.end():].strip()
                break
        else:
            out.append(ln)
            continue
        if s:
            out.append(s)
    return out, removed, header_title


def detect_title(lines: list[str], header_title: str | None) -> str:
    """Document title for the H1: prefer the running-header text, else join
    the wrapped title block that precedes the Authors line."""
    if header_title:
        return header_title
    parts = []
    for ln in lines:
        s = ln.strip()
        if not s:
            if parts:
                break
            continue
        if s.lower().startswith("authors") or len(parts) == 4:
            break
        parts.append(s)
    if not parts:
        sys.exit("empty markitdown output")
    return " ".join(parts)


# --------------------------------------------------------------- structure

def outline_entries(pdf: Path) -> list[tuple[str, int]]:
    """[(title, markdown_level)] from the PDF bookmark outline."""
    import fitz

    doc = fitz.open(pdf)
    toc = doc.get_toc()
    doc.close()
    return [(norm(t), min(lvl + 1, 6)) for lvl, t, _page in toc]


def text_toc_entries(lines: list[str]) -> list[tuple[str, int]]:
    """Fallback: parse a printed 'Title ..... page' table of contents."""
    starts = [i for i, ln in enumerate(lines)
              if ln.strip() == "Table of contents"]
    if not starts:
        return []
    entries, last_hit = [], starts[0]
    for i in range(starts[0], min(starts[0] + 120, len(lines))):
        s = lines[i].strip()
        if not s or s == "Table of contents":
            continue
        m = TOC_ENTRY_RE.match(s)
        if m and int(m.group("page")) < 200:
            title = m.group("title").rstrip(". ")
            entries.append((norm(title), 2 if re.match(r"^\d+\.\s", title) else 3))
            last_hit = i
        elif i - last_hit > 3:
            break
    return entries


def promote_headings(lines: list[str],
                     entries: list[tuple[str, int]]) -> tuple[list[str], list[str]]:
    """Promote body lines matching outline titles to markdown headings.

    A title can also appear verbatim inside the printed TOC, so the LAST
    standalone occurrence is treated as the real body heading. Headings that
    wrap over 2–3 lines in the extracted text are joined.
    """
    wanted = dict(entries)
    # candidate positions per title: (start_line, n_lines)
    candidates: dict[str, tuple[int, int]] = {}
    for i in range(len(lines)):
        if not lines[i].strip():
            continue
        for n in (1, 2, 3):
            if i + n > len(lines):
                break
            joined = norm(" ".join(lines[i:i + n]))
            if joined in wanted:
                candidates[joined] = (i, n)  # later hits overwrite -> last
                break

    replace: dict[int, tuple[str, int]] = {
        pos: (title, n) for title, (pos, n) in candidates.items()}
    out, skip = [], 0
    for i, ln in enumerate(lines):
        if skip:
            skip -= 1
            continue
        if i in replace:
            title, n = replace[i]
            out.append(f"{'#' * wanted[title]} {title}")
            skip = n - 1
        else:
            out.append(ln)
    unmatched = [t for t in wanted if t not in candidates]
    return out, unmatched


def rebuild_toc(lines: list[str], entries: list[tuple[str, int]]) -> list[str]:
    """Replace the flattened printed TOC (between the 'Table of contents'
    line and the first promoted heading) with a nested markdown list."""
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip() == "Table of contents")
    except StopIteration:
        return lines
    heading_re = re.compile(r"^#{2,6} ")
    end = next((i for i in range(start + 1, len(lines))
                if heading_re.match(lines[i])), None)
    if end is None:
        return lines
    min_lvl = min(lvl for _t, lvl in entries)
    toc_block = ["## Table of contents", ""]
    toc_block += [f"{'  ' * (lvl - min_lvl)}- {t}" for t, lvl in entries]
    toc_block.append("")
    return lines[:start] + toc_block + lines[end:]


# --------------------------------------------------------- figures & tables

def extract_captions(lines: list[str]) -> list[str]:
    """Caption labels like 'Figure 3:' present in the markdown, in order."""
    seen, labels = set(), []
    for ln in lines:
        m = CAPTION_RE.match(ln.strip())
        if m:
            label = f"{m.group(1)} {m.group(2)}:"
            if label not in seen:
                seen.add(label)
                labels.append(label)
    return labels


def render_caption_images(pdf: Path, labels: list[str], assets: Path,
                          zoom: float) -> dict[str, Path]:
    """For each caption label, render the page region above the caption
    (where the figure/table sits) to a PNG. Falls back to the full page."""
    import fitz

    images: dict[str, Path] = {}
    doc = fitz.open(pdf)
    assets.mkdir(parents=True, exist_ok=True)
    for label in labels:
        for page in doc:
            hits = page.search_for(label)
            if not hits:
                continue
            cap = hits[0]
            top_margin = 45  # skip the running-header band
            clip = fitz.Rect(0, top_margin, page.rect.width, cap.y0 - 2)
            if clip.height < 60:  # caption at top of page -> take full page
                clip = fitz.Rect(0, top_margin, page.rect.width,
                                 page.rect.height - 40)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
            name = label.rstrip(":").lower().replace(" ", "-") + ".png"
            path = assets / name
            pix.save(path)
            images[label] = path
            break
    doc.close()
    return images


def embed_images(lines: list[str], images: dict[str, Path],
                 md_dir: Path) -> list[str]:
    out, done = [], set()
    for ln in lines:
        m = CAPTION_RE.match(ln.strip())
        if m:
            label = f"{m.group(1)} {m.group(2)}:"
            if label in images and label not in done:
                done.add(label)
                rel = images[label].relative_to(md_dir)
                out.append(f"![{label.rstrip(':')}]({rel})")
                out.append("")
                out.append(f"*{ln.strip()}*")
                continue
        out.append(ln)
    return out


# ------------------------------------------------------------------ checks

def validate_mermaid(text: str) -> list[tuple[int, bool, str]]:
    """Validate each ```mermaid block with mmdc. Returns (idx, ok, msg)."""
    blocks = MERMAID_RE.findall(text)
    if not blocks:
        return []
    mmdc = shutil.which("mmdc")
    results = []
    for i, block in enumerate(blocks, 1):
        if not mmdc:
            results.append((i, False, "mmdc not installed — skipped"))
            continue
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "d.mmd"
            src.write_text(block)
            proc = subprocess.run(
                [mmdc, "-i", str(src), "-o", str(Path(td) / "d.svg"),
                 "--quiet"], capture_output=True, text=True, timeout=120)
            ok = proc.returncode == 0
            msg = "ok" if ok else (proc.stderr or proc.stdout).strip()[:200]
            results.append((i, ok, msg))
    return results


def sanity_check(text: str, title: str) -> list[str]:
    """Residual-noise scan of the final markdown."""
    problems = []
    lines = text.split("\n")
    footers = sum(1 for ln in lines if FOOTER_RE.match(ln.strip()))
    if footers:
        problems.append(f"{footers} page-footer lines remain")
    headers = sum(1 for ln in lines[1:] if ln.strip() == title)
    if headers:
        problems.append(f"{headers} running-header lines remain")
    glued = sum(1 for ln in lines
                if re.match(rf"^{re.escape(title)}{MONTH}", ln.strip()))
    if glued:
        problems.append(f"{glued} glued header prefixes remain")
    return problems


# -------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert a course whitepaper PDF to structured markdown")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-o", "--output", type=Path,
                    help="output .md (default: alongside the PDF)")
    ap.add_argument("--assets", type=Path,
                    help="image dir (default: <md dir>/assets/<pdf stem>)")
    ap.add_argument("--markitdown", default="markitdown",
                    help="markitdown executable to use")
    ap.add_argument("--no-images", action="store_true",
                    help="skip figure/table image extraction")
    ap.add_argument("--zoom", type=float, default=2.0,
                    help="render scale for extracted images")
    args = ap.parse_args()

    out_md = args.output or args.pdf.with_suffix(".md")
    assets = args.assets or out_md.parent / "assets" / args.pdf.stem

    raw = run_markitdown(args.pdf, args.markitdown)
    lines, removed, header_title = denoise(raw.split("\n"))
    title = detect_title(lines, header_title)

    entries = outline_entries(args.pdf)
    source = "PDF outline"
    if not entries:
        entries = text_toc_entries(lines)
        source = "printed TOC"
    unmatched: list[str] = []
    if entries:
        lines, unmatched = promote_headings(lines, entries)
        lines = rebuild_toc(lines, entries)

    # the wrapped title block becomes a single H1
    start = next((i for i, ln in enumerate(lines) if ln.strip()), 0)
    end = start
    while (end < len(lines) and lines[end].strip()
           and not lines[end].strip().lower().startswith("authors")
           and not lines[end].startswith("#") and end - start < 4):
        end += 1
    lines[start:end] = [f"# {title}"]

    captions = extract_captions(lines)
    images: dict[str, Path] = {}
    if captions and not args.no_images:
        images = render_caption_images(args.pdf, captions, assets, args.zoom)
        lines = embed_images(lines, images, out_md.parent)

    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    out_md.write_text(text, encoding="utf-8")

    # ---- report ----
    print(f"== {args.pdf.name} -> {out_md}")
    print(f"   title: {title}")
    print(f"   noise removed: {removed} header/footer artifacts")
    print(f"   headings promoted ({source}): "
          f"{len(entries) - len(unmatched)}/{len(entries)}")
    for t in unmatched:
        print(f"     unmatched entry: {t!r}")
    print(f"   figures/tables: {len(images)}/{len(captions)} rendered "
          f"-> {assets if images else '(none)'}")
    for c in captions:
        if c not in images:
            print(f"     caption not located in PDF: {c!r}")
    for i, ok, msg in validate_mermaid(text):
        print(f"   mermaid block {i}: {'PASS' if ok else 'FAIL — ' + msg}")
    for p in sanity_check(text, title):
        print(f"   WARNING: {p}")


if __name__ == "__main__":
    main()
