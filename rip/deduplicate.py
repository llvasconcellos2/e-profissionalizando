import os
import shutil
from pathlib import Path

RIP_DIR = Path(__file__).parent.resolve()
LOG_FILE = RIP_DIR / "deduplicate.log"

HTML_EXTS = {".html", ".htm"}


def main():
    # Collect all HTML files in subdirectories (not root)
    html_files = []
    for root, dirs, files in os.walk(RIP_DIR):
        root_path = Path(root)
        if root_path == RIP_DIR:
            continue
        for f in files:
            if Path(f).suffix.lower() in HTML_EXTS:
                html_files.append(root_path / f)

    # Deepest first — first file to claim a name wins
    html_files.sort(key=lambda p: len(p.parts), reverse=True)

    moved = 0
    deleted = 0
    log_lines = []

    for file_path in html_files:
        dest = RIP_DIR / file_path.name
        if dest.exists():
            file_path.unlink()
            msg = f"DELETED  {file_path.relative_to(RIP_DIR)}"
            deleted += 1
        else:
            shutil.move(str(file_path), str(dest))
            msg = f"MOVED    {file_path.relative_to(RIP_DIR)}  ->  {file_path.name}"
            moved += 1
        print(msg)
        log_lines.append(msg)

    # Remove empty directories bottom-up
    rmdir_count = 0
    for root, dirs, files in os.walk(RIP_DIR, topdown=False):
        root_path = Path(root)
        if root_path == RIP_DIR:
            continue
        try:
            root_path.rmdir()  # only succeeds if truly empty
            msg = f"RMDIR    {root_path.relative_to(RIP_DIR)}"
            print(msg)
            log_lines.append(msg)
            rmdir_count += 1
        except OSError:
            pass  # not empty, leave it

    summary = f"\nDone. moved={moved}  deleted={deleted}  dirs_removed={rmdir_count}"
    print(summary)
    log_lines.append(summary)

    LOG_FILE.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"Log written to {LOG_FILE}")


if __name__ == "__main__":
    main()
