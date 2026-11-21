"""Pilot summary: attack success, utility, classifier blocks and cost per model. Does NOT score disclosure.

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\summarize_pilot.py results\\pilot_transcripts.csv logs\\<pilot log folder>

Writes results/pilot_summary.csv and prints the same numbers.

Metrics (n = number of runs the percentage is calculated over):
    n_runs            runs for this model
    n_blocked         runs stopped by Anthropic's safety classifier (the user saw nothing)
    n_completed       runs NOT blocked = n_runs - n_blocked
    ASR_all           attack success rate = runs where the attacker's goal was carried out / n_runs
    ASR_completed     same, but only over completed (not blocked) runs. A blocked run can't succeed or
                      fail by the agent's choice, so this is the fairer measure of the MODEL's behaviour.
    utility_all       % of runs where the user's real task was done correctly (over all runs)
    utility_completed same, over completed runs only
    cost_total        measured dollars for this model's runs (token counts x published prices)
    cost_per_run      mean dollars per run, over all runs / over completed runs only. Completed runs
                      are the better guide to future cost, since blocked runs stop early and are cheap.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

from compute_cost import price  # same price table as compute_cost.py
from inspect_ai.log import read_eval_log


def pct(k: int, n: int) -> str:
    return f"{100 * k / n:.1f}" if n else ""


def per_sample_cost(log_paths: list[Path]) -> dict[tuple[str, str], float]:
    """Dollar cost of each individual run, keyed by (model, sample_id)."""
    costs = {}
    for f in log_paths:
        log = read_eval_log(str(f))
        for s in log.samples:
            total = 0.0
            for model, u in s.model_usage.items():
                total += price(model, u.input_tokens, u.input_tokens_cache_write or 0,
                               u.input_tokens_cache_read or 0, u.output_tokens)
            costs[(log.eval.model, s.id)] = total
    return costs


def main() -> None:
    csv_path, log_dir = Path(sys.argv[1]), Path(sys.argv[2])
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    costs = per_sample_cost(sorted(log_dir.rglob("*.eval")))

    by_model = defaultdict(list)
    for r in rows:
        r["cost"] = costs[(r["model"], r["sample_id"])]
        by_model[r["model"]].append(r)

    out_rows = []
    for model, rs in sorted(by_model.items()):
        done = [r for r in rs if r["blocked_by_classifier"] == "0"]
        n, nd = len(rs), len(done)
        succ_all = sum(r["attack_succeeded"] == "1" for r in rs)
        succ_done = sum(r["attack_succeeded"] == "1" for r in done)
        util_all = sum(r["utility"] == "1" for r in rs)
        util_done = sum(r["utility"] == "1" for r in done)
        cost_all = sum(r["cost"] for r in rs)
        cost_done = sum(r["cost"] for r in done)
        out_rows.append({
            "model": model, "n_runs": n, "n_blocked": n - nd, "n_completed": nd,
            "attacks_succeeded": succ_all,
            "ASR_all_pct": pct(succ_all, n), "ASR_completed_pct": pct(succ_done, nd),
            "utility_all_pct": pct(util_all, n), "utility_completed_pct": pct(util_done, nd),
            "n_utility_all": util_all, "n_utility_completed": util_done,
            "cost_total_usd": f"{cost_all:.4f}",
            "cost_per_run_all_usd": f"{cost_all / n:.5f}" if n else "",
            "cost_per_run_completed_usd": f"{cost_done / nd:.5f}" if nd else "",
        })

    out = Path("results/pilot_summary.csv")
    if out.exists():
        sys.exit(f"{out} already exists; refusing to overwrite.")
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    for r in out_rows:
        print(r)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
