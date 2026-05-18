"""
nb_model.py — Reproduction script for the NB crash frequency pipeline.

Executes NB01 -> NB02 -> NB03 -> NB04 in order using nbconvert.
Each notebook is run in-place; its outputs (CSVs, pickles, plots) are written
to the outputs/ directory as defined inside each notebook.

Usage:
    python nb_model.py
    python nb_model.py --data-dir path/to/data --output-dir path/to/outputs

Requirements:
    pip install nbconvert jupyter-client ipykernel
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Notebooks to run in order
PIPELINE = [
    "NB01_data_prep.ipynb",
    "NB02_eda.ipynb",
    "NB03_baseline_model.ipynb",
    "NB04_enriched_model.ipynb",
]


def run_notebook(nb_path: Path, timeout: int = 600) -> bool:
    """Execute a single notebook with nbconvert. Returns True on success."""
    cmd = [
        sys.executable, "-m", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout={timeout}",
        str(nb_path),
    ]
    print(f"  Running {nb_path.name} ...", end=" ", flush=True)
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode == 0:
        print(f"ok ({elapsed:.1f}s)")
        return True
    else:
        print(f"FAILED ({elapsed:.1f}s)")
        print(result.stderr[-2000:])   # last 2000 chars of stderr
        return False


def print_summary(output_dir: Path):
    """Print file sizes and key statistics from nb_model_results.json."""
    print("\n=== Output summary ===")

    # File inventory
    output_files = [
        "nb_model_ready.csv",
        "model_baseline.pkl",
        "model_enriched.pkl",
        "baseline_results.json",
        "nb_model_results.json",
        "nb_comparison_table.csv",
    ]
    for name in output_files:
        path = output_dir / name
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  {name:<35} {size_kb:>8.1f} KB")
        else:
            print(f"  {name:<35} NOT FOUND")

    # Key statistics from nb_model_results.json
    results_path = output_dir / "nb_model_results.json"
    if results_path.exists():
        with open(results_path) as f:
            res = json.load(f)
        print()
        print("Key statistics:")
        bl = res.get("phase3_baseline", {})
        p4 = res.get("phase4_enriched", {})
        print(f"  Baseline  AIC        : {bl.get('aic', 'n/a'):.2f}")
        print(f"  Baseline  alpha      : {bl.get('dispersion_alpha', 'n/a'):.4f}")
        print(f"  Enriched  AIC        : {p4.get('aic', 'n/a'):.2f}")
        print(f"  CV score  beta_z     : {p4.get('cv_score_beta', 'n/a'):.4f}")
        print(f"  CV score  IRR        : {p4.get('cv_score_irr', 'n/a'):.4f}")
        print(f"  LR p-value (Phase 4) : {p4.get('lr_p_vs_baseline', 'n/a'):.4f}")
        print(f"  delta_AIC            : {p4.get('delta_aic_vs_baseline', 'n/a'):+.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Run NB01->NB04 crash model pipeline via nbconvert"
    )
    parser.add_argument(
        "--data-dir", type=Path, default=None,
        help="Override DATA path inside notebooks (not yet implemented — "
             "edit ROOT variable inside each notebook for now)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Override output directory (not yet implemented — "
             "edit ROOT variable inside each notebook for now)",
    )
    parser.add_argument(
        "--timeout", type=int, default=600,
        help="Per-notebook execution timeout in seconds (default: 600)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()   # scripts/../ = nb-model/
    output_dir   = (args.output_dir or project_root / "outputs").resolve()

    print("=== nb_model.py — NB crash frequency pipeline ===")
    print(f"Project : {project_root}")
    print(f"Outputs : {output_dir}")
    print()

    if args.data_dir or args.output_dir:
        print("NOTE: --data-dir / --output-dir are not yet wired to notebook execution.")
        print("      Edit ROOT at the top of each notebook to change paths.\n")

    # Run each notebook in order — notebooks live in pipeline/
    for nb_name in PIPELINE:
        nb_path = project_root / "pipeline" / nb_name
        if not nb_path.exists():
            print(f"  MISSING: {nb_name} — skipping")
            continue
        ok = run_notebook(nb_path, timeout=args.timeout)
        if not ok:
            print(f"\nPipeline stopped at {nb_name}.")
            sys.exit(1)

    print_summary(output_dir)
    print("\nDone.")


if __name__ == "__main__":
    main()
