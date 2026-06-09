"""
Fast multiline search-and-replace across all HTML files in the rip/ folder.
Uses ripgrep to find candidate files first, then Python regex for replacement.

Usage:
  python rip_replace.py           # apply replacements
  python rip_replace.py --dry-run # preview only, no writes
"""

import os
import re
import sys
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rip")
DRY_RUN = "--dry-run" in sys.argv

# Prefer VS Code's bundled ripgrep, fall back to PATH
RG_CANDIDATES = [
    r"C:\Users\leona\AppData\Local\Programs\Microsoft VS Code\6a44c352bd\resources\app\node_modules\@vscode\ripgrep-universal\bin\win32-x64\rg.exe",
]
RG = next((p for p in RG_CANDIDATES if os.path.isfile(p)), "rg")

# --- Define replacements here ---
# Each tuple: (search_pattern, replacement, re_flags)
# Tips:
#   \r?\n    — line break (handles Windows CRLF and Unix LF)
#   [ \t]*   — optional spaces/tabs (indentation)
#   \s+      — any whitespace including newlines
REPLACEMENTS = [
    (
        r'<style type="text/css">\r?\n[ \t]*<!--',
        '<style type="text/css">',
        re.IGNORECASE,
    ),
    # Add more replacements below:
    # (
    #     r'find pattern',
    #     'replace with',
    #     re.IGNORECASE,
    # ),
]
# --------------------------------

compiled = [(re.compile(p, f), r) for p, r, f in REPLACEMENTS]

EXTENSIONS = ("*.html", "*.htm", "*.css", "*.js", "*.php")


def find_candidate_files():
    """Use ripgrep to quickly locate files containing any of the patterns."""
    # rg first-pattern term (literal prefix before any special chars) for fast pre-filter
    # We use --multiline (-U) and --files-with-matches (-l)
    first_pattern = REPLACEMENTS[0][0]
    cmd = [
        RG,
        "--multiline",
        "--files-with-matches",
        "--no-heading",
        "-e", first_pattern,
    ]
    for ext in EXTENSIONS:
        cmd += ["--glob", ext]
    cmd.append(ROOT)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        print(f"ripgrep found {len(files)} candidate files in {ROOT}")
        return files
    except FileNotFoundError:
        print(f"ripgrep not found at {RG!r}, falling back to full scan…")
        return None


def full_scan_files():
    """Fallback: walk the entire tree."""
    exts = {e.lstrip("*") for e in EXTENSIONS}
    files = []
    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            if any(fn.lower().endswith(ext) for ext in exts):
                files.append(os.path.join(dirpath, fn))
    print(f"Full scan found {len(files)} files")
    return files


def process_files(files):
    modified = 0
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception as e:
            print(f"  SKIP {filepath}: {e}")
            continue

        new_content = content
        for pattern, replacement in compiled:
            new_content = pattern.sub(replacement, new_content)

        if new_content != content:
            modified += 1
            if DRY_RUN:
                print(f"  WOULD MODIFY: {filepath}")
            else:
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(new_content)

    return modified


candidates = find_candidate_files()
if candidates is None:
    candidates = full_scan_files()

modified = process_files(candidates)
action = "[DRY RUN] Would modify" if DRY_RUN else "Modified"
print(f"\n{action} {modified} of {len(candidates)} candidate files.")
