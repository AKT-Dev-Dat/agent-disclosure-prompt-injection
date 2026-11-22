"""Agreement between Aman's hand scores and the LLM grader on the human-check sample (build step 7).

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\compute_agreement.py

Reads results/human_check.csv (Aman's scores) and results/human_check_key.csv (grader's scores),
joined by check_id. ONLY rows with row_type = "sample" (check_id 1-30) are used. Rows 31-33
(row_type = "grader_failure") have no grader score, so there is nothing to agree with.

Writes results/human_agreement.csv (long format: one number per line) and prints it.

Metrics (explained so they can be defended in an interview):
    exact agreement   % of rows where Aman and the grader gave the identical answer.
    Cohen's kappa     agreement corrected for chance:  kappa = (p_o - p_e) / (1 - p_e)
                      p_o = observed agreement (the fraction above).
                      p_e = agreement you'd expect by luck if the two raters scored independently,
                            each keeping their own mix of answers: sum over categories of
                            (share of Aman's answers in that category) x (share of the grader's).
                      1 = perfect, 0 = no better than chance. With very lopsided data (almost all
                      answers in two categories that track the condition) p_e is high and kappa is
                      fragile: one disagreement can move it a lot.
    confusion counts  for every (grader score, Aman score) pair, how many rows. The diagonal is
                      agreement; off-diagonal cells show WHERE the two disagree.
    Legitimate caution is compared the same way, on BENIGN rows only (it is not asked on injected rows).
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "results" / "human_check.csv"
KEY = ROOT / "results" / "human_check_key.csv"
OUT = ROOT / "results" / "human_agreement.csv"


def cohens_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Cohen's kappa for two raters; pairs = [(grader, aman), ...]. None if undefined (p_e = 1)."""
    n = len(pairs)
    p_o = sum(g == a for g, a in pairs) / n
    g_counts, a_counts = Counter(g for g, _ in pairs), Counter(a for _, a in pairs)
    p_e = sum(g_counts[c] / n * a_counts[c] / n for c in set(g_counts) | set(a_counts))
    return None if p_e == 1 else (p_o - p_e) / (1 - p_e)


def main() -> None:
    sheet = {r["check_id"]: r for r in csv.DictReader(SHEET.open(encoding="utf-8-sig"))}
    key = {r["check_id"]: r for r in csv.DictReader(KEY.open(encoding="utf-8-sig"))}
    ids = [i for i in key if key[i]["row_type"] == "sample"]
    missing = [i for i in ids if sheet[i]["aman_score"] == ""
               or (sheet[i]["condition"] == "benign" and sheet[i]["aman_legitimate_caution"] == "")]
    if missing:
        raise SystemExit(f"Rows not yet hand-scored: {missing}")

    out = []

    def add(measure, n, n_agree, kappa, grader="", aman="", count=""):
        out.append({"measure": measure, "grader_value": grader, "aman_value": aman, "count": count,
                    "n_rows": n, "n_agree": n_agree,
                    "pct_agree": f"{100 * n_agree / n:.1f}" if n_agree != "" else "",
                    "cohens_kappa": "" if kappa in ("", None) else f"{kappa:.3f}"})

    for label, rows, g_field, a_field in (
            ("score", ids, "grader_score", "aman_score"),
            ("legitimate_caution (benign rows)", [i for i in ids if sheet[i]["condition"] == "benign"],
             "grader_legitimate_caution", "aman_legitimate_caution")):
        pairs = [(key[i][g_field], sheet[i][a_field]) for i in rows]
        n, n_agree = len(pairs), sum(g == a for g, a in pairs)
        add(f"{label}: summary", n, n_agree, cohens_kappa(pairs))
        # Confusion counts: every combination that can occur (0-3 for score; true/false for caution).
        values = ["0", "1", "2", "3"] if label == "score" else ["true", "false"]
        counts = Counter(pairs)
        for g in values:
            for a in values:
                add(f"{label}: confusion", "", "", "", g, a, counts[(g, a)])
        # Per-level agreement: of the rows the grader put at this level, how many Aman also put there.
        for g in values:
            n_g = sum(1 for p in pairs if p[0] == g)
            add(f"{label}: per grader level", n_g, counts[(g, g)] if n_g else "", "", g, g)

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)
    disagreements = [i for i in ids if key[i]["grader_score"] != sheet[i]["aman_score"]
                     or key[i]["grader_legitimate_caution"] != sheet[i]["aman_legitimate_caution"]]
    for i in disagreements:
        print(f"Disagreement on check_id {i} ({key[i]['sample_id']}, {key[i]['model']}, defence "
              f"{key[i]['defence']}): grader {key[i]['grader_score']}/{key[i]['grader_legitimate_caution']}"
              f" vs Aman {sheet[i]['aman_score']}/{sheet[i]['aman_legitimate_caution']}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
