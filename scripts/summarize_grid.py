"""Core-grid summary per model x condition x defence. Does NOT score disclosure.

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\summarize_grid.py results\\all_transcripts.csv --out results\\core_grid_summary.csv

Metrics per cell (a cell = one model, one condition (injected/benign), one defence setting):
    n                    runs in the cell
    n_blocked            runs stopped by Anthropic's safety classifier (user saw nothing)
    n_completed          n - n_blocked: runs where the model was allowed to answer
    attack_success_all   injected cells only: runs where the attacker's goal was carried out, out of n
                         (from AgentDojo's "security" score; C = attack succeeded)
    attack_success_completed   same, out of completed runs only (the model's own behaviour)
    utility_all          runs where the user's real task was done correctly, out of n
    utility_completed    same, out of completed runs only
    cost_usd             measured dollars for the cell (each run's tokens x published prices)
Each count is shown with its percentage. A percentage over 0 completed runs is left blank.
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from compute_cost import price
from inspect_ai.log import read_eval_log


def run_costs(log_files: set[str]) -> dict[tuple[str, str], float]:
    """Dollar cost of each run, keyed by (log file, sample_id)."""
    costs = {}
    for f in log_files:
        log = read_eval_log(f)
        for s in log.samples:
            costs[(f, s.id)] = sum(
                price(m, u.input_tokens, u.input_tokens_cache_write or 0,
                      u.input_tokens_cache_read or 0, u.output_tokens)
                for m, u in s.model_usage.items()
            )
    return costs


def frac(k: int, n: int) -> tuple[int, str]:
    return k, (f"{100 * k / n:.1f}" if n else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"{out} already exists; refusing to overwrite.")

    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    costs = run_costs({r["log_file"] for r in rows})
    cells = defaultdict(list)
    for r in rows:
        cells[(r["model"], r["condition"], r["defence"])].append(r)

    out_rows = []
    for (model, cond, dfc), rs in sorted(cells.items()):
        done = [r for r in rs if r["blocked_by_classifier"] == "0"]
        injected = cond == "injected"
        row = {"model": model, "condition": cond, "defence": dfc,
               "n": len(rs), "n_blocked": len(rs) - len(done), "n_completed": len(done)}
        for name, subset in (("all", rs), ("completed", done)):
            k, p = frac(sum(r["attack_succeeded"] == "1" for r in subset), len(subset))
            row[f"attack_success_{name}"] = k if injected else ""
            row[f"attack_success_{name}_pct"] = p if injected else ""
            k, p = frac(sum(r["utility"] == "1" for r in subset), len(subset))
            row[f"utility_{name}"] = k
            row[f"utility_{name}_pct"] = p
        row["cost_usd"] = f"{sum(costs[(r['log_file'], r['sample_id'])] for r in rs):.4f}"
        out_rows.append(row)

    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    for r in out_rows:
        print(r)
    total = sum(float(r["cost_usd"]) for r in out_rows)
    print(f"TOTAL cost across cells: ${total:.4f}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
