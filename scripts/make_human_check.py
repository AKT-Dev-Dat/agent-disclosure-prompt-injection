"""Build Aman's blind human-check sheet: 30 graded runs, stratified by grader score (build step 6).

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\make_human_check.py

Outputs:
    results/human_check.csv      what Aman scores. Columns: check_id, sample_id, condition,
                                 visible_messages, injected_goal, aman_score (EMPTY),
                                 aman_legitimate_caution (EMPTY). No grader scores, no model, no defence.
    results/human_check_key.csv  the grader's answers for the same 30 rows, joined by check_id.
                                 Open it only AFTER scoring, so the check stays blind.

Why check_id: the same sample_id (e.g. workspace-u7-i10) was run on both models and both defence
settings, so sample_id alone does not identify a run. check_id (1-30) does.

Sampling method (decision #11: "sampled by grader score so every level (0-3) is covered"):
    1. Use only runs the grader scored (grader failures are excluded).
    2. Split 30 as evenly as possible across the score levels that actually occur. If a level has fewer
       runs than its share, take all of them and give the spare places to the other levels, evenly.
    3. Within each level, use a random generator with seed 2026 (a fresh one per level): shuffle the runs
       of each model x condition group, then take one from each group in turn (round robin), so both
       models and both conditions are covered wherever that level contains them.
    4. Shuffle the final 30 (seed 2026) so the row order does not reveal the grader's score.
"""
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCORES = ROOT / "results" / "disclosure_scores.csv"
TRANSCRIPTS = ROOT / "results" / "all_transcripts.csv"
OUT = ROOT / "results" / "human_check.csv"
KEY = ROOT / "results" / "human_check_key.csv"
N, SEED = 30, 2026


def run_key(r: dict) -> tuple:
    """A run is identified by sample_id + model + defence (sample_id alone repeats across cells)."""
    return r["sample_id"], r["model"], r["defence"]


def allocate(sizes: dict[int, int], total: int) -> dict[int, int]:
    """Split `total` places across levels as evenly as possible, capped by how many runs each level has."""
    quota = {lvl: 0 for lvl in sizes}
    remaining = min(total, sum(sizes.values()))
    while remaining:
        open_levels = sorted(l for l in sizes if quota[l] < sizes[l])
        share, extra = divmod(remaining, len(open_levels))
        for i, lvl in enumerate(open_levels):
            give = min(share + (1 if i < extra else 0), sizes[lvl] - quota[lvl])
            quota[lvl] += give
            remaining -= give
    return quota


def main() -> None:
    for p in (OUT, KEY):
        if p.exists():
            sys.exit(f"{p} already exists; refusing to overwrite.")
    from inspect_evals.agentdojo.task_suites.workspace.task_suite import WORKSPACE_TASK_SUITE
    goals = {str(int(k)): t.GOAL for k, t in WORKSPACE_TASK_SUITE.injection_tasks.items()}

    transcripts = {run_key(r): r for r in csv.DictReader(TRANSCRIPTS.open(encoding="utf-8-sig"))}
    graded = [r for r in csv.DictReader(SCORES.open(encoding="utf-8-sig")) if r["score"] != ""]

    by_level = defaultdict(list)
    for r in graded:
        by_level[int(r["score"])].append(r)
    quota = allocate({lvl: len(rs) for lvl, rs in by_level.items()}, N)
    print("Runs per grader score level:", {l: len(by_level[l]) for l in sorted(by_level)})
    print("Chosen per level:", {l: quota[l] for l in sorted(quota)})

    chosen = []
    for lvl in sorted(by_level):
        rng = random.Random(SEED)
        groups = defaultdict(list)
        for r in sorted(by_level[lvl], key=run_key):
            groups[(r["model"], r["condition"])].append(r)
        for g in groups.values():
            rng.shuffle(g)
        order = sorted(groups)
        picked, i = [], 0
        while len(picked) < quota[lvl]:
            g = groups[order[i % len(order)]]
            if g:
                picked.append(g.pop())
            i += 1
        chosen.extend(picked)

    random.Random(SEED).shuffle(chosen)

    sheet, key = [], []
    for check_id, r in enumerate(chosen, 1):
        t = transcripts[run_key(r)]
        visible = json.loads(t["visible_messages"])
        n = len(visible)
        text = "\n\n".join(f"--- Message {i} of {n}{' (final message)' if i == n else ''} ---\n{m}"
                           for i, m in enumerate(visible, 1)) or "(no visible text)"
        sheet.append({"check_id": check_id, "sample_id": r["sample_id"], "condition": r["condition"],
                      "visible_messages": text,
                      "injected_goal": goals[t["injection_task_id"]] if r["condition"] == "injected" else "",
                      "aman_score": "", "aman_legitimate_caution": ""})
        key.append({"check_id": check_id, "sample_id": r["sample_id"], "model": r["model"],
                    "condition": r["condition"], "defence": r["defence"], "grader_score": r["score"],
                    "grader_warning_in_final_message": r["warning_in_final_message"],
                    "grader_legitimate_caution": r["legitimate_caution"],
                    "grader_evidence_quote": r["evidence_quote"], "grader_reason": r["reason"]})

    for path, rows in ((OUT, sheet), (KEY, key)):
        with path.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    cover = defaultdict(int)
    for k in key:
        cover[(k["model"].split("/")[-1], k["condition"], k["grader_score"])] += 1
    print("Coverage (model, condition, grader score): count")
    for c in sorted(cover):
        print("  ", c, cover[c])
    print(f"Wrote {OUT} and {KEY}")


if __name__ == "__main__":
    main()
