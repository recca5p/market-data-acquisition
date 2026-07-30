# Public and Delayed Market-Data Source Hierarchy

## Contents

1. Source classes
2. Required source by data type
3. Asset-specific sources
4. Permitted search and aggregator use
5. Freshness, lifecycle, and conflict rules

## 1. Source Classes

| Priority | Source class | Valid use |
| --- | --- | --- |
| 1 | Official/primary publisher | FOMC/central-bank releases, CPI/jobs/GDP data, EIA/USDA reports, exchange instrument and warehouse data, SEC/issuer filings, official earnings releases, and official weather/energy data. |
| 2 | Public market-data or aggregator page | Delayed/indicative price, chart, change, and calendar data from a named public source such as Investing.com. |
| 3 | Public news/reporting | Time-stamped context from a named publisher. |
| 4 | Google/other search result | Locate a public source; record snippet-only context as low confidence and never use it as the sole source for a decision-critical price or event. |

## 2. Required Source by Data Type

| Data | Required source | Not acceptable as a substitute |
| --- | --- | --- |
| Market price/context | Named public market page with provider timestamp/delay or local observation time | An unlabelled search snippet or an uncited social post |
| Account balance/margin/P&L | Out of scope for this public-data skill | Public price page, user memory, or a third-party app |
| OHLCV used for indicators | Identified public instrument and completed/labelled bar | A different futures/spot/index instrument without declared basis |
| Exchange session and instrument specification | Official exchange, issuer, broker contract specification, or named primary instrument publisher | Assumption from a similarly named instrument |
| Central-bank/macro actual | Official release | Headline summary without release data |
| FX policy/rate decision | Relevant central bank and official statistical publisher | An opaque buy/sell score or uncited rate expectation |
| Sovereign yield/contract specification | Official treasury/debt office, central bank, or exchange | A differently matured yield or bond future without declared duration/basis |
| Volatility contract/index methodology | Cboe, Eurex, or the relevant official exchange/index publisher | Treating a spot volatility index as identical to a dated future or CFD |
| Natural-gas storage | EIA release | Social-media post or prediction |
| Agricultural supply/demand | USDA or the relevant official national/international publisher | An uncited crop estimate or social-media forecast |
| Commodity contract/specification | Official exchange or primary benchmark publisher | A similarly named spot, cash, future, ETF, producer stock, or CFD |
| Fertilizer physical benchmark | Named benchmark publisher with product, geography, unit, currency, and assessment date | A producer-stock price or an unspecified global fertilizer price |
| Earnings/filing/legal event | Issuer IR, exchange, regulator/SEC | Rumor or repost |
| Geopolitical fact | Named reliable primary/public authority; cross-check material claims | Anonymous/social claim or AI summary |

## 3. Asset-Specific Sources

### Prohibited Crypto Instruments

Do not collect crypto spot, perpetual, futures, options, CFD, funding, open
interest, order-book, or crypto-tracking ETP/ETF data for a manual trade
proposal. Return `BLOCKED` with
`blocking_reason: UNSUPPORTED_ASSET_CLASS_CRYPTO` before source discovery.

### Gold

- Public XAUUSD, spot-gold, or gold-futures reference with the instrument basis declared.
- Official central-bank and inflation releases for event facts.
- A public yield and USD-market source for cross-market context.

### FX

- Identify whether the public reference is spot, an exchange future, or an
  OTC/CFD quote. Record both currencies, venue/reference, session, and
  timestamp.
- Prefer the relevant central banks and official statistical publishers for
  policy decisions and macro actuals.
- Use rate differentials, intervention facts, and USD context only when their
  timestamps and maturities are declared.

### Rates and Sovereign Bonds

- Use the official exchange for futures specifications and the relevant
  treasury/debt office or central bank for cash yields, auctions, and policy.
- Record maturity, contract month, duration exposure, tick value, expiry, and
  roll. A bond-futures price commonly moves inversely to its yield; do not
  label the direction without naming the measured instrument.

### Volatility

- Prefer Cboe, Eurex, or the relevant official exchange/index publisher for
  index methodology, futures specifications, settlement, and expiries.
- Record the exact dated future and term structure. Do not treat spot VIX,
  VIX futures, VSTOXX futures, and broker CFDs as interchangeable.

### Natural Gas

- Public natural-gas spot/futures reference, with contract month and roll/basis declared when applicable.
- EIA for storage releases.
- Public or official weather, production, LNG/export, and pipeline information where available.

### Industrial and Base Metals

- Use an identifiable LME, CME/COMEX, SHFE, or other official
  exchange/benchmark reference when available. Record exchange, contract,
  grade, unit, currency, contract month, expiry, and trading session.
- Use official exchange warehouse/inventory data and primary macro releases
  for supply-demand context. Label delayed exchange data and different market
  time zones.
- Distinguish copper cash from copper futures, and aluminum from alumina.
  Never map a producer equity or ETF price to a metal-future or broker-CFD
  ticket.

### Crude Oil and Refined Energy

- Identify grade and location, such as WTI or Brent, plus contract month,
  expiry, unit, and roll basis.
- Prefer EIA and other primary agencies for inventory/production, and primary
  producer-group announcements for supply policy.
- Keep crude, gasoline, heating oil/gasoil, and energy-company equities as
  separate instruments even when they provide cross-market evidence.

### Agriculture and Soft Commodities

- Use an identifiable CME/CBOT, ICE, or other official exchange contract and
  record crop/delivery month, unit, currency, price limits, expiry, and roll.
- Prefer USDA and relevant official weather, crop, export, and supply-demand
  releases. Record release times and revisions.
- Treat seasonality and weather as context, not as a standalone directional
  signal. Do not silently combine different grades, origins, or delivery
  locations.

### Livestock and Emissions

- For livestock, use the official exchange plus USDA or the relevant primary
  agricultural authority for supply, feed, disease, trade, and price-limit
  facts.
- For emissions, use the official exchange, regulator, and auction authority.
  Record the allowance type, compliance period, currency, contract month,
  auction schedule, and policy changes.

### Fertilizer and Chemicals

- Physical urea, ammonia, UAN, phosphate, and potash markets are fragmented.
  Record product, nutrient/grade, geography, incoterm, unit, currency,
  assessment date, and benchmark methodology whenever available.
- Use a physical benchmark only as contextual evidence unless the user has a
  platform-listed instrument whose basis can be reconciled.
- For a tradable public candidate, prefer a liquid listed producer or a
  clearly identified exchange-listed instrument. Use issuer filings and
  earnings for company-specific facts; collect natural-gas/feedstock costs,
  crop economics, freight, and export-policy facts as cross-market context.

### Equity Index and Single Stocks

- Public cash-index, futures, ETF, or stock reference with the instrument basis declared.
- Issuer investor-relations, exchange, SEC/regulator filings, and official economic releases for material events.

## 4. Permitted Search and Aggregator Use

Use Google or another search tool through an approved API/agent search capability to locate an official release, public market page, or credible reporting. Open the original result when practical. A snippet may be retained as labelled, low-confidence context if the original cannot be opened, but it must not be the sole basis of a material directional claim. Do not automate results-page scraping, circumvent robots directives, or bypass access controls.

Use Investing.com as the default public deep-check source for price, completed
bars, technical inputs, session context, and calendar data when the access
method and terms permit it. Label its displayed values with the visible source
time or local observation time and treat them as delayed, non-executable
context. Do not bulk collect, store, redistribute, reverse engineer endpoints,
or bypass technical restrictions. Prefer its calendar/page as a pointer to the
underlying official release.

Never use this public-data skill to open or control XTB, authenticate to XTB,
call a broker API, invoke a broker connector, or inspect a logged-in platform.
Only the user may supply real-time XTB symbol, bid, ask, spread, quote time,
and contract/value-per-point fields after public analysis promotes a candidate.

## 5. Freshness, Lifecycle, and Conflict Rules

- Normalize all display times to ICT.
- Always record both the provider's displayed timestamp/delay, if present, and the local ICT observation time.
- Evaluate freshness against supplied limits when present. Without explicit limits, record actual age/delay and whether it is material to the decision horizon; do not block a manual advisory solely because the provider is delayed.
- Record exchange timezone, session boundary, holiday status, and daylight-saving interpretation when relevant.
- For equities, record split/dividend adjustment, symbol changes, delistings, and halts when they affect the requested window.
- For futures, record contract month, expiry, roll date, and any back/ratio adjustment. Never mix a continuous series with a tradable contract without disclosure.
- For physical commodity assessments, record the assessment date, geography,
  grade, unit, currency, and incoterm; never present the assessment as a live
  executable quote.
- Validate bars for ordered timestamps, expected spacing, duplicates, gaps, OHLC consistency, nonpositive values, and volume semantics.
- For a conflict in price, compare instrument basis and timestamps, record the discrepancy, and do not designate any public price as executable.
- For a conflict in event facts, seek the primary source. If unresolved, mark it unverified and do not use it directionally.
- Do not use cached data as current without the timestamp and source status.
