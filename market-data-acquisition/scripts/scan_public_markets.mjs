#!/usr/bin/env node

const DEFAULT_UNIVERSE = [
  ["FX", "EURUSD=X", "EURUSD"],
  ["FX", "GBPUSD=X", "GBPUSD"],
  ["FX", "JPY=X", "USDJPY"],
  ["FX", "AUDUSD=X", "AUDUSD"],
  ["INDEX", "ES=F", "US500"],
  ["INDEX", "NQ=F", "US100"],
  ["INDEX", "YM=F", "US30"],
  ["INDEX", "^N225", "JP225"],
  ["INDEX", "^GDAXI", "DE40"],
  ["RATES", "ZN=F", "TNOTE"],
  ["VOLATILITY", "^VIX", "VIX"],
  ["PRECIOUS_METAL", "GC=F", "GOLD"],
  ["PRECIOUS_METAL", "SI=F", "SILVER"],
  ["BASE_METAL", "HG=F", "COPPER"],
  ["ENERGY", "CL=F", "OIL.WTI"],
  ["ENERGY", "BZ=F", "OIL"],
  ["ENERGY", "NG=F", "NATGAS"],
  ["AGRICULTURE", "ZW=F", "WHEAT"],
  ["AGRICULTURE", "ZC=F", "CORN"],
  ["AGRICULTURE", "ZS=F", "SOYBEAN"],
  ["SOFT", "KC=F", "COFFEE"],
  ["SOFT", "CC=F", "COCOA"],
  ["SOFT", "SB=F", "SUGAR"],
  ["LIVESTOCK", "LE=F", "CATTLE"],
  ["LIVESTOCK", "HE=F", "LEANHOGS"],
  ["FERTILIZER_PROXY", "CF", "CF.US"],
  ["FERTILIZER_PROXY", "NTR", "NTR.US"],
  ["FERTILIZER_PROXY", "MOS", "MOS.US"],
  ["STOCK", "AAPL", "AAPL.US"],
  ["STOCK", "MSFT", "MSFT.US"],
  ["STOCK", "NVDA", "NVDA.US"],
  ["STOCK", "TSLA", "TSLA.US"],
  ["STOCK", "META", "META.US"],
  ["STOCK", "AMZN", "AMZN.US"],
];

const SESSION_CORES = {
  ASIA: ["USDJPY", "AUDUSD", "JP225", "GOLD"],
  EUROPE: ["EURUSD", "GBPUSD", "DE40", "GOLD", "OIL.WTI"],
  US_PREOPEN: ["US500", "US100", "GOLD", "OIL.WTI", "NATGAS"],
  US_CASH: [
    "US500",
    "US100",
    "GOLD",
    "OIL.WTI",
    "NATGAS",
    "AAPL.US",
    "MSFT.US",
    "NVDA.US",
    "TSLA.US",
    "META.US",
    "AMZN.US",
  ],
  OVERNIGHT: ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "GOLD"],
};

function autoSession() {
  const hour = Number(
    new Intl.DateTimeFormat("en-GB", {
      timeZone: "Asia/Ho_Chi_Minh",
      hour: "2-digit",
      hourCycle: "h23",
    }).format(new Date()),
  );
  if (hour >= 5 && hour < 14) return "ASIA";
  if (hour >= 14 && hour < 19) return "EUROPE";
  if (hour >= 19 && hour < 21) return "US_PREOPEN";
  if (hour >= 21) return "US_CASH";
  return "OVERNIGHT";
}

function parseArgs(argv) {
  const options = { top: 8, symbols: null, session: "ALL" };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--top") options.top = Number(argv[++i]);
    else if (argv[i] === "--symbols") {
      options.symbols = argv[++i].split(",").map((value) => value.trim());
    } else if (argv[i] === "--session") {
      options.session = argv[++i].replaceAll("-", "_").toUpperCase();
    } else if (argv[i] === "--help") {
      process.stdout.write(
        "Usage: scan_public_markets.mjs [--top N] [--session all|auto|asia|europe|us-preopen|us-cash|overnight] [--symbols SYMBOL,...]\n",
      );
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${argv[i]}`);
    }
  }
  if (!Number.isInteger(options.top) || options.top < 1 || options.top > 50) {
    throw new Error("--top must be an integer from 1 through 50");
  }
  const allowedSessions = ["ALL", "AUTO", ...Object.keys(SESSION_CORES)];
  if (!allowedSessions.includes(options.session)) {
    throw new Error(`--session must be one of ${allowedSessions.join(", ")}`);
  }
  if (options.session === "AUTO") options.session = autoSession();
  return options;
}

function formatIct(epochSeconds) {
  if (!Number.isFinite(epochSeconds)) return null;
  const parts = new Intl.DateTimeFormat("sv-SE", {
    timeZone: "Asia/Ho_Chi_Minh",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date(epochSeconds * 1000));
  return `${parts} ICT`;
}

function round(value, digits = 5) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function ema(values, period) {
  if (values.length < period) return null;
  const multiplier = 2 / (period + 1);
  let value =
    values.slice(0, period).reduce((sum, item) => sum + item, 0) / period;
  for (let i = period; i < values.length; i += 1) {
    value = values[i] * multiplier + value * (1 - multiplier);
  }
  return value;
}

function rsi(values, period = 14) {
  if (values.length < period + 1) return null;
  let gains = 0;
  let losses = 0;
  for (let i = values.length - period; i < values.length; i += 1) {
    const change = values[i] - values[i - 1];
    if (change > 0) gains += change;
    else losses -= change;
  }
  if (losses === 0) return 100;
  return 100 - 100 / (1 + gains / losses);
}

function atr(bars, period = 14) {
  if (bars.length < period + 1) return null;
  const values = [];
  for (let i = 1; i < bars.length; i += 1) {
    values.push(
      Math.max(
        bars[i].high - bars[i].low,
        Math.abs(bars[i].high - bars[i - 1].close),
        Math.abs(bars[i].low - bars[i - 1].close),
      ),
    );
  }
  return (
    values.slice(-period).reduce((sum, item) => sum + item, 0) / period
  );
}

function normalizeBars(result, intervalSeconds, daily = false) {
  const quote = result.indicators?.quote?.[0];
  if (!quote) return [];
  const providerTime = result.meta?.regularMarketTime;
  const bars = [];
  for (let i = 0; i < (result.timestamp || []).length; i += 1) {
    const timestamp = result.timestamp[i];
    const values = [
      quote.open?.[i],
      quote.high?.[i],
      quote.low?.[i],
      quote.close?.[i],
    ];
    if (!Number.isFinite(timestamp) || values.some((value) => !Number.isFinite(value))) {
      continue;
    }
    if (!daily && timestamp + intervalSeconds > providerTime) continue;
    const [open, high, low, close] = values;
    if (open <= 0 || close <= 0 || high < low) continue;
    bars.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume: quote.volume?.[i] || 0,
    });
  }
  if (daily && bars.length > 1) bars.pop();
  return bars;
}

function metrics(bars) {
  if (bars.length < 21) return null;
  const closes = bars.map((bar) => bar.close);
  const last = bars.at(-1);
  const prior20 = bars.slice(-21, -1);
  const prior60 = bars.slice(-61, -1);
  return {
    last,
    ema20: ema(closes, 20),
    ema50: ema(closes, 50),
    rsi14: rsi(closes),
    atr14: atr(bars),
    prior20High: Math.max(...prior20.map((bar) => bar.high)),
    prior20Low: Math.min(...prior20.map((bar) => bar.low)),
    prior60High: Math.max(...prior60.map((bar) => bar.high)),
    prior60Low: Math.min(...prior60.map((bar) => bar.low)),
  };
}

function trendVote(metric) {
  if (!metric || !Number.isFinite(metric.ema20) || !Number.isFinite(metric.ema50)) {
    return 0;
  }
  if (metric.last.close > metric.ema20 && metric.ema20 > metric.ema50) return 2;
  if (metric.last.close < metric.ema20 && metric.ema20 < metric.ema50) return -2;
  if (metric.last.close > metric.ema20) return 1;
  if (metric.last.close < metric.ema20) return -1;
  return 0;
}

function classifyCandidate(m15, h1, daily, providerLagSeconds) {
  const vote = trendVote(m15) + trendVote(h1) + trendVote(daily);
  const direction =
    vote >= 3 ? "BULLISH" : vote <= -3 ? "BEARISH" : "MIXED";
  let setupType = "NONE";
  let trigger = null;
  if (m15 && direction === "BULLISH" && m15.last.close > m15.prior20High) {
    setupType = "BREAKOUT_CLOSE";
    trigger = m15.prior20High;
  } else if (
    m15 &&
    direction === "BEARISH" &&
    m15.last.close < m15.prior20Low
  ) {
    setupType = "BREAKOUT_CLOSE";
    trigger = m15.prior20Low;
  } else if (m15 && Math.abs(vote) >= 4) {
    setupType = "TREND_PULLBACK";
    trigger = m15.ema20;
  }

  const extensionAtr =
    m15 && Number.isFinite(m15.atr14) && m15.atr14 > 0 && Number.isFinite(trigger)
      ? Math.abs(m15.last.close - trigger) / m15.atr14
      : null;
  const roomToLevelAtr =
    m15 && Number.isFinite(m15.atr14) && m15.atr14 > 0
      ? direction === "BULLISH"
        ? Math.max(0, m15.prior60High - m15.last.close) / m15.atr14
        : direction === "BEARISH"
          ? Math.max(0, m15.last.close - m15.prior60Low) / m15.atr14
          : 0
      : null;

  let readiness = "NEAR_READY";
  const stale = providerLagSeconds > 1800;
  if (stale || direction === "MIXED" || setupType === "NONE") readiness = "REJECT";
  else if (
    Number.isFinite(extensionAtr) &&
    extensionAtr <= 0.75 &&
    Math.abs(vote) >= 4
  ) {
    readiness = "READY_NOW";
  }

  const score =
    Math.abs(vote) * 10 +
    (readiness === "READY_NOW" ? 25 : readiness === "NEAR_READY" ? 10 : 0) +
    (setupType === "BREAKOUT_CLOSE" ? 5 : 0) -
    Math.min(providerLagSeconds / 60, 30) -
    (Number.isFinite(extensionAtr) ? Math.max(0, extensionAtr - 0.75) * 8 : 0);

  return {
    direction,
    setupType,
    readiness,
    trendVote: vote,
    extensionAtr,
    roomToLevelAtr,
    score,
  };
}

async function fetchChart(symbol, interval, range) {
  const url =
    `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}` +
    `?interval=${interval}&range=${range}&includePrePost=true&events=div%2Csplits`;
  const response = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 Codex public-market scan" },
    signal: AbortSignal.timeout(10000),
  });
  const payload = await response.json();
  const result = payload.chart?.result?.[0];
  if (!response.ok || !result) {
    throw new Error(
      `${response.status}: ${payload.chart?.error?.description || "no chart result"}`,
    );
  }
  return { result, url };
}

async function scanOne([bucket, publicSymbol, brokerSymbol]) {
  const [m15Raw, h1Raw, dailyRaw] = await Promise.all([
    fetchChart(publicSymbol, "15m", "5d"),
    fetchChart(publicSymbol, "60m", "1mo"),
    fetchChart(publicSymbol, "1d", "1y"),
  ]);
  const providerTime = m15Raw.result.meta.regularMarketTime;
  const providerLagSeconds = Math.max(
    0,
    Math.floor(Date.now() / 1000) - providerTime,
  );
  const m15 = metrics(normalizeBars(m15Raw.result, 900));
  const h1 = metrics(normalizeBars(h1Raw.result, 3600));
  const daily = metrics(normalizeBars(dailyRaw.result, 86400, true));
  const classification = classifyCandidate(
    m15,
    h1,
    daily,
    providerLagSeconds,
  );
  return {
    bucket,
    public_symbol: publicSymbol,
    intended_broker_symbol: brokerSymbol,
    public_reference_basis: `${m15Raw.result.meta.exchangeName || "public"} ${m15Raw.result.meta.instrumentType || "market"} reference`,
    currency: m15Raw.result.meta.currency || null,
    provider_price: round(m15Raw.result.meta.regularMarketPrice),
    provider_time_vn: formatIct(providerTime),
    provider_lag_seconds: providerLagSeconds,
    readiness: classification.readiness,
    directional_structure: classification.direction,
    setup_type: classification.setupType,
    trend_vote: classification.trendVote,
    extension_atr: round(classification.extensionAtr, 2),
    room_to_recent_level_atr: round(classification.roomToLevelAtr, 2),
    last_completed_m15: m15
      ? {
          opened_at_vn: formatIct(m15.last.timestamp),
          open: round(m15.last.open),
          high: round(m15.last.high),
          low: round(m15.last.low),
          close: round(m15.last.close),
          volume: m15.last.volume,
          atr14: round(m15.atr14),
          rsi14: round(m15.rsi14, 1),
          prior20_high: round(m15.prior20High),
          prior20_low: round(m15.prior20Low),
        }
      : null,
    ranking_score: round(classification.score, 2),
    source_url: m15Raw.url,
  };
}

async function mapWithConcurrency(items, concurrency, mapper) {
  const results = new Array(items.length);
  let nextIndex = 0;
  async function worker() {
    while (nextIndex < items.length) {
      const current = nextIndex++;
      try {
        results[current] = await mapper(items[current]);
      } catch (error) {
        results[current] = {
          bucket: items[current][0],
          public_symbol: items[current][1],
          intended_broker_symbol: items[current][2],
          error: String(error),
        };
      }
    }
  }
  await Promise.all(
    Array.from({ length: Math.min(concurrency, items.length) }, () => worker()),
  );
  return results;
}

const options = parseArgs(process.argv.slice(2));
const requested = options.symbols
  ? DEFAULT_UNIVERSE.filter(
      (item) =>
        options.symbols.includes(item[1]) || options.symbols.includes(item[2]),
    )
  : options.session === "ALL"
    ? DEFAULT_UNIVERSE
    : DEFAULT_UNIVERSE.filter((item) =>
        SESSION_CORES[options.session].includes(item[2]),
      );
if (requested.length === 0) {
  throw new Error("No requested symbols matched the public scan universe");
}

const scanStarted = Math.floor(Date.now() / 1000);
const results = await mapWithConcurrency(requested, 6, scanOne);
const failures = results.filter((item) => item.error);
const ranked = results
  .filter((item) => !item.error)
  .sort((left, right) => right.ranking_score - left.ranking_score);

process.stdout.write(
  `${JSON.stringify(
    {
      schema_version: "1.0",
      observed_at_vn: formatIct(Math.floor(Date.now() / 1000)),
      elapsed_seconds: Math.floor(Date.now() / 1000) - scanStarted,
      source_mode: "PUBLIC_NON_EXECUTABLE",
      scan_scope: options.symbols ? "CUSTOM_SYMBOLS" : options.session,
      methodology_warning:
        "Mechanical Yahoo-reference breadth ranking only. Deep-check promoted candidates with publicly visible Investing.com data and official events. Never treat this as XTB data; current XTB values must come from the user.",
      requested_count: requested.length,
      success_count: ranked.length,
      failure_count: failures.length,
      shortlist: ranked.slice(0, options.top),
      failures,
    },
    null,
    2,
  )}\n`,
);
