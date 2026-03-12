"""
End-to-end report builder.

Auto-detects the .xlsx data file in the current directory, generates notebooks,
and executes them. All outputs go to ./output/{dataname}_*.

PDF export is handled separately by export_pdf.py.

Usage:
    python run.py                        # auto-detect xlsx file
    python run.py --data-name SPX        # specify data file stem
    python run.py --output-dir results   # custom output directory
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description="Generate and execute HSI research report notebooks.")
    parser.add_argument("--data-name", default=None, help="Data file stem (e.g. 'HSI'). Auto-detected if omitted.")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output/).")
    args = parser.parse_args()

    data_name = find_data_name(args.data_name)
    output_dir = Path(args.output_dir)
    runtime_dir = output_dir / ".jupyter_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime_dir.resolve())
    os.environ.setdefault("JUPYTER_ALLOW_INSECURE_WRITES", "true")

    import nbformat
    from nbclient import NotebookClient

    print(f"=== Building report for: {data_name}.xlsx ===")
    print(f"=== Output directory: {output_dir}/ ===\n")

    # ── Step 1: Generate notebooks ──────────────────────────────────────────
    print("[1/2] Generating notebooks...")
    run([sys.executable, "create_research_report.py",
         "--data-name", data_name, "--output-dir", str(output_dir)])

    notebooks = {
        "en": output_dir / f"{data_name}_research_report.ipynb",
        "zh": output_dir / f"{data_name}_research_report_zh.ipynb",
    }

    # ── Step 2: Execute notebooks ────────────────────────────────────────────
    print("\n[2/2] Executing notebooks...")
    code_dir = str(Path(".").resolve())
    for lang, nb_path in notebooks.items():
        out_path = output_dir / f"{data_name}_research_report{'_zh' if lang == 'zh' else ''}_executed.ipynb"
        print(f"  Executing {nb_path.name} ...")
        nb = nbformat.read(nb_path, as_version=4)
        client = NotebookClient(nb, cwd=code_dir)
        client.execute()
        nbformat.write(nb, out_path)
        print(f"  Written to {out_path.name}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n=== Done! Output files in {output_dir}/ ===")
    for f in sorted(output_dir.iterdir()):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name:60s} {size_kb:>6} KB")
    print("\nTo export PDF: python export_pdf.py output/<notebook>_executed.ipynb")


if __name__ == "__main__":
    main()
