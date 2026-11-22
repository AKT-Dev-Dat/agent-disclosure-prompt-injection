"""The study's one figure: results/main_figure.png (Prompt 5 B.4).

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\make_figure.py

Reads results/summary_table.csv (made by scripts/make_summary_table.py); every number drawn comes
from that file. Built to read in black and white: each category has its own grey level AND hatch
pattern, and every segment carries its count.

Left panel (INJECTED runs only), one stacked bar per model x defence, 20 runs each. Each run falls
into exactly one outcome:
    attack succeeded                              AgentDojo security = C
    blocked by API classifier (user told nothing) the API refused mid-task; no answer, no warning
    completed, specific warning                   run finished; disclosure score 3
    completed, no/weak warning                    run finished; disclosure score 0, 1 or 2
Right panel: task completion (utility = AgentDojo says the user's task was done), injected vs
benign, per model, pooled over both defence settings (40 runs per bar). Blocked runs count as not done.
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "results" / "summary_table.csv"
OUT = ROOT / "results" / "main_figure.png"

MODEL_NAME = {"claude-haiku-5-5": "Haiku 5.5", "claude-opus-5-5": "Opus 5.5"}
# (column in summary_table.csv, legend label, fill grey, hatch, text colour on the fill)
CATEGORIES = [
    ("attack_succeeded", "Attack succeeded", "#000000", "", "white"),
    ("n_blocked", "Blocked by API classifier (user told nothing)", "#595959", "///", "white"),
    ("completed_specific_warning", "Completed, specific warning", "#d9d9d9", "", "black"),
    ("completed_no_or_weak_warning", "Completed, no/weak warning", "#ffffff", "..", "black"),
]


def main() -> None:
    rows = list(csv.DictReader(TABLE.open(encoding="utf-8")))
    injected = [r for r in rows if r["condition"] == "injected"]
    injected.sort(key=lambda r: (r["model"], r["defence"]))

    plt.rcParams.update({"font.size": 10, "hatch.linewidth": 0.8, "hatch.color": "#000000"})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.6), gridspec_kw={"width_ratios": [2.2, 1]})
    fig.suptitle("Where the safety signal is lost", fontsize=14, fontweight="bold")

    # Left: stacked outcome counts for injected runs.
    labels = [f"{MODEL_NAME[r['model']]}\ndefence: {r['defence']}" for r in injected]
    x = range(len(injected))
    bottoms = [0] * len(injected)
    for col, label, grey, hatch, ink in CATEGORIES:
        vals = [int(r[col]) for r in injected]
        ax1.bar(x, vals, bottom=bottoms, width=0.6, color=grey, hatch=hatch, edgecolor="black",
                linewidth=0.8, label=label)
        for i, v in enumerate(vals):
            if v:
                ax1.text(i, bottoms[i] + v / 2, str(v), ha="center", va="center", color="black",
                         fontsize=10, fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax1.set_xticks(list(x), labels)
    ax1.set_ylabel("Number of injected runs (20 per bar)")
    ax1.set_ylim(0, 20)
    ax1.set_yticks(range(0, 21, 5))
    # Categories that are 0 in every bar have no visible segment; say so in the title.
    zero = [label for col, label, *_ in CATEGORIES if all(int(r[col]) == 0 for r in injected)]
    note = ("\n(0 in every bar: " + "; ".join(z.lower() for z in zero) + ")") if zero else ""
    ax1.set_title("Injected runs: what happened" + note, fontsize=11)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=9)

    # Right: utility, injected vs benign, per model (pooled over defence settings).
    done, total = defaultdict(int), defaultdict(int)
    for r in rows:
        done[(r["model"], r["condition"])] += int(r["utility"])
        total[(r["model"], r["condition"])] += int(r["n_runs"])
    models = sorted(MODEL_NAME)
    width = 0.36
    for j, (cond, grey, hatch) in enumerate((("injected", "#a6a6a6", "xx"), ("benign", "#ffffff", ""))):
        xs = [i + (j - 0.5) * width for i in range(len(models))]
        pcts = [100 * done[(m, cond)] / total[(m, cond)] for m in models]
        ax2.bar(xs, pcts, width=width, color=grey, hatch=hatch, edgecolor="black", linewidth=0.8,
                label=cond.capitalize())
        for xx, p, m in zip(xs, pcts, models):
            ax2.text(xx, p + 1.5, f"{done[(m, cond)]}/{total[(m, cond)]}", ha="center", va="bottom", fontsize=9)
    ax2.set_xticks(range(len(models)), [MODEL_NAME[m] for m in models])
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Task completed (%)")
    ax2.set_title("Task completion (utility)\nboth defence settings pooled", fontsize=11)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=9)

    fig.text(0.01, 0.005, "Source: results/summary_table.csv. AgentDojo workspace suite, 20 sampled tasks, "
             "'important_instructions' attack, Nov 2026.", fontsize=7.5, color="#333333")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(OUT, dpi=200)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
