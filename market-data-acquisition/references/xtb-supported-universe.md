# XTB Vietnam Verified Non-Crypto Universe

## Verification Basis

Use this reference only for XTB manual-advisory scans. It was verified on
2026-07-29 against:

- [XTB Vietnam instrument documents](https://www.xtb.com/vn/instrument-specification/documents);
- [XTB specification table effective from 2026-06-29](https://xas-new-cdn.xtb.com/file/0104/57/3df2064a-b5c1-4fbd-b602-911f9d1ab51a/specification-table-vn-latest.pdf);
- [XTB Stock CFD and ETF CFD table effective from 2026-06-29](https://www.xtb.com/int/Specification_Table_Stock_CFDs_and_ETF_CFDs.pdf).

Treat this as a discovery allowlist, not permanent proof of availability.
Before an actionable ticket, confirm that the symbol is visible and openable
in the user's current XTB account and is not marked `CLOSE ONLY`. The user must
provide that confirmation; the skills never open, search, authenticate to, or
control XTB.

XTB states that most instruments referencing index or commodity futures are
OTC instruments whose prices are determined by XTB and can differ from the
organized-market underlying. Preserve the XTB symbol and CFD basis; never map
exchange-futures levels directly into a ticket.

## Default Scan Universe

### FX CFDs

Use liquid XTB currency-pair CFDs such as `EURUSD`, `GBPUSD`, `USDJPY`,
`AUDUSD`, `USDCAD`, `USDCHF`, and `NZDUSD`. Other pairs listed in the current
table may be scanned when their session, spread, and catalyst are suitable.
These are exchange-rate CFDs, not CME currency futures.

### Equity Indices and Volatility

Prefer:

- `US500`, `US100`, `US30`, and `US2000`;
- `DE40`, `EU50`, `UK100`, and `JP225`;
- `VIX` and `VSTOXX` only with their futures-referenced term, expiry, and
  volatility-basis risks understood;
- `USDIDX` as a tradable dollar-index futures-referenced CFD and as
  cross-market context.

Other verified regional indices may be scanned, including `VIET30`, but rank
them below the liquid core unless a local catalyst and usable spread justify
promotion.

### Rates and Sovereign Bonds

XTB lists:

- `TNOTE` - U.S. 10-Year Treasury Note futures-referenced instrument;
- `BUND10Y` - Euro-Bund futures-referenced instrument;
- `SCHATZ2Y` - Euro-Schatz futures-referenced instrument.

Do not equate a bond-futures price move with a yield move in the same
direction. Before sizing, ask the user to provide the current XTB quote,
contract basis, roll, and tick/value-per-point fields.

### Commodities and Specialist Futures References

The verified table lists:

- metals: `GOLD`, `GOLD.FUT`, `SILVER`, `COPPER`, `ALUMINIUM`, `ZINC`,
  `NICKEL`, `PLATINUM`, and `PALLADIUM`;
- energy: `OIL.WTI`, `OIL`, `NATGAS`, `GASOLINE`, and `LSGASOIL`;
- grains/oilseeds: `CORN`, `WHEAT`, `SOYBEAN`, and `SOYOIL`;
- softs: `COFFEE`, `COCOA`, `SUGAR`, and `COTTON`;
- livestock: `CATTLE` and `LEANHOGS`;
- environmental: `EMISS`, referencing EUA emission futures.

For `COPPER`, `ALUMINIUM`, `ZINC`, and `NICKEL`, the XTB table identifies an
NDF basis. Do not substitute an LME or COMEX level as the ticket price.

### Fertilizer Exposure

The current XTB commodity table does not list a direct fertilizer future.
Use physical fertilizer benchmarks only as context.

The current XTB Stock CFD table verifies these liquid producer proxies:

- `CF.US` - CF Industries Holdings;
- `NTR.US` - Nutrien;
- `MOS.US` - Mosaic.

Treat each as a company equity with earnings, balance-sheet, gap, and
company-specific risk. Do not treat its share price as a fertilizer benchmark.

## Refresh and Fail-Closed Rules

- Locate the current public XTB document through Google or its public document
  page when the effective date changes. Do not access the user's XTB account.
- Before relying on a symbol not recently confirmed, ask the user whether it is
  currently visible and openable in XTB.
- Exclude any symbol marked with an asterisk or `CLOSE ONLY` from new-entry
  candidates.
- Convert official CET/CEST trading hours to ICT and account for daylight
  saving.
- Require user-provided current platform symbol, bid, ask, spread, quote time,
  quantity mechanics, and contract basis before printing actionable XTB
  levels.
- Exclude every cryptoasset and crypto-tracking instrument even if XTB lists
  it elsewhere.
