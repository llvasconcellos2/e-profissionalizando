"""
Fast multiline search-and-replace across all HTML files in the rip/ folder.
Supports multiline patterns via Python regex (re.DOTALL).

Usage: python rip_replace.py [--dry-run]
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "rip")
DRY_RUN = "--dry-run" in sys.argv

# --- Define replacements here ---
# Each entry: (pattern_string, replacement_string, flags)
# Use r"..." raw strings. Whitespace tip:
#   \s+ matches any whitespace including newlines
#   \r?\n matches a line break (CR+LF or LF)
#   [ \t]* matches optional spaces/tabs on the same or next line
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

modified = 0
checked = 0

for dirpath, _, filenames in os.walk(ROOT):
    for filename in filenames:
        if not filename.lower().endswith((".html", ".htm", ".css", ".js", ".php")):
            continue
        filepath = os.path.join(dirpath, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception as e:
            print(f"  SKIP {filepath}: {e}")
            continue

        new_content = content
        for pattern, replacement in compiled:
            new_content = pattern.sub(replacement, new_content)

        checked += 1
        if new_content != content:
            modified += 1
            if DRY_RUN:
                print(f"  WOULD MODIFY: {filepath}")
            else:
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(new_content)

print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Checked {checked} files, modified {modified}.")
