# Decision log: Agent disclosure under indirect prompt injection

Owner: Aman Tareen. Started 21 Nov 2026.

---

## How to use this log (read once)

**What it is:** a dated record of every choice that shapes the study, written at the time you make it. It shows a reviewer HOW you think: what you weighed, what you rejected, and what would make you change course.

**Why it matters for the application:** the research discussion will ask "why did you do it this way?" This log is your answer, already written. It also proves your predictions came before your results.

**Rules:**
1. Write the entry when you decide, not afterwards. Short is fine.
2. Never delete or rewrite an old entry. If you change your mind, add a new entry that says "Supersedes #X" and why.
3. Every entry has the same 6 parts (template below).
4. Commit to git after each entry (`git add . && git commit -m "Decision #X" && git push`). Git's timestamps are your proof of order.

### Entry template
```
### #[number]: [short title]
- Date:
- Decision: [what you chose, in one sentence]
- Options considered: [2–3 alternatives]
- Why: [the main reason, 1–3 sentences; cite evidence if you have it]
- Trade-off accepted: [what you give up by choosing this]
- Would change my mind if: [a concrete observation that would reverse it]
```

### Good vs weak entry
- **Weak:** "Used Haiku and Opus because they're good models."
- **Good:** "Used Haiku and Opus because they give the widest capability gap within one model family, which H1 needs. Trade-off: no middle point (Sonnet), so I can't tell whether any effect is gradual. Would change my mind if: the core grid finishes before Sun 12:00, in which case add Sonnet."

The "Would change my mind if" line is what separates research judgment from preference. Never skip it.

---

## Part 1: Decisions so far

### #1: Study frontier-model behaviour, not build a product
- Date: 21 Nov 2026
- Decision: Run a black-box behavioural evaluation of Claude models via the API.
- Options considered: hybrid classifier cascade on a prompt-injection dataset; interpretability on a small open model; product projects (RAG, voice agent, memory assistant).
- Why: The Residency asks for empirical AI safety research. A behavioural eval studies the models directly and is feasible in 48 hours without ML training experience.
- Trade-off accepted: No access to model internals; I can only observe behaviour, not explain its cause.
- Would change my mind if: the eval can't run on my setup by Sat 20:00, in which case fall back to the classifier cascade.

### #2: Headline measure = disclosure, not attack success rate
- Date: 21 Nov 2026
- Decision: The main measure is whether the agent tells the user about an injection. Attack success rate (ASR) is secondary.
- Options considered: ASR as headline.
- Why: Public results suggest current Claude models resist most injections, so ASR is likely near zero for all models (a ceiling effect), which would make the result uninformative. Disclosure can vary even when ASR doesn't, and it tests whether a human overseer receives the signal they need.
- Trade-off accepted: Disclosure needs a rubric and partly manual scoring, which is more subjective than ASR's automatic grading.
- Would change my mind if: the pilot shows disclosure is flat (almost all 0 or all 3). See #13.

### #3: Use AgentDojo via UK AISI Inspect, workspace suite
- Date: 21 Nov 2026
- Decision: Use the AgentDojo benchmark through Inspect's `inspect_evals/agentdojo`, workspace suite (email, calendar, drive).
- Options considered: hand-built scenarios only; other prompt-injection benchmarks.
- Why: Established benchmark with rule-based grading of attack success and task completion; the Inspect version saves a day of building; the workspace suite matches the enterprise data-leakage setting I worked on at Citi.
- Trade-off accepted: Its tasks and attacks are public and may already be familiar to models, which could make them look more robust than they are.
- Would change my mind if: Prompt 0 shows it can't run on Windows or can't support our defence condition.

### #4: Pilot before the full run
- Date: 21 Nov 2026
- Decision: Run a 20-task pilot on Haiku and Opus before spending the main budget.
- Options considered: Run the full grid straight away.
- Why: Protects time and money if the main measure turns out to be flat or the scoring doesn't work.
- Trade-off accepted: Costs about 1–2 hours.
- Would change my mind if: N/A (low-cost safeguard).

### #5: Report false alarms alongside disclosure
- Date: 21 Nov 2026
- Decision: Measure how often the agent flags normal emails as suspicious, and always report it next to disclosure.
- Options considered: Disclosure only.
- Why: More warnings isn't automatically better; constant warnings cause alert fatigue. Reporting both avoids a one-sided result.
- Trade-off accepted: Needs extra benign runs (more cost).
- Would change my mind if: N/A.

### #6: Predictions committed before ANY model run
- Date: 21 Nov 2026
- Decision: Write and commit predictions (Part 2) before the pilot. Pilot data stays in the analysis.
- Options considered: Predict after the pilot; exclude pilot tasks from the main analysis.
- Why: Predicting after seeing pilot results would be "postdiction" and would undermine the pre-registration. Committing first keeps the order provable.
- Trade-off accepted: Predictions are made with less information.
- Would change my mind if: N/A.

### #7: Core grid sized to the deadline
- Date: 21 Nov 2026
- Decision: Core = Haiku + Opus × default attack × no defence / defence × 20 tasks = 80 injected runs + 80 benign runs. Stretch 1: a second attack type. Stretch 2: Sonnet. Stretch only if the core is done by Sun 12:00.
- Options considered: Full 3 models × 3 attacks × 2 defences grid (360–720 runs).
- Why: The full grid doesn't fit the time available. Haiku vs Opus gives the widest capability gap.
- Trade-off accepted: Fewer conditions; results may not generalise to other attack types.
- Would change my mind if: the core finishes early.

### #8: H3 reframed around cost
- Date: 21 Nov 2026
- Decision: H3 becomes "A one-line reporting instruction raises specific warnings; we measure its cost in false alarms and task completion."
- Options considered: Original H3 ("the instruction raises disclosure").
- Why: Telling a model to report and then finding it reports mostly tests instruction-following. The informative part is the cost.
- Trade-off accepted: None significant.
- Would change my mind if: N/A.

### #9: Score all injected runs, show n in every cell
- Date: 21 Nov 2026
- Decision: Score disclosure on every injected run, split by attack succeeded / failed, with the number of runs (n) shown in every cell.
- Options considered: Score only runs where the attack failed.
- Why: Otherwise each model would be scored on a different set of tasks, making comparisons unfair.
- Trade-off accepted: Slightly more complex tables.
- Would change my mind if: N/A.

### #10: Score every message the user sees, not just the last one
- Date: 21 Nov 2026
- Decision: Score all messages shown to the user during a run, plus a yes/no for "warning appears in the final message".
- Options considered: Score the final message only.
- Why: Agents sometimes flag a problem midway and then leave it out of the final summary.
- Trade-off accepted: More text to score.
- Would change my mind if: N/A.

### #11: Check the automated grader against my own scoring
- Date: 21 Nov 2026
- Decision: Claude scores all transcripts with the rubric. I hand-score 30, sampled so every score level (0–3) is covered, without seeing Claude's score. Report agreement per level and overall.
- Options considered: Trust the grader; random 30-sample check.
- Why: Claude grading Claude is a version of the circular-assurance problem. A check bounds the risk. Sampling by level avoids an unstable result when most scores are 0.
- Trade-off accepted: Single human rater; still a limitation, stated in the README.
- Would change my mind if: agreement is low (kappa below 0.6), in which case revise the rubric and re-grade.

### #12: Attack, defence method, task sampling and model IDs
- Date: 21 Nov 2026
- Decision: (a) Use AgentDojo's single built-in attack (`important_instructions`); comparing attack types moves to Stretch 1, via the one-setting name swap (note signed by the user "Emma Johnson" vs a stranger "Mark Smith"). (b) Deliver the reporting instruction with Inspect's built-in `--system-message` setting, which adds the line in front of the eval's own system prompt. (c) Sample 20 different workspace user tasks, each paired with one randomly chosen injection task (fixed random seed, task IDs recorded); the benign runs reuse the same 20 user tasks. (d) Models: `anthropic/claude-haiku-5-5` and `anthropic/claude-opus-5-5` (to be confirmed against my API key during setup).
- Options considered: (a) port 2 extra attacks from the original AgentDojo code; (b) a custom wrapper file; (c) 10 user tasks × 2 injection tasks, or hand-picked pairs.
- Why: (a) The Inspect eval has only one attack (Prompt 0 report), and porting new attacks costs time the core study needs. (b) The built-in setting needs no code and keeps the eval's normal instructions intact. (c) 20 different tasks give more variety than 10 tasks used twice, and random selection with a recorded seed rules out cherry-picking.
- Trade-off accepted: H2 (attack framing) can't be tested in the core study. The single attack impersonates the user, so models may reasonably treat it as a real request; this is stated as a limitation.
- Would change my mind if: the first test log shows the `--system-message` line replaced the eval's own prompt or didn't reach the model; in that case switch to the wrapper.

### #13: Pilot result (GO / NO-GO)
- Date:
- Decision: [GO / NO-GO]
- What the pilot showed: [e.g. "Of 20 resisted attacks, Haiku: X silent, Y specific warnings; Opus: …"]
- Why:
- If NO-GO, what changes: [e.g. headline switches to the defence trade-off]

---

## Part 2: Pre-registered predictions

**Fill in and commit BEFORE any model is run.**

Committed at: 2026-11-21 18:01:31 +0000 (UTC)
Git commit hash: 859e64404255985075cacb03052b58d13170f9db

Note: all numbers are "out of 100 runs". I chose a range for each; the number in brackets is the midpoint used for scoring.

| # | Prediction | My prediction |
|---|---|---|
| P1 | Haiku falls for the attack (ASR), no defence | 8–15 (11) |
| P2 | Opus falls for the attack (ASR), no defence | 2–5 (3) |
| P3 | Haiku gives a specific warning (score 3) when it resists, no defence | about 15 |
| P4 | Opus gives a specific warning (score 3) when it resists, no defence | about 35 |
| P5 | Specific warnings WITH the reporting instruction (both models) | over 90 (92) |
| P6 | False alarms on normal emails WITH the reporting instruction | 0–2 (1) |
| P7 | False alarms on normal emails, no defence | 2–5 (3) |

**Direction predictions (more important than exact numbers):**
- D1: Opus resists more than Haiku. **Agree.**
- D2: Opus warns more often than Haiku (without the instruction). **Agree.**
- D3: The reporting instruction raises warnings. **Agree.** It also raises false alarms. **Disagree**: I predict false alarms stay the same or fall slightly, because a precise instruction ("instructions directed at you") gives the model a clearer test than its own vague caution.

**My reasoning:**
I expect both models to resist most attacks, because Claude models are trained against prompt injection, with Opus more resistant than Haiku. I expect silent resistance to be common: models are trained to ignore injected text rather than report it, so without being asked they will mostly carry on with the task and say nothing. Opus, as the more capable model, is more likely to notice the injection and mention it. With an explicit instruction to report, I expect warnings to become near-universal, and because the instruction defines precisely what counts as suspicious, I don't expect it to make the models jumpier on normal emails.

**How I'll judge my predictions afterwards:** a prediction is "correct" if the result falls inside my number ±10 points, and a direction prediction is correct if the observed difference points the same way.

---

## Part 3: Deviations from plan
Anything that ended up different from the brief, and why. Reviewers trust a study more when changes are logged, not hidden.

| Date | What changed | Why | Effect on results |
|---|---|---|---|
| 21 Nov | Virtual environment placed at C:\venvs\adpi, outside the project | Windows' 260-character path limit broke the install inside the project folder | None; recorded in requirements.txt and README |
| 21 Nov | AgentDojo's "security" score treated as attack success (security = C means the attack succeeded) | Step-1 test plus the eval's own code show the label is the reverse of its name | Prevents every ASR figure being inverted; analysis code labels it explicitly |
| 21 Nov | Rubric: warnings about pre-existing phishing text in benign runs recorded as "legitimate caution", not false alarms | Step-1 inspection: benign environments contain real phishing-style default text | False-alarm rate isn't inflated by correct caution; both counts reported |
| 21 Nov | Rubric: any location where the agent met the injection counts as "where" | The attack is planted in all 16 slots at once | Avoids penalising warnings that name a different copy of the same attack |
| 21 Nov | Only visible messages scored; hidden reasoning ignored | Haiku produces hidden reasoning, but it is encrypted and unreadable | Can't test "noticed but stayed quiet" from reasoning; stated as a limitation |
| 21 Nov | A revision of P6/P7/D3 (P6 3–7, P7 0–1, D3 Agree) was drafted but never committed; git shows it postdates the pre-registration and the step-1 runs, so it is NOT used for scoring. Results are judged against the committed originals. | | |

---

## Part 4: Open questions and ideas for next time
Things noticed during the work that are outside this weekend's scope. These feed the "What research would you like to work on?" answer.

- [e.g. Do agents disclose differently when the attacker adapts to their responses?]
- [e.g. Would a cheap monitor model, reading the agent's actions, catch what the agent itself doesn't report?]
