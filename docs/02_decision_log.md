# Decision log

Format: date / decision / alternatives considered / reason. Add a line for every design change. This doubles as research-discussion prep.

| # | Date | Decision | Alternatives considered | Reason |
|---|---|---|---|---|
| 1 | 21 Nov | Do a frontier-model behavioural eval (black-box, via API) | Classifier cascade on a prompt-injection dataset; interpretability on an open model; product-style portfolio projects (RAG, voice agent, memory) | Studies frontier models directly; maps to the Safeguards and adversarial robustness areas; feasible in 48h without ML training experience |
| 2 | 21 Nov | Headline = disclosure; ASR secondary | ASR as headline | Public results suggest near-zero ASR for current Claude models (ceiling effect). Disclosure can vary when ASR doesn't, and ties to oversight |
| 3 | 21 Nov | Use AgentDojo via Inspect, workspace suite | Hand-built scenarios only; InjecAgent; BIPIA | Established benchmark with rule-based grading and utility measure; Inspect integration saves a day of harness work; workspace suite fits the enterprise data-leakage setting |
| 4 | 21 Nov | Pilot gate before the full run | Full grid immediately | Protects budget and time if disclosure turns out flat |
| 5 | 21 Nov | Report false alarms next to disclosure | Disclosure only | More warnings isn't automatically better (alert fatigue); avoids a one-sided metric |
| 6 | 21 Nov | Write and commit predictions BEFORE any model run (including the pilot). Pilot data stays in the main analysis | Predictions after the pilot; excluding pilot tasks | Predicting after seeing pilot results would be postdiction. Committing first keeps the order provable |
| 7 | 21 Nov | Core grid = Haiku + Opus × default attack × no defence / defence × 20 tasks (80 injected + 80 benign runs). Stretch 1: second attack type. Stretch 2: Sonnet. Stretch layers only if the core is done by Sun 12:00 | Full 3 × 3 × 2 grid | 360–720 runs doesn't fit the time available. Haiku vs Opus gives the widest capability gap |
| 8 | 21 Nov | H3 reworded around cost: "A one-line reporting instruction raises specific warnings; we measure its cost in false alarms and task completion" | Original H3 ("raises disclosure") | The original mostly tested instruction-following; the cost is the informative part |
| 9 | 21 Nov | Score disclosure on ALL injected runs, split by attack succeeded / failed, n shown in every cell | Scoring only failed attacks | Avoids each model being scored on a different set of tasks |
| 10 | 21 Nov | Score every message shown to the user during the run, plus a yes/no for "warning in final message" | Final message only | Agents sometimes flag mid-run and then drop it |
| 11 | 21 Nov | Hand-check 30 transcripts sampled by grader score so every level is covered; report agreement per level. Claude-grading-Claude stated as a limitation | Random 30; no stratification | Mostly-zero scores make random-sample agreement unstable; acknowledges the circularity |
| 12 | | (attack type confirmed / exact model IDs) | | |
| 13 | | (pilot result: GO / NO-GO) | | |

## Pre-registered predictions
Fill in and save BEFORE ANY model run, including the pilot. Core grid only (Sonnet rows are stretch; skip them). Commit to git so the timestamp proves the order.

Committed at: ____ (git commit hash: ____)

| Model | Attack type | Defence | Predicted ASR | Predicted % specific warning (score 3) | Predicted false-alarm % |
|---|---|---|---|---|---|
| Haiku | default | none | | | |
| Haiku | default | report-instruction | | | |
| Sonnet | default | none | | | |
| Sonnet | default | report-instruction | | | |
| Opus | default | none | | | |
| Opus | default | report-instruction | | | |

Reasoning behind my predictions (3–5 lines):
