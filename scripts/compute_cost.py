"""Measured token use and dollar cost from Inspect .eval logs, per log and per model.

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\compute_cost.py <log folder or .eval file> [...]

Terms used:
    input tokens        new text sent to the model (about 3/4 of a word per token)
    cache write         text sent for the first time and stored by Anthropic for re-use (prompt
                        caching; Inspect turns it on by default). Costs slightly more than input.
    cache read          stored text re-used on a later call. Costs about 1/20 to 1/10 of input.
    output tokens       text the model writes, INCLUDING its hidden reasoning (billed as output)
    reasoning tokens    the hidden-thinking part of output (already inside output; not added again)
    cost                sum of each token type x its price. This is the actual measured spend.
    cost_per_run        cost / number of runs (samples) - used to estimate future batches.
"""
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

# USD per million tokens: (input, cache write 5-minute, cache read, output).
# Source: platform.claude.com/docs/en/about-claude/pricing, read 21 Nov 2026. Update if prices change.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.125, 0.01, 0.50),
    "claude-opus-5-5": (4.00, 5.00, 0.20, 20.00),
}


def price(model: str, inp: int, cache_write: int, cache_read: int, out: int) -> float:
    """Dollar cost of a token mix for one model."""
    p_in, p_cw, p_cr, p_out = PRICES[model.split("/")[-1]]
    return (inp * p_in + cache_write * p_cw + cache_read * p_cr + out * p_out) / 1_000_000


def find_logs(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        files.extend(sorted(p.rglob("*.eval")) if p.is_dir() else [p])
    return files


def usage_by_model(paths: list[str]) -> dict[str, dict[str, int]]:
    """Add up tokens and runs per model across all the logs given."""
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for f in find_logs(paths):
        log = read_eval_log(str(f), header_only=True)
        n_runs = log.results.total_samples if log.results else 0
        for model, u in log.stats.model_usage.items():
            t = totals[model]
            t["runs"] += n_runs
            t["input"] += u.input_tokens
            t["cache_write"] += u.input_tokens_cache_write or 0
            t["cache_read"] += u.input_tokens_cache_read or 0
            t["output"] += u.output_tokens
            t["reasoning"] += u.reasoning_tokens or 0
            t["total"] += u.total_tokens
    return totals


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    totals = usage_by_model(sys.argv[1:])
    grand = 0.0
    for model, t in sorted(totals.items()):
        cost = price(model, t["input"], t["cache_write"], t["cache_read"], t["output"])
        grand += cost
        per_run = cost / t["runs"] if t["runs"] else float("nan")
        print(f"{model}: runs={t['runs']} input={t['input']} cache_write={t['cache_write']} "
              f"cache_read={t['cache_read']} output={t['output']} (reasoning={t['reasoning']}) "
              f"total_tokens={t['total']}")
        print(f"    cost=${cost:.4f}  cost_per_run=${per_run:.5f}  "
              f"tokens_per_run={t['total'] / t['runs'] if t['runs'] else float('nan'):.0f}")
    print(f"TOTAL cost: ${grand:.4f}")


if __name__ == "__main__":
    main()
