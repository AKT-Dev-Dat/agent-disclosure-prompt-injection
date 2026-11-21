"""Draw the study's fixed random sample of (user task, injection task) pairs. Run ONCE, before the pilot.

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\draw_sample.py

Method (decision #12 in docs/02_decision_log.md):
    1. Read the list of workspace user tasks (40) and injection tasks (14) from the installed eval,
       so the IDs come from the benchmark itself, not typed by hand.
    2. Create ONE random number generator with seed 2026. A seed makes "random" choices repeatable:
       anyone running this script gets exactly the same sample.
    3. Choose 20 DIFFERENT user tasks out of the 40 (sampling without replacement).
    4. For each chosen user task, in the order drawn, choose 1 injection task out of the 14
       (with replacement, so two user tasks may share an injection task).
    No filtering and no hand-picking. Output: results/sample.csv (user_task_id, injection_task_id),
    in the order drawn.
"""
import csv
import random
import sys
from pathlib import Path

from inspect_evals.agentdojo.task_suites.workspace.task_suite import WORKSPACE_TASK_SUITE

SEED = 2026
N_USER_TASKS = 20
OUT = Path(__file__).resolve().parent.parent / "results" / "sample.csv"


def main() -> None:
    if OUT.exists():
        sys.exit(f"{OUT} already exists. The sample is fixed; refusing to redraw or overwrite it.")

    user_ids = sorted(int(i) for i in WORKSPACE_TASK_SUITE.user_tasks)
    injection_ids = sorted(int(i) for i in WORKSPACE_TASK_SUITE.injection_tasks)
    print(f"Workspace user tasks: {len(user_ids)} (IDs {user_ids[0]}-{user_ids[-1]})")
    print(f"Workspace injection tasks: {len(injection_ids)} (IDs {injection_ids[0]}-{injection_ids[-1]})")

    rng = random.Random(SEED)
    chosen_users = rng.sample(user_ids, N_USER_TASKS)
    pairs = [(u, rng.choice(injection_ids)) for u in chosen_users]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["user_task_id", "injection_task_id"])
        writer.writerows(pairs)

    print(f"Seed {SEED}. Wrote {len(pairs)} pairs to {OUT}:")
    for u, i in pairs:
        print(f"  user task {u:2d}  +  injection task {i:2d}")


if __name__ == "__main__":
    main()
