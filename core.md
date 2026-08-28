# Core invariants

Shared across every MODE. Do not duplicate entire skill files here. After this file, Read only the skills the router named.

This is a **manual, non-crypto trading advisory** pack. 1–2 year accumulation (quality-at-a-discount) is a **different repo** — do not mix loaders, time horizons, or LONG/SHORT session trades with that playbook: https://github.com/recca5p/quality-at-a-discount

## MANUAL_ADVISORY

Every workflow is `MANUAL_ADVISORY`. The user alone reads the broker, supplies real-time fields, and decides whether and how to place an order.

- Never log in to XTB, open or control a broker app/browser, call a broker API or connector, or use credentials / authenticated session state.
- Set `xtb_interaction_allowed: false`. Treat all XTB real-time and account fields as `USER_PROVIDED_REALTIME` only.
- Never submit, modify, cancel, or simulate an order.
- Missing XTB/broker/account values are never a market-coverage skip reason. They only block exact ticket fields, quantity, and account-specific monetary estimates.

## Data honesty

- Never invent quotes, bars, fills, account values, costs, P&L, timestamps, sources, or test results.
- Public quotes and completed bars are analytical references, not executable prices. Keep them labelled `NON_EXECUTABLE_REFERENCE` until the broker symbol and price basis are reconciled.
- Disclose source, basis, provider time, stated delay, and observation time in **ICT (Asia/Ho_Chi_Minh, UTC+7)**.
- Do not bypass CAPTCHA, paywalls, robots, rate limits, or access controls.

## Asset class

Crypto spot, perpetuals, futures, options, CFDs, and crypto-tracking ETPs/ETFs → `NO_TRADE` with `UNSUPPORTED_ASSET_CLASS_CRYPTO` and `DO_NOT_CLICK`. Do not size or ticket them. Supported markets: FX, equity indices, rates/sovereign bonds, volatility, precious metals, industrial/base metals, energy, agriculture/softs, livestock, emissions/environmental, fertilizer/chemicals, liquid stocks.

## Hybrid M5

H1 is regime, M15 is setup, only a **completed M5 bar** may trigger entry. A public M5 feed delayed by one full bar cannot produce `READY_NOW`; mark `NEAR_READY` and `NEEDS_USER_REALTIME`. Until the profile is `ADVISORY_VALIDATED`, cap research risk at `0.25%` of confirmed equity; require explicit costs; reject spread above `20%` of stop distance and total cost above `0.25R`.

## Open-ended scan replies

For this user's `BROAD_BASELINE` and `ACTIVE_SESSION_REFRESH` advisories, default the user-facing response language to **Vietnamese** unless the user requests another language.

Lead with the actionable plan or `NO_TRADE`. Immediately after that block, render the canonical acquisition `coverage_audit` under the exact headings `ĐÃ KHẢO SÁT` and `SKIP/LOẠI VÀ LÝ DO`. Never summarize this merely as “đã quét thị trường”.

The audit must disclose scan mode, session, ICT observation time, attempted and succeeded counts, every required baseline bucket, representative instruments, provider/session status and evidence, coverage outcome, and each material unpromoted/rejected candidate or skipped bucket with a stable reason code and a plain explanation. A refresh must name its reused baseline acquisition ID and age plus exactly what was refreshed, or explicitly say that no baseline was reused. Missing XTB/broker/account values are never a market-coverage skip reason.

## Journal

Append-only. Workspace file `trade-history/manual-advisory-history.jsonl` is gitignored. Never rewrite, reorder, or delete prior events. Never infer that the user entered.

## Decision states

Keep `DIRECTION_READY`, `PLAN_PARTIAL`, `PLAN_READY`, `NO_TRADE`, and `WAIT_FOR_DATA` distinct. A valid public direction with missing platform data is `NEEDS_USER_REALTIME`, not `WAIT_FOR_DATA`.
