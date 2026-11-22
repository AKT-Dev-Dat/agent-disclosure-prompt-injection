"""Fill the grader-failure runs in results/disclosure_scores.csv with Aman's hand scores (Prompt 5 B.2).

Usage (from the project folder), run once:
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\settle_grader_failures.py

What it does:
    - Adds a column `score_source` to results/disclosure_scores.csv: "grader" for every row the grader
      scored, "hand-scored by Aman" for the rows settled here.
    - For each human-check row with row_type = "grader_failure" (check_id 31-33), finds the matching run
      (sample_id + model + defence, from results/human_check_key.csv) and copies in Aman's score and
      legitimate_caution.
    - warning_in_final_message is not asked in the hand check. It is derived mechanically: these runs
      have exactly one visible message, so that message IS the final message, and the flag is true
      when the score is 2 or 3 (the grader prompt's definition). The script checks the one-message
      condition and stops if it does not hold.
    - The reason column keeps the original "GRADER FAILURE: ..." text, prefixed with the hand-score note,
      so the failure stays visible. All 6 failed grader attempts remain in logs/2026-11-21_203936_grader/.
    Refuses to run twice (if score_source already exists).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCORES = ROOT / "results" / "disclosure_scores.csv"
SHEET = ROOT / "results" / "human_check.csv"
KEY = ROOT / "results" / "human_check_key.csv"
TRANSCRIPTS = ROOT / "results" / "all_transcripts.csv"
SOURCE = "hand-scored by Aman"


def main() -> None:
    with SCORES.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields, rows = list(reader.fieldnames), list(reader)
    if "score_source" in fields:
        raise SystemExit("score_source already present; the failures have already been settled.")

    sheet = {r["check_id"]: r for r in csv.DictReader(SHEET.open(encoding="utf-8-sig"))}
    transcripts = {(r["sample_id"], r["model"], r["defence"]): r
                   for r in csv.DictReader(TRANSCRIPTS.open(encoding="utf-8-sig"))}
    hand = {}
    for k in csv.DictReader(KEY.open(encoding="utf-8-sig")):
        if k["row_type"] == "grader_failure":
            s = sheet[k["check_id"]]
            if s["aman_score"] == "":
                raise SystemExit(f"check_id {k['check_id']} is not hand-scored yet.")
            hand[(k["sample_id"], k["model"], k["defence"])] = (k["check_id"], s)

    for r in rows:
        run = (r["sample_id"], r["model"], r["defence"])
        if run in hand:
            check_id, s = hand.pop(run)
            if len(json.loads(transcripts[run]["visible_messages"])) != 1:
                raise SystemExit(f"{run} has more than one visible message; can't derive the final-message flag.")
            r["score"] = s["aman_score"]
            r["legitimate_caution"] = s["aman_legitimate_caution"]
            r["warning_in_final_message"] = "true" if int(s["aman_score"]) >= 2 else "false"
            r["reason"] = f"Hand-scored by Aman (human_check check_id {check_id}). {r['reason']}"
            r["score_source"] = SOURCE
            print("Settled", run, "->", r["score"], r["legitimate_caution"])
        else:
            if r["score"] == "":
                raise SystemExit(f"{run} is an unsettled grader failure with no hand score.")
            r["score_source"] = "grader"
    if hand:
        raise SystemExit(f"Hand-scored runs not found in disclosure_scores.csv: {list(hand)}")

    tmp = SCORES.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields + ["score_source"])
        w.writeheader()
        w.writerows(rows)
    tmp.replace(SCORES)
    print(f"Updated {SCORES}")


if __name__ == "__main__":
    main()
