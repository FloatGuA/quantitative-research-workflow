"""
Export any Jupyter Notebook to PDF via HTML.

Usage:
    python export_pdf.py report.ipynb                  # single file
    python export_pdf.py output/                       # all *.ipynb in directory
"""

import argparse
import subprocess
import sys
from pathlib import Path

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_edge() -> str | None:
    import shutil
    for path in EDGE_PATHS:
        if Path(path).exists():
            return path
    return shutil.which("msedge") or shutil.which("chromium") or shutil.which("google-chrome")


def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)


def export_one(nb_path: Path, edge: str) -> Path:
    """Convert a single .ipynb to PDF. Returns the PDF path."""
    html_path = nb_path.with_suffix(".html")
    pdf_path = nb_path.with_suffix(".pdf")

    # Step 1: ipynb → HTML
    print(f"  {nb_path.name} → {html_path.name}")
    run([
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "html", str(nb_path),
        "--output", html_path.name,
        "--output-dir", str(nb_path.parent),
    ])

    # Step 2: HTML → PDF via Edge
    print(f"  {html_path.name} → {pdf_path.name}")
    subprocess.run([
        edge, "--headless", "--disable-gpu", "--no-sandbox",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ], capture_output=True)

    if not pdf_path.exists():
        print(f"  WARNING: PDF not generated for {nb_path.name}")
    else:
        size_kb = pdf_path.stat().st_size // 1024
        print(f"  Done: {pdf_path.name} ({size_kb} KB)")

    return pdf_path


def collect_targets(path_arg: str) -> list[Path]:
    p = Path(path_arg)
    if p.is_dir():
        targets = sorted(p.glob("*.ipynb"))
        if not targets:
            print(f"No .ipynb files found in {p}")
            sys.exit(1)
        return targets
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)
    return [p]


def main():
    parser = argparse.ArgumentParser(description="Export executed notebooks to PDF.")
    parser.add_argument(
        "target",
        help="Path to a .ipynb file, or a directory to batch-convert all *.ipynb files.",
    )
    args = parser.parse_args()

    edge = find_edge()
    if not edge:
        print("ERROR: Microsoft Edge or Chromium not found.")
        print("Install Edge or Chromium and try again.")
        sys.exit(1)

    targets = collect_targets(args.target)
    print(f"=== Exporting {len(targets)} notebook(s) to PDF ===\n")

    for nb_path in targets:
        export_one(nb_path, edge)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
