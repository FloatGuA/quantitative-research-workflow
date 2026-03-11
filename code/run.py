"""
End-to-end report builder.

Auto-detects the .xlsx data file in the current directory, generates notebooks,
executes them, and exports to PDF. All outputs go to ./output/{dataname}_*.

Usage:
    python run.py                        # auto-detect xlsx file
    python run.py --data-name SPX        # specify data file stem
    python run.py --output-dir results   # custom output directory
    python run.py --skip-pdf             # skip PDF export
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)


def find_data_name(data_name_arg: str | None) -> str:
    if data_name_arg:
        return data_name_arg
    xlsx_files = sorted(Path(".").glob("*.xlsx"))
    if not xlsx_files:
        raise FileNotFoundError("No .xlsx file found in current directory. Place your data file here first.")
    if len(xlsx_files) > 1:
        print(f"Multiple xlsx files found: {[f.name for f in xlsx_files]}, using {xlsx_files[0].name}")
    return xlsx_files[0].stem


def find_edge() -> str | None:
    for path in EDGE_PATHS:
        if Path(path).exists():
            return path
    return shutil.which("msedge") or shutil.which("chromium") or shutil.which("google-chrome")


def main():
    parser = argparse.ArgumentParser(description="Build HSI research report end-to-end.")
    parser.add_argument("--data-name", default=None, help="Data file stem (e.g. 'HSI'). Auto-detected if omitted.")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output/).")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip PDF export step.")
    args = parser.parse_args()

    data_name = find_data_name(args.data_name)
    output_dir = Path(args.output_dir)

    print(f"=== Building report for: {data_name}.xlsx ===")
    print(f"=== Output directory: {output_dir}/ ===\n")

    # ── Step 1: Generate notebooks ──────────────────────────────────────────
    print("[1/4] Generating notebooks...")
    run([sys.executable, "create_research_report.py",
         "--data-name", data_name, "--output-dir", str(output_dir)])

    notebooks = {
        "en": output_dir / f"{data_name}_research_report.ipynb",
        "zh": output_dir / f"{data_name}_research_report_zh.ipynb",
    }

    # ── Step 2: Execute notebooks ────────────────────────────────────────────
    print("\n[2/4] Executing notebooks...")
    code_dir = str(Path(".").resolve())
    executed = {}
    for lang, nb_path in notebooks.items():
        out_path = output_dir / f"{data_name}_research_report{'_zh' if lang == 'zh' else ''}_executed.ipynb"
        print(f"  Executing {nb_path.name} ...")
        nb = nbformat.read(nb_path, as_version=4)
        client = NotebookClient(nb, cwd=code_dir)
        client.execute()
        nbformat.write(nb, out_path)
        print(f"  Written to {out_path.name}")
        executed[lang] = out_path

    if args.skip_pdf:
        print("\n[3/4] Skipping HTML export (--skip-pdf).")
        print("[4/4] Skipping PDF export (--skip-pdf).")
    else:
        # ── Step 3: Convert to HTML ──────────────────────────────────────────
        print("\n[3/4] Exporting to HTML...")
        html_files = {}
        for lang, nb_path in executed.items():
            suffix = "_zh" if lang == "zh" else ""
            html_path = output_dir / f"{data_name}_research_report{suffix}.html"
            print(f"  Converting {nb_path.name} → {html_path.name} ...")
            run([
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "html", str(nb_path),
                "--output", html_path.name,
                "--output-dir", str(output_dir),
            ])
            html_files[lang] = html_path

        # ── Step 4: Convert to PDF ───────────────────────────────────────────
        print("\n[4/4] Exporting to PDF...")
        edge = find_edge()
        if not edge:
            print("  WARNING: Edge/Chromium not found, skipping PDF export.")
            print("  Install Microsoft Edge or run with --skip-pdf to suppress this warning.")
        else:
            for lang, html_path in html_files.items():
                suffix = "_zh" if lang == "zh" else ""
                pdf_path = output_dir / f"{data_name}_research_report{suffix}.pdf"
                print(f"  Converting {html_path.name} → {pdf_path.name} ...")
                subprocess.run([
                    edge, "--headless", "--disable-gpu",
                    f"--print-to-pdf={pdf_path.resolve()}",
                    str(html_path.resolve()),
                ], capture_output=True)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n=== Done! Output files in {output_dir}/ ===")
    for f in sorted(output_dir.iterdir()):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name:60s} {size_kb:>6} KB")


if __name__ == "__main__":
    main()
