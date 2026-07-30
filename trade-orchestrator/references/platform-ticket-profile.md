# Platform Ticket Output Profile

Use this profile only when the user provides current XTB values by text,
screenshot, or export. The skills must never open or control XTB.

## Supported User Inputs

The user can act on:

- instrument shown by the platform;
- `Market` or `Stop / Limit` tab;
- `BUY` or `SELL`;
- quantity;
- pending trigger price when the `Stop / Limit` tab is used;
- stop-loss checkbox and price;
- take-profit checkbox and price.

Treat bid, ask, spread, contract value, margin, pip/point value, fees, and swap
as read-only context unless the user says they can edit them.

## Source and Basis Rules

- If the journal contains a matching unresolved
  `BASIS_INCIDENT_LOCK_ACTIVE` for the same account, broker symbol, and
  contract, do not populate that user-facing ticket. Ask the user for a current
  compact quote or screenshot with exact broker symbol, bid, ask, spread,
  quote time, and contract or roll basis first. Do not block unrelated
  instruments.
- When the user supplies current XTB data, use its exact broker symbol, bid,
  ask, spread, quote time, and price scale for the ticket.
- Use public spot, futures, index, or news sources for analysis only. Never copy
  their numeric levels into the ticket until the level has been reconciled to
  the platform price basis.
- If the platform basis cannot be reconciled, use `REQUEST_USER_REALTIME`,
  preserve the public-basis directional plan, and ask the user only for current
  symbol, bid, ask, spread, quote time, and matching point value. Do not access
  XTB or output a misleading numeric ticket.
- A displayed quantity is `USER_SELECTED`, not automatically risk-approved.
- Margin is collateral, not maximum loss. Do not present it as trade risk.

## Order Mapping

Choose one ticket action:

- valid signal at the verified current quote: `MARKET` plus `BUY` or `SELL`;
- breakout above current price: `STOP_LIMIT`, `BUY_STOP`;
- breakout below current price: `STOP_LIMIT`, `SELL_STOP`;
- pullback below current price: `STOP_LIMIT`, `BUY_LIMIT`;
- rebound above current price: `STOP_LIMIT`, `SELL_LIMIT`;
- no valid expressible action: `DO_NOT_CLICK`.

In proactive mode, use `MARKET` only after the setup is `READY_NOW` and the
verified quote lies inside the valid entry zone. Do not create alerts,
recurring monitors, or pre-trigger pending orders. Use Stop/Limit only when the
user explicitly asks for it or a validated strategy requires it.

Translate completed analytical confirmation into a ticket the platform can
express. A setup that still needs a market trigger is `NEAR_READY`, not a
ticket. Do not manufacture a pending order merely to avoid waiting.

## Required User-Facing Block

Put this block before analysis, IDs, schemas, or warnings only after platform
translation succeeds:

```text
THAO TÁC TRÊN TICKET
Tab: Lệnh theo giá thị trường | Lệnh Stop / Limit
Loại: Market | Buy Stop | Sell Stop | Buy Limit | Sell Limit
Nút: BUY | SELL
Khối lượng: <value or CHƯA TÍNH>
Giá đặt: <pending price or GIÁ HIỆN TẠI>
Cắt lỗ: BẬT -> <price>
Chốt lời: BẬT -> <price>
```

Then show at most:

- estimated money at risk and reward when point/pip value is known;
- confirmed equity, risk percentage, estimated net reward-to-risk, and target
  profit;
- one cancel/expiry instruction;
- one time-stop or scheduled-event cutoff;
- one basis/spread verification warning;
- a concise reason for the trade.

For an activated USD 2,000 profile, prefer a ticket with approximately USD 15
risk and USD 30 net target. Never exceed USD 20 single-trade risk or USD 40
aggregate open risk. If estimated net reward-to-risk is below 1.8, reduce risk
or reject; always reject below 1.5.

Use the platform's own labels and the user's language. Keep internal workflow
IDs and detailed evidence after the ticket block.

When translation has not succeeded, do not render an empty ticket block.
Render `KẾ HOẠCH CHỦ ĐỘNG`, label all levels `NON_EXECUTABLE_REFERENCE`, and
show `REQUEST_USER_REALTIME`.
