# Agent contract

Start at `SKILL.md`. Detect MODE from the user question, then Read **only** the files that router names. The running agent is the decision maker. Do not spawn named subagents.

## Invariants

Follow `core.md`: `MANUAL_ADVISORY`; never broker login/API/browser control; public data is non-executable until basis is reconciled; Missing XTB is not a coverage skip; never invent numbers; crypto → `NO_TRADE`; Hybrid M5 with a 0.25% research risk cap; ICT timestamps; Vietnamese default for open-ended `BROAD_BASELINE` / `ACTIVE_SESSION_REFRESH` replies; lead with the plan or `NO_TRADE` then `ĐÃ KHẢO SÁT` and `SKIP/LOẠI VÀ LÝ DO`; journal is append-only and gitignored; do not mix this pack with the sibling 1–2y accumulation repo.

## Skills

Domain contracts live under `skills/<name>/SKILL.md` (plus `references/` and `scripts/` when present). Apply them by reading those files. This pack does not implement a code-change subagent; if you are changing this repo, edit files normally.

## Tests

After changing executable code, schemas consumed by tests, or test paths, run:

```text
python -m unittest discover -s tests -v
```
