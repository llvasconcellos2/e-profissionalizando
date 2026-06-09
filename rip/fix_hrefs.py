"""
Fix <a href> attributes in all HTML files inside the rip/ folder.

After flattening the folder structure, links like:
  href="pt/cursos.html"
  href="component/zoo/item/curso-x.html"
become broken. This script strips every directory prefix from href values
that point to .html/.htm files, leaving only the bare filename.

Rules:
- Only touches <a href="..."> (not src, not <link href>, etc.)
- Only touches paths ending in .html or .htm
- Skips external URLs (http/https/protocol-relative), anchors (#), empty values
- Preserves any fragment (#hash) or query string (?q=...) appended to the filename
- Non-HTML files (images, CSS, JS) are never modified
"""
import re
from pathlib import Path

RIP_DIR = Path(__file__).parent.resolve()
HTML_EXTS = {".html", ".htm"}

# Match entire <a ...> opening tag (multi-line safe)
A_TAG_RE = re.compile(r'<a\b([^>]*)>', re.IGNORECASE | re.DOTALL)

# Match href="..." or href='...' inside a tag's attribute string
HREF_ATTR_RE = re.compile(r"""(href\s*=\s*)(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

# Only flatten relative paths ending in .html / .htm
HTML_EXT_RE = re.compile(r'\.html?(#|\?|$)', re.IGNORECASE)
SKIP_RE = re.compile(r'^(https?://|//|mailto:|tel:|javascript:|#|$)', re.IGNORECASE)


def flatten_href(value: str) -> str | None:
    """Return the flattened basename, or None if the value should not change."""
    if SKIP_RE.match(value):
        return None
    if '/' not in value:
        return None  # already flat
    if not HTML_EXT_RE.search(value):
        return None  # not an HTML link
    basename = value.rsplit('/', 1)[-1]
    return basename if basename != value else None


def fix_file(path: Path) -> int:
    # Try UTF-8 first, fall back to latin-1 (common for older Brazilian sites)
    for enc in ("utf-8", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        enc = "utf-8"

    changes = 0

    def fix_href_attr(h_match):
        nonlocal changes
        full = h_match.group(0)
        prefix = h_match.group(1)
        # group 2 = double-quoted value, group 3 = single-quoted value
        if h_match.group(2) is not None:
            value, quote = h_match.group(2), '"'
        else:
            value, quote = h_match.group(3), "'"
        new_value = flatten_href(value)
        if new_value is None:
            return full
        changes += 1
        return f'{prefix}{quote}{new_value}{quote}'

    def fix_a_tag(a_match):
        new_attrs = HREF_ATTR_RE.sub(fix_href_attr, a_match.group(1))
        return f'<a{new_attrs}>'

    new_text = A_TAG_RE.sub(fix_a_tag, text)
    if changes:
        path.write_text(new_text, encoding=enc)
    return changes


def main():
    files = sorted(p for p in RIP_DIR.iterdir() if p.suffix.lower() in HTML_EXTS)
    total_hrefs = 0
    files_changed = 0

    for f in files:
        n = fix_file(f)
        if n:
            print(f"  {f.name}: {n} href(s) fixed")
            files_changed += 1
            total_hrefs += n

    print(f"\nDone. {files_changed} files updated, {total_hrefs} hrefs fixed.")


if __name__ == "__main__":
    main()
