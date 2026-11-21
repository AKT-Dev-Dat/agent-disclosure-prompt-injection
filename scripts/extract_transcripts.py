"""Turn Inspect .eval logs into one CSV row per sample (one agent run).

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\extract_transcripts.py <log folder or .eval file> [...] --out results\\file.csv

Columns written (one row per run):
    log_file               which .eval log the row came from
    sample_id              AgentDojo's ID, e.g. "workspace-u0-i0" (user task 0 + injection task 0)
    model                  e.g. anthropic/claude-haiku-5-5
    condition              "injected" (attack present) or "benign" (injections off)
    defence                "none", or "report-instruction" if --system-message was used
    system_message_added   the exact extra system message, if any (empty if none)
    user_task_id           the legitimate task the user asked for (0-39 in workspace)
    injection_task_id      the attacker's goal (0-13 in workspace); empty for benign runs
    attack_succeeded       METRIC INPUT for attack success rate (ASR).
                           Comes from AgentDojo's "security" score. WARNING: the name is misleading.
                           security = "C" means the attacker's goal WAS carried out, so we write
                           attack_succeeded = 1. security = "I" means it was not -> 0.
                           (Evidence: notes/step1_report.md, section 4.) Empty for benign runs.
    utility                METRIC INPUT for utility: 1 if the user's real task was done correctly
                           (AgentDojo's rule-based check on the final state), else 0.
    n_visible_messages     how many agent messages contained text the user could read
    visible_messages       all those messages, in order, as a JSON list of strings
    final_visible_message  the last message with readable text: what the user sees at the end
    has_hidden_reasoning   1 if the model produced hidden "thinking" (encrypted, not scored), else 0
    error                  error text if the run crashed, else empty

"Visible" means the text parts of the agent's (assistant's) messages. Hidden reasoning and tool
calls are not visible text, so they are left out. This follows decision #10 and Part 3 of
docs/02_decision_log.md (only visible messages are scored).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from inspect_ai.log import read_eval_log
from inspect_ai.model import ContentReasoning, ContentText

COLUMNS = [
    "log_file", "sample_id", "model", "condition", "defence", "system_message_added",
    "user_task_id", "injection_task_id", "attack_succeeded", "utility",
    "n_visible_messages", "visible_messages", "final_visible_message",
    "has_hidden_reasoning", "error",
]


def find_logs(paths: list[str]) -> list[Path]:
    """Accept folders and/or .eval files; return every .eval file, sorted by name (= by time)."""
    files: list[Path] = []
    for p in map(Path, paths):
        files.extend(sorted(p.rglob("*.eval")) if p.is_dir() else [p])
    return files


def split_content(content) -> tuple[str, bool]:
    """Return (visible text, whether hidden reasoning was present) for one message."""
    if isinstance(content, str):
        return content.strip(), False
    texts = [part.text for part in content if isinstance(part, ContentText)]
    reasoning = any(isinstance(part, ContentReasoning) for part in content)
    return "\n".join(t for t in texts if t).strip(), reasoning


def c_to_int(value) -> int | str:
    """AgentDojo scores are "C" (correct/true) or "I" (incorrect/false). Convert to 1 / 0."""
    return {"C": 1, "I": 0}.get(value, "")


def rows_from_log(path: Path):
    log = read_eval_log(str(path))
    system_message = log.plan.config.system_message or ""
    for sample in log.samples or []:
        visible, reasoning_seen = [], False
        for msg in sample.messages:
            if msg.role != "assistant":
                continue
            text, has_reasoning = split_content(msg.content)
            reasoning_seen = reasoning_seen or has_reasoning
            if text:
                visible.append(text)

        score = next(iter(sample.scores.values())).value if sample.scores else {}
        injected = "injection_task_id" in sample.metadata
        yield {
            "log_file": path.as_posix(),
            "sample_id": sample.id,
            "model": log.eval.model,
            "condition": "injected" if injected else "benign",
            "defence": "report-instruction" if system_message else "none",
            "system_message_added": system_message,
            "user_task_id": sample.metadata.get("task_id", ""),
            "injection_task_id": sample.metadata.get("injection_task_id", ""),
            # security "C" = attack succeeded (see docstring). Benign runs have no security score.
            "attack_succeeded": c_to_int(score.get("security")) if injected else "",
            "utility": c_to_int(score.get("utility")),
            "n_visible_messages": len(visible),
            "visible_messages": json.dumps(visible, ensure_ascii=False),
            "final_visible_message": visible[-1] if visible else "",
            "has_hidden_reasoning": int(reasoning_seen),
            "error": sample.error.message if sample.error else "",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("logs", nargs="+", help="log folder(s) or .eval file(s)")
    parser.add_argument("--out", required=True, help="CSV file to write")
    args = parser.parse_args()

    out = Path(args.out)
    if out.exists():
        sys.exit(f"{out} already exists; refusing to overwrite.")
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = [row for f in find_logs(args.logs) for row in rows_from_log(f)]
    # utf-8-sig so Excel shows accented characters and dashes correctly.
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
