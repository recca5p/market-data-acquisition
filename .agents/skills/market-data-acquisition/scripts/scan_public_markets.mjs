#!/usr/bin/env node

const SCANNER_SCHEMA_VERSION = "1.2";
const COVERAGE_AUDIT_VERSION = "1.0";

// These are the canonical breadth buckets expected by the acquisition and
// advisory contracts. Keep this list independent of the provider universe so
// an unconfigured public reference is disclosed as a gap instead of appearing
// covered by an adjacent instrument.
const REQUIRED_BASELINE_BUCKETS = [
  "FX",
  "EQUITY_INDICES",
  "RATES_SOVEREIGN_BONDS",
  "VOLATILITY",
  "PRECIOUS_METALS",
  "INDUSTRIAL_BASE_METALS",
  "ENERGY",
  "AGRICULTURE_SOFTS",
  "LIVESTOCK",
  "EMISSIONS_ENVIRONMENTAL",
  "FERTILIZER_CHEMICALS",
  "LIQUID_STOCKS",
];

// Normalized provider/open-state values. Yahoo's raw chart meta marketState
// is retained alongside this mapping whenever the provider exposes it.
const PROVIDER_MARKET_STATES = [
  "OPEN",
  "PREOPEN",
  "AFTER_HOURS",
  "CLOSED",
  "HALTED",
  "HOLIDAY",
  "UNKNOWN",
];

const DEFAULT_UNIVERSE = [
  ["FX", "EURUSD=X", "EURUSD"],
  ["FX", "GBPUSD=X", "GBPUSD"],
  ["FX", "JPY=X", "USDJPY"],
  ["FX", "AUDUSD=X", "AUDUSD"],
  ["EQUITY_INDICES", "ES=F", "US500"],
  ["EQUITY_INDICES", "NQ=F", "US100"],
  ["EQUITY_INDICES", "YM=F", "US30"],
  ["EQUITY_INDICES", "^N225", "JP225"],
  ["EQUITY_INDICES", "^GDAXI", "DE40"],
  ["RATES_SOVEREIGN_BONDS", "ZN=F", "TNOTE"],
  ["VOLATILITY", "^VIX", "VIX"],
  ["PRECIOUS_METALS", "GC=F", "GOLD"],
  ["PRECIOUS_METALS", "SI=F", "SILVER"],
  ["INDUSTRIAL_BASE_METALS", "HG=F", "COPPER"],
  ["ENERGY", "CL=F", "OIL.WTI"],
  ["ENERGY", "BZ=F", "OIL"],
  ["ENERGY", "NG=F", "NATGAS"],
  ["AGRICULTURE_SOFTS", "ZW=F", "WHEAT"],
  ["AGRICULTURE_SOFTS", "ZC=F", "CORN"],
  ["AGRICULTURE_SOFTS", "ZS=F", "SOYBEAN"],
  ["AGRICULTURE_SOFTS", "KC=F", "COFFEE"],
  ["AGRICULTURE_SOFTS", "CC=F", "COCOA"],
  ["AGRICULTURE_SOFTS", "SB=F", "SUGAR"],
  ["LIVESTOCK", "LE=F", "CATTLE"],
  ["LIVESTOCK", "HE=F", "LEANHOGS"],
  ["FERTILIZER_CHEMICALS", "CF", "CF.US"],
  ["FERTILIZER_CHEMICALS", "NTR", "NTR.US"],
  ["FERTILIZER_CHEMICALS", "MOS", "MOS.US"],
  ["LIQUID_STOCKS", "AAPL", "AAPL.US"],
  ["LIQUID_STOCKS", "MSFT", "MSFT.US"],
  ["LIQUID_STOCKS", "NVDA", "NVDA.US"],
  ["LIQUID_STOCKS", "TSLA", "TSLA.US"],
  ["LIQUID_STOCKS", "META", "META.US"],
  ["LIQUID_STOCKS", "AMZN", "AMZN.US"],
];

// Do not invent alternate instruments for these gaps. They remain explicit
// until a reviewed public reference is configured for the scanner.
const UNCONFIGURED_PUBLIC_REFERENCES = [
  {
    bucket: "INDUSTRIAL_BASE_METALS",
    instrument_key: "ALUMINIUM",
    reason_code: "NO_CONFIGURED_PUBLIC_REFERENCE",
    plain_reason:
      "Chưa có tham chiếu công khai Yahoo đã cấu hình cho nhôm; đồng chỉ phủ một phần rổ kim loại cơ bản.",
  },
  {
    bucket: "EMISSIONS_ENVIRONMENTAL",
    instrument_key: "EMISS",
    reason_code: "NO_CONFIGURED_PUBLIC_REFERENCE",
    plain_reason:
      "Chưa có tham chiếu công khai Yahoo đã cấu hình cho thị trường phát thải/môi trường.",
  },
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
  const options = {
    top: 8,
    symbols: null,
    session: "ALL",
    entryTiming: "HYBRID_M5",
    selfTest: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--top") options.top = Number(argv[++i]);
    else if (argv[i] === "--symbols") {
      options.symbols = argv[++i].split(",").map((value) => value.trim());
    } else if (argv[i] === "--session") {
      options.session = argv[++i].replaceAll("-", "_").toUpperCase();
    } else if (argv[i] === "--entry-timing") {
      options.entryTiming = argv[++i].replaceAll("-", "_").toUpperCase();
    } else if (argv[i] === "--self-test") {
      options.selfTest = true;
    } else if (argv[i] === "--help") {
      process.stdout.write(
        "Usage: scan_public_markets.mjs [--top N] [--session all|auto|asia|europe|us-preopen|us-cash|overnight] [--symbols SYMBOL,...] [--entry-timing hybrid-m5|m15] [--self-test]\n",
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
  if (!["HYBRID_M5", "M15"].includes(options.entryTiming)) {
    throw new Error("--entry-timing must be hybrid-m5 or m15");
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

function normalizeProviderMarketState(rawValue) {
  const raw =
    typeof rawValue === "string" && rawValue.trim().length > 0
      ? rawValue.trim().toUpperCase()
      : null;
  if (!raw) return { value: "UNKNOWN", raw_value: null };
  if (["OPEN", "REGULAR", "REGULAR_MARKET"].includes(raw)) {
    return { value: "OPEN", raw_value: raw };
  }
  if (raw.includes("PRE")) return { value: "PREOPEN", raw_value: raw };
  if (raw.includes("POST") || raw.includes("AFTER")) {
    return { value: "AFTER_HOURS", raw_value: raw };
  }
  if (raw.includes("HALT")) return { value: "HALTED", raw_value: raw };
  if (raw.includes("HOLIDAY")) return { value: "HOLIDAY", raw_value: raw };
  if (raw.includes("CLOSED") || raw.includes("CLOSE")) {
    return { value: "CLOSED", raw_value: raw };
  }
  return { value: "UNKNOWN", raw_value: raw };
}

function isSessionInactive(providerMarketState) {
  return ["PREOPEN", "AFTER_HOURS", "CLOSED", "HALTED", "HOLIDAY"].includes(
    providerMarketState,
  );
}

function scanModeFor(options) {
  if (options.symbols) return "CUSTOM_SYMBOLS";
  return options.session === "ALL"
    ? "BROAD_BASELINE"
    : "ACTIVE_SESSION_REFRESH";
}

function uniqueStrings(values) {
  return [...new Set(values.filter((value) => value))];
}

const REASON_EXPLANATIONS = {
  MARKET_CLOSED: "Thị trường/tham chiếu công khai đang đóng theo trạng thái nhà cung cấp.",
  SESSION_INACTIVE:
    "Tham chiếu công khai đang ngoài phiên giao dịch chính (tiền phiên hoặc sau giờ).",
  STALE_TRIGGER_DATA:
    "Dữ liệu kích hoạt công khai đã quá cũ so với ngưỡng của khung thời gian.",
  NO_COMPLETED_TRIGGER:
    "Chưa có điều kiện kích hoạt hoàn tất, có thể kiểm chứng từ các nến công khai.",
  MIXED_TIMEFRAME_STRUCTURE:
    "Cấu trúc H1/M15 không đồng thuận theo quy tắc cơ học của bộ quét.",
  TRIGGER_INTEGRITY_FAILED:
    "Giá tham chiếu hiện tại không còn bảo toàn tính toàn vẹn của kích hoạt.",
  OUTSIDE_VALID_ENTRY_ZONE:
    "Giá tham chiếu hiện tại nằm ngoài vùng vào hợp lệ của kích hoạt.",
  OVEREXTENDED:
    "Giá đã kéo giãn quá 0,75 ATR từ vùng/kích hoạt tham chiếu.",
  INSUFFICIENT_REWARD_RISK:
    "Không đủ không gian cơ học để lớp quyết định xây dựng tỷ lệ lợi nhuận/rủi ro chấp nhận được.",
  EVENT_RISK:
    "Sự kiện đã được xác minh làm khóa điều kiện thị trường của ứng viên.",
  SOURCE_UNAVAILABLE:
    "Nguồn công khai không trả về dữ liệu có thể dùng cho lần thử này.",
  IDENTITY_OR_BASIS_UNRESOLVED:
    "Không thể xác nhận định danh hoặc cơ sở giá của tham chiếu công khai.",
  NO_LIQUID_IDENTIFIABLE_INSTRUMENT:
    "Không xác định được công cụ công khai đủ thanh khoản cho rổ này.",
  NOT_IN_REFRESH_SCOPE:
    "Rổ này không thuộc lõi của lần làm mới phiên; không được quét lại như một quét nền đầy đủ.",
  NO_CONFIGURED_PUBLIC_REFERENCE:
    "Bộ quét chưa có tham chiếu công khai đã cấu hình cho công cụ/rổ này.",
  NOT_REQUESTED_BY_CALLER:
    "Rổ này nằm ngoài phạm vi biểu tượng tùy chọn mà người gọi yêu cầu.",
  LOWER_RANKED_THAN_SHORTLIST:
    "Ứng viên hợp lệ về dữ liệu nhưng xếp hạng thấp hơn giới hạn shortlist của lần quét.",
};

function plainReasonFor(reasonCodes, fallback) {
  const explanations = uniqueStrings(
    reasonCodes.map((reasonCode) => REASON_EXPLANATIONS[reasonCode]),
  );
  return explanations.length > 0 ? explanations.join(" ") : fallback;
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
  const previous = bars.at(-2);
  const prior20 = bars.slice(-21, -1);
  const prior60 = bars.slice(-61, -1);
  return {
    last,
    previous,
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

function alignedContext(m15, h1) {
  const m15Vote = trendVote(m15);
  const h1Vote = trendVote(h1);
  const direction =
    m15Vote === 2 && h1Vote === 2
      ? "BULLISH"
      : m15Vote === -2 && h1Vote === -2
        ? "BEARISH"
        : "MIXED";
  return { direction, vote: m15Vote + h1Vote, m15Vote, h1Vote };
}

function classifyCandidate({
  m5,
  m15,
  h1,
  daily,
  providerLagSeconds,
  providerMarketState,
  currentPrice,
  entryTiming,
}) {
  const hybrid = entryTiming === "HYBRID_M5";
  const context = alignedContext(m15, h1);
  const vote = hybrid
    ? context.vote
    : trendVote(m15) + trendVote(h1) + trendVote(daily);
  const direction = hybrid
    ? context.direction
    : vote >= 3
      ? "BULLISH"
      : vote <= -3
        ? "BEARISH"
        : "MIXED";
  const triggerMetric = hybrid ? m5 : m15;
  const contextSetupExtensionAtr =
    m15 &&
    Number.isFinite(m15.atr14) &&
    m15.atr14 > 0 &&
    Number.isFinite(m15.ema20)
      ? Math.abs(m15.last.close - m15.ema20) / m15.atr14
      : null;
  let setupType = "NONE";
  let trigger = null;
  let triggerConditionMet = false;
  if (hybrid && triggerMetric?.previous) {
    const confirmsLong =
      direction === "BULLISH" &&
      triggerMetric.last.close > triggerMetric.previous.high &&
      triggerMetric.last.close > triggerMetric.last.open;
    const confirmsShort =
      direction === "BEARISH" &&
      triggerMetric.last.close < triggerMetric.previous.low &&
      triggerMetric.last.close < triggerMetric.last.open;
    if (
      confirmsLong &&
      triggerMetric.last.close > triggerMetric.prior20High
    ) {
      setupType = "BREAKOUT_CLOSE";
      trigger = triggerMetric.last.close;
      triggerConditionMet = true;
    } else if (
      confirmsShort &&
      triggerMetric.last.close < triggerMetric.prior20Low
    ) {
      setupType = "BREAKOUT_CLOSE";
      trigger = triggerMetric.last.close;
      triggerConditionMet = true;
    } else if (confirmsLong || confirmsShort) {
      setupType = "TREND_PULLBACK";
      trigger = triggerMetric.last.close;
      triggerConditionMet = true;
    }
  } else if (!hybrid) {
    if (
      triggerMetric &&
      direction === "BULLISH" &&
      triggerMetric.last.close > triggerMetric.prior20High
    ) {
      setupType = "BREAKOUT_CLOSE";
      trigger = triggerMetric.prior20High;
      triggerConditionMet = true;
    } else if (
      triggerMetric &&
      direction === "BEARISH" &&
      triggerMetric.last.close < triggerMetric.prior20Low
    ) {
      setupType = "BREAKOUT_CLOSE";
      trigger = triggerMetric.prior20Low;
      triggerConditionMet = true;
    } else if (
      triggerMetric &&
      direction !== "MIXED" &&
      Math.abs(vote) >= 4
    ) {
      setupType = "TREND_PULLBACK";
      trigger = triggerMetric.ema20;
      triggerConditionMet = true;
    }
  }

  const extensionAtr =
    triggerMetric &&
    Number.isFinite(triggerMetric.atr14) &&
    triggerMetric.atr14 > 0 &&
    Number.isFinite(trigger)
      ? Math.abs(triggerMetric.last.close - trigger) / triggerMetric.atr14
      : null;
  const currentExtensionAtr =
    triggerMetric &&
    Number.isFinite(triggerMetric.atr14) &&
    triggerMetric.atr14 > 0 &&
    Number.isFinite(trigger) &&
    Number.isFinite(currentPrice)
      ? Math.abs(currentPrice - trigger) / triggerMetric.atr14
      : null;
  const roomToLevelAtr =
    triggerMetric &&
    Number.isFinite(triggerMetric.atr14) &&
    triggerMetric.atr14 > 0 &&
    Number.isFinite(currentPrice)
      ? direction === "BULLISH"
        ? Math.max(0, triggerMetric.prior60High - currentPrice) /
          triggerMetric.atr14
        : direction === "BEARISH"
          ? Math.max(0, currentPrice - triggerMetric.prior60Low) /
            triggerMetric.atr14
          : 0
      : null;

  let triggerIntegrity = triggerConditionMet;
  if (
    triggerConditionMet &&
    triggerMetric &&
    Number.isFinite(currentPrice)
  ) {
    if (setupType === "BREAKOUT_CLOSE") {
      triggerIntegrity =
        direction === "BULLISH"
          ? currentPrice >= trigger
          : direction === "BEARISH"
            ? currentPrice <= trigger
            : false;
    } else if (setupType === "TREND_PULLBACK") {
      triggerIntegrity =
        direction === "BULLISH"
          ? currentPrice >= triggerMetric.last.low
          : direction === "BEARISH"
            ? currentPrice <= triggerMetric.last.high
            : false;
    }
  }

  let readiness = "NEAR_READY";
  const staleForTrigger =
    !Number.isFinite(providerLagSeconds) ||
    providerLagSeconds >= (hybrid ? 300 : 1800);
  const sessionInactive = isSessionInactive(providerMarketState);
  let triggerDataState = staleForTrigger ? "STALE" : "PUBLIC_COMPLETED";
  const contextExtended =
    hybrid &&
    Number.isFinite(contextSetupExtensionAtr) &&
    contextSetupExtensionAtr > 0.75;
  if (sessionInactive || direction === "MIXED" || contextExtended) {
    readiness = "REJECT";
  } else if (hybrid && !triggerConditionMet) {
    readiness = "NEAR_READY";
    if (staleForTrigger) triggerDataState = "NEEDS_USER_REALTIME";
  } else if (!triggerIntegrity) {
    readiness = "REJECT";
  } else if (hybrid && staleForTrigger) {
    readiness = "NEAR_READY";
    triggerDataState = "NEEDS_USER_REALTIME";
  } else if (staleForTrigger) {
    readiness = "REJECT";
    triggerDataState = "STALE";
  } else if (
    Number.isFinite(currentExtensionAtr) &&
    currentExtensionAtr <= 0.75 &&
    Math.abs(vote) >= 4
  ) {
    readiness = "READY_NOW";
  }

  const score =
    Math.abs(vote) * 10 +
    (readiness === "READY_NOW" ? 25 : readiness === "NEAR_READY" ? 10 : 0) +
    (setupType === "BREAKOUT_CLOSE" ? 5 : 0) -
    Math.min(
      Number.isFinite(providerLagSeconds) ? providerLagSeconds / 60 : 30,
      30,
    ) -
    (Number.isFinite(currentExtensionAtr)
      ? Math.max(0, currentExtensionAtr - 0.75) * 8
      : 0);

  return {
    direction,
    setupType,
    readiness,
    trendVote: vote,
    contextVotes: {
      m15: context.m15Vote,
      h1: context.h1Vote,
    },
    contextSetupExtensionAtr,
    extensionAtr,
    currentExtensionAtr,
    roomToLevelAtr,
    triggerIntegrity,
    triggerConditionMet,
    triggerDataState,
    triggerTimeframe: hybrid ? "M5" : "M15",
    score,
  };
}

function metricSnapshot(metric, intervalSeconds) {
  if (!metric) return null;
  return {
    opened_at_vn: formatIct(metric.last.timestamp),
    closed_at_vn: formatIct(metric.last.timestamp + intervalSeconds),
    open: round(metric.last.open),
    high: round(metric.last.high),
    low: round(metric.last.low),
    close: round(metric.last.close),
    volume: metric.last.volume,
    atr14: round(metric.atr14),
    rsi14: round(metric.rsi14, 1),
    prior20_high: round(metric.prior20High),
    prior20_low: round(metric.prior20Low),
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
  const [m5Raw, m15Raw, h1Raw, dailyRaw] = await Promise.all([
    options.entryTiming === "HYBRID_M5"
      ? fetchChart(publicSymbol, "5m", "5d")
      : Promise.resolve(null),
    fetchChart(publicSymbol, "15m", "5d"),
    fetchChart(publicSymbol, "60m", "1mo"),
    fetchChart(publicSymbol, "1d", "1y"),
  ]);
  const triggerRaw = m5Raw || m15Raw;
  const providerTime = triggerRaw.result.meta.regularMarketTime;
  const observedEpochSeconds = Math.floor(Date.now() / 1000);
  const providerLagSeconds = Number.isFinite(providerTime)
    ? Math.max(0, observedEpochSeconds - providerTime)
    : null;
  const providerMarketState = normalizeProviderMarketState(
    triggerRaw.result.meta.marketState,
  );
  const currentPrice = triggerRaw.result.meta.regularMarketPrice;
  const m5 = m5Raw ? metrics(normalizeBars(m5Raw.result, 300)) : null;
  const m15 = metrics(normalizeBars(m15Raw.result, 900));
  const h1 = metrics(normalizeBars(h1Raw.result, 3600));
  const daily = metrics(normalizeBars(dailyRaw.result, 86400, true));
  const classification = classifyCandidate({
    m5,
    m15,
    h1,
    daily,
    providerLagSeconds,
    providerMarketState: providerMarketState.value,
    currentPrice,
    entryTiming: options.entryTiming,
  });
  return {
    bucket,
    public_symbol: publicSymbol,
    intended_broker_symbol: brokerSymbol,
    public_reference_basis: `${m15Raw.result.meta.exchangeName || "public"} ${m15Raw.result.meta.instrumentType || "market"} reference`,
    currency: m15Raw.result.meta.currency || null,
    entry_timing_mode: options.entryTiming,
    context_timeframes: ["H1", "M15"],
    trigger_timeframe: classification.triggerTimeframe,
    trigger_data_state: classification.triggerDataState,
    provider_price: round(currentPrice),
    provider_time_vn: formatIct(providerTime),
    provider_lag_seconds: providerLagSeconds,
    provider_market_state: providerMarketState.value,
    provider_market_state_raw: providerMarketState.raw_value,
    provider_market_state_source: "YAHOO_CHART_META.marketState",
    provider_market_state_time_vn: formatIct(providerTime),
    provider_market_state_observed_at_vn: formatIct(observedEpochSeconds),
    readiness: classification.readiness,
    directional_structure: classification.direction,
    setup_type: classification.setupType,
    trend_vote: classification.trendVote,
    context_votes: classification.contextVotes,
    context_setup_extension_atr: round(
      classification.contextSetupExtensionAtr,
      2,
    ),
    extension_atr: round(classification.extensionAtr, 2),
    current_extension_atr: round(classification.currentExtensionAtr, 2),
    current_price_in_valid_zone:
      classification.triggerIntegrity &&
      Number.isFinite(classification.currentExtensionAtr) &&
      classification.currentExtensionAtr <= 0.75,
    trigger_integrity: classification.triggerIntegrity,
    trigger_condition_met: classification.triggerConditionMet,
    room_to_recent_level_atr: round(classification.roomToLevelAtr, 2),
    last_completed_m5: metricSnapshot(m5, 300),
    last_completed_m15: metricSnapshot(m15, 900),
    last_completed_trigger_bar: metricSnapshot(
      options.entryTiming === "HYBRID_M5" ? m5 : m15,
      options.entryTiming === "HYBRID_M5" ? 300 : 900,
    ),
    ranking_score: round(classification.score, 2),
    source_url: triggerRaw.url,
  };
}

function runSelfTest() {
  const bullishMetric = {
    last: { timestamp: 1, open: 99.7, high: 100.2, low: 99.8, close: 100 },
    previous: { timestamp: 0, open: 99.5, high: 99.9, low: 99.4, close: 99.7 },
    ema20: 99.9,
    ema50: 99.5,
    rsi14: 55,
    atr14: 1,
    prior20High: 101,
    prior20Low: 98,
    prior60High: 103,
    prior60Low: 97,
  };
  const m15Ready = classifyCandidate({
    m5: null,
    m15: bullishMetric,
    h1: bullishMetric,
    daily: bullishMetric,
    providerLagSeconds: 60,
    currentPrice: 100,
    entryTiming: "M15",
  });
  if (m15Ready.readiness !== "READY_NOW") {
    throw new Error("self-test failed: valid M15 setup was not READY_NOW");
  }
  const m15Broken = classifyCandidate({
    m5: null,
    m15: bullishMetric,
    h1: bullishMetric,
    daily: bullishMetric,
    providerLagSeconds: 60,
    currentPrice: 99.7,
    entryTiming: "M15",
  });
  if (m15Broken.readiness !== "REJECT" || m15Broken.triggerIntegrity) {
    throw new Error("self-test failed: broken trigger was not rejected");
  }
  const hybridDelayed = classifyCandidate({
    m5: bullishMetric,
    m15: bullishMetric,
    h1: bullishMetric,
    daily: bullishMetric,
    providerLagSeconds: 600,
    currentPrice: 100,
    entryTiming: "HYBRID_M5",
  });
  if (
    hybridDelayed.readiness !== "NEAR_READY" ||
    hybridDelayed.triggerDataState !== "NEEDS_USER_REALTIME"
  ) {
    throw new Error("self-test failed: delayed M5 trigger did not request realtime");
  }
  const noM5Trigger = classifyCandidate({
    m5: {
      ...bullishMetric,
      last: {
        timestamp: 1,
        open: 100.1,
        high: 100.2,
        low: 99.9,
        close: 100,
      },
      previous: {
        timestamp: 0,
        open: 99.9,
        high: 100.1,
        low: 99.8,
        close: 100,
      },
    },
    m15: bullishMetric,
    h1: bullishMetric,
    daily: bullishMetric,
    providerLagSeconds: 60,
    currentPrice: 100,
    entryTiming: "HYBRID_M5",
  });
  if (
    noM5Trigger.readiness !== "NEAR_READY" ||
    noM5Trigger.triggerConditionMet
  ) {
    throw new Error("self-test failed: absent M5 trigger was not kept near-ready");
  }
  const closedCandidate = classifyCandidate({
    m5: null,
    m15: bullishMetric,
    h1: bullishMetric,
    daily: bullishMetric,
    providerLagSeconds: 60,
    providerMarketState: "CLOSED",
    currentPrice: 100,
    entryTiming: "M15",
  });
  if (closedCandidate.readiness !== "REJECT") {
    throw new Error("self-test failed: closed provider state was not rejected");
  }

  const syntheticInstrument = {
    bucket: "FX",
    public_symbol: "JPY=X",
    intended_broker_symbol: "USDJPY",
    entry_timing_mode: "M15",
    provider_lag_seconds: 60,
    provider_market_state: "OPEN",
    provider_market_state_raw: "REGULAR",
    provider_market_state_source: "YAHOO_CHART_META.marketState",
    provider_market_state_time_vn: "2026-01-01 10:00:00 ICT",
    provider_market_state_observed_at_vn: "2026-01-01 10:01:00 ICT",
    last_completed_trigger_bar: { closed_at_vn: "2026-01-01 10:00:00 ICT" },
    trigger_condition_met: true,
    directional_structure: "BULLISH",
    trigger_integrity: true,
    current_price_in_valid_zone: true,
    current_extension_atr: 0.1,
    readiness: "READY_NOW",
    source_url: "https://example.invalid/chart/JPY=X",
  };
  const baselineAudit = buildCoverageAudit({
    options: {
      top: 1,
      symbols: null,
      session: "ALL",
      entryTiming: "M15",
    },
    requested: DEFAULT_UNIVERSE,
    results: [syntheticInstrument],
    ranked: [syntheticInstrument],
  });
  const baseMetals = baselineAudit.bucket_rows.find(
    (bucket) => bucket.bucket_id === "INDUSTRIAL_BASE_METALS",
  );
  const emissions = baselineAudit.bucket_rows.find(
    (bucket) => bucket.bucket_id === "EMISSIONS_ENVIRONMENTAL",
  );
  if (
    !baseMetals?.reason_codes.includes("NO_CONFIGURED_PUBLIC_REFERENCE") ||
    !emissions?.reason_codes.includes("NO_CONFIGURED_PUBLIC_REFERENCE")
  ) {
    throw new Error(
      "self-test failed: aluminium or emissions configuration gap was hidden",
    );
  }
  const refreshAudit = buildCoverageAudit({
    options: {
      top: 1,
      symbols: null,
      session: "ASIA",
      entryTiming: "M15",
    },
    requested: DEFAULT_UNIVERSE.filter((item) =>
      SESSION_CORES.ASIA.includes(item[2]),
    ),
    results: [syntheticInstrument],
    ranked: [syntheticInstrument],
  });
  const nonCore = refreshAudit.bucket_rows.find(
    (bucket) => bucket.bucket_id === "EMISSIONS_ENVIRONMENTAL",
  );
  if (
    nonCore?.coverage_outcome !== "NOT_SCANNED" ||
    !nonCore.reason_codes.includes("NOT_IN_REFRESH_SCOPE")
  ) {
    throw new Error(
      "self-test failed: non-core refresh bucket was not explicitly scoped out",
    );
  }
  const closedAttempt = instrumentAttemptFromResult(
    {
      ...syntheticInstrument,
      provider_market_state: "CLOSED",
      readiness: "REJECT",
    },
    new Set(),
  );
  if (!closedAttempt.reason_codes.includes("MARKET_CLOSED")) {
    throw new Error("self-test failed: closed state missed MARKET_CLOSED reason");
  }
  process.stdout.write(
    `${JSON.stringify(
      {
        status: "PASS",
        tests: [
          "current price remains inside valid M15 trigger",
          "broken M15 trigger is rejected",
          "delayed public M5 trigger requires user realtime",
          "aligned context without M5 confirmation remains near-ready",
          "closed provider state produces MARKET_CLOSED and cannot be promoted",
          "coverage audit exposes aluminium and emissions configuration gaps",
          "session-core refresh marks non-core buckets NOT_IN_REFRESH_SCOPE",
        ],
      },
      null,
      2,
    )}\n`,
  );
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

function reasonCodesForInstrument(item) {
  if (item.error) return ["SOURCE_UNAVAILABLE"];

  const reasonCodes = [];
  if (["CLOSED", "HALTED", "HOLIDAY"].includes(item.provider_market_state)) {
    reasonCodes.push("MARKET_CLOSED");
  } else if (["PREOPEN", "AFTER_HOURS"].includes(item.provider_market_state)) {
    reasonCodes.push("SESSION_INACTIVE");
  }

  const triggerLagLimit =
    item.entry_timing_mode === "HYBRID_M5" ? 300 : 1800;
  if (
    !Number.isFinite(item.provider_lag_seconds) ||
    item.provider_lag_seconds >= triggerLagLimit
  ) {
    reasonCodes.push("STALE_TRIGGER_DATA");
  }
  if (!item.last_completed_trigger_bar || !item.trigger_condition_met) {
    reasonCodes.push("NO_COMPLETED_TRIGGER");
  }
  if (item.directional_structure === "MIXED") {
    reasonCodes.push("MIXED_TIMEFRAME_STRUCTURE");
  }
  if (item.trigger_condition_met && item.trigger_integrity === false) {
    reasonCodes.push("TRIGGER_INTEGRITY_FAILED");
  }
  if (item.current_price_in_valid_zone === false) {
    reasonCodes.push("OUTSIDE_VALID_ENTRY_ZONE");
  }
  if (
    Number.isFinite(item.current_extension_atr) &&
    item.current_extension_atr > 0.75
  ) {
    reasonCodes.push("OVEREXTENDED");
  }
  return uniqueStrings(reasonCodes);
}

function instrumentAttemptFromResult(item, promotedSymbols, observedAtVn = null) {
  const reasonCodes = reasonCodesForInstrument(item);
  let promotionState = "NOT_PROMOTED";
  if (item.error || item.readiness === "REJECT") {
    promotionState = "REJECTED";
  } else if (promotedSymbols.has(item.intended_broker_symbol)) {
    promotionState = "PROMOTED";
  }
  if (promotionState === "NOT_PROMOTED" && reasonCodes.length === 0) {
    reasonCodes.push("LOWER_RANKED_THAN_SHORTLIST");
  }

  if (item.error) {
    return {
      instrument_key: item.intended_broker_symbol || item.public_symbol,
      public_symbol: item.public_symbol || null,
      intended_broker_symbol: item.intended_broker_symbol || null,
      attempt_state: "FAILED",
      promotion_state: promotionState,
      readiness: "REJECT",
      provider_market_state: "UNKNOWN",
      provider_market_state_raw: null,
      status_source: "YAHOO_CHART_ENDPOINT",
      status_time_vn: null,
      status_observed_at_vn: observedAtVn,
      source_identifier_or_url: null,
      reason_codes: reasonCodes,
      plain_reason: `${plainReasonFor(reasonCodes, "Lần thử nguồn công khai thất bại.")} ${item.error}`,
    };
  }

  return {
    instrument_key: item.intended_broker_symbol || item.public_symbol,
    public_symbol: item.public_symbol,
    intended_broker_symbol: item.intended_broker_symbol,
    attempt_state: "SUCCEEDED",
    promotion_state: promotionState,
    readiness: item.readiness,
    provider_market_state: item.provider_market_state,
    provider_market_state_raw: item.provider_market_state_raw,
    status_source: item.provider_market_state_source,
    status_time_vn: item.provider_market_state_time_vn,
    status_observed_at_vn: item.provider_market_state_observed_at_vn,
    source_identifier_or_url: item.source_url,
    reason_codes: reasonCodes,
    plain_reason: plainReasonFor(
      reasonCodes,
      promotionState === "PROMOTED"
        ? "Ứng viên được giữ trong shortlist cơ học; vẫn cần kiểm tra sâu bằng nguồn công khai độc lập."
        : "Dữ liệu đã được khảo sát nhưng ứng viên không được quảng bá trong lần quét này.",
    ),
  };
}

function unconfiguredReferenceAttempt(reference, observedAtVn) {
  return {
    instrument_key: reference.instrument_key,
    public_symbol: null,
    intended_broker_symbol: null,
    attempt_state: "NOT_SCANNED",
    promotion_state: "NOT_SCANNED",
    readiness: null,
    provider_market_state: "UNKNOWN",
    provider_market_state_raw: null,
    status_source: "SCANNER_CONFIGURATION",
    status_time_vn: null,
    status_observed_at_vn: observedAtVn,
    source_identifier_or_url: null,
    reason_codes: [reference.reason_code],
    plain_reason: reference.plain_reason,
  };
}

function representativeInstrumentsForBucket(bucket) {
  return uniqueStrings([
    ...DEFAULT_UNIVERSE.filter((item) => item[0] === bucket).map(
      (item) => item[2],
    ),
    ...UNCONFIGURED_PUBLIC_REFERENCES.filter(
      (reference) => reference.bucket === bucket,
    ).map((reference) => reference.instrument_key),
  ]);
}

function summarizeSessionState(instrumentAttempts) {
  const states = uniqueStrings(
    instrumentAttempts
      .filter((attempt) => attempt.attempt_state === "SUCCEEDED")
      .map((attempt) => attempt.provider_market_state),
  );
  if (states.length === 0) return "NOT_SCANNED";
  return states.length === 1 ? states[0] : "MIXED";
}

function inactiveSessionOnly(instrumentAttempts) {
  const successfulAttempts = instrumentAttempts.filter(
    (attempt) => attempt.attempt_state === "SUCCEEDED",
  );
  return (
    successfulAttempts.length > 0 &&
    successfulAttempts.every((attempt) =>
      isSessionInactive(attempt.provider_market_state),
    )
  );
}

function nonScopedBucketRow({ bucket, reasonCode, scanMode, observedAtVn }) {
  return {
    bucket_id: bucket,
    required_for_baseline: true,
    scan_state: "NOT_SCANNED",
    coverage_outcome: "NOT_SCANNED",
    representative_instruments: representativeInstrumentsForBucket(bucket),
    session_state: "NOT_SCANNED",
    session_evidence: [],
    instrument_attempt_count: 0,
    instrument_success_count: 0,
    instrument_failure_count: 0,
    promoted_count: 0,
    not_promoted_count: 0,
    rejected_count: 0,
    reason_codes: [reasonCode],
    plain_reason: `${plainReasonFor([reasonCode], "Rổ không được quét.")} Chế độ quét: ${scanMode}; ghi nhận lúc ${observedAtVn}.`,
    instrument_attempts: [],
  };
}

function bucketRow({ bucket, instrumentAttempts, observedAtVn }) {
  const successfulAttempts = instrumentAttempts.filter(
    (attempt) => attempt.attempt_state === "SUCCEEDED",
  );
  const failedAttempts = instrumentAttempts.filter(
    (attempt) => attempt.attempt_state === "FAILED",
  );
  const hasUnconfiguredReference = instrumentAttempts.some((attempt) =>
    attempt.reason_codes.includes("NO_CONFIGURED_PUBLIC_REFERENCE"),
  );
  const allInactive = inactiveSessionOnly(instrumentAttempts);
  let coverageOutcome = "COVERED";
  if (successfulAttempts.length === 0) {
    coverageOutcome = "GAP";
  } else if (hasUnconfiguredReference || failedAttempts.length > 0) {
    coverageOutcome = "PARTIAL";
  } else if (allInactive) {
    coverageOutcome = "SKIPPED";
  }

  const reasonCodes = uniqueStrings(
    instrumentAttempts.flatMap((attempt) => attempt.reason_codes),
  );
  const sessionEvidence = instrumentAttempts
    .filter((attempt) => attempt.attempt_state === "SUCCEEDED")
    .map((attempt) => ({
      instrument_key: attempt.instrument_key,
      provider_market_state: attempt.provider_market_state,
      provider_market_state_raw: attempt.provider_market_state_raw,
      status_source: attempt.status_source,
      status_time_vn: attempt.status_time_vn,
      status_observed_at_vn: attempt.status_observed_at_vn,
    }));
  const representativeInstruments = uniqueStrings([
    ...instrumentAttempts.map((attempt) => attempt.instrument_key),
    ...representativeInstrumentsForBucket(bucket),
  ]);
  const coverageFallback =
    coverageOutcome === "COVERED"
      ? `Đã thu thập được ít nhất một tham chiếu công khai cho rổ ${bucket}.`
      : `Phủ rổ ${bucket} là ${coverageOutcome} tại ${observedAtVn}.`;

  return {
    bucket_id: bucket,
    required_for_baseline: true,
    scan_state: "ATTEMPTED",
    coverage_outcome: coverageOutcome,
    representative_instruments: representativeInstruments,
    session_state: summarizeSessionState(instrumentAttempts),
    session_evidence: sessionEvidence,
    instrument_attempt_count: successfulAttempts.length + failedAttempts.length,
    instrument_success_count: successfulAttempts.length,
    instrument_failure_count: failedAttempts.length,
    promoted_count: instrumentAttempts.filter(
      (attempt) => attempt.promotion_state === "PROMOTED",
    ).length,
    not_promoted_count: instrumentAttempts.filter(
      (attempt) => attempt.promotion_state === "NOT_PROMOTED",
    ).length,
    rejected_count: instrumentAttempts.filter(
      (attempt) => attempt.promotion_state === "REJECTED",
    ).length,
    reason_codes: reasonCodes,
    plain_reason: plainReasonFor(reasonCodes, coverageFallback),
    instrument_attempts: instrumentAttempts,
  };
}

function buildCoverageAudit({ options, requested, results, ranked }) {
  const observedAtVn = formatIct(Math.floor(Date.now() / 1000));
  const scanMode = scanModeFor(options);
  const promotedSymbols = new Set(
    ranked
      .slice(0, options.top)
      .filter((item) => item.readiness !== "REJECT")
      .map((item) => item.intended_broker_symbol),
  );
  const attemptsByBucket = new Map();
  for (const item of results) {
    const attempts = attemptsByBucket.get(item.bucket) || [];
    attempts.push(
      instrumentAttemptFromResult(item, promotedSymbols, observedAtVn),
    );
    attemptsByBucket.set(item.bucket, attempts);
  }
  const requestedBuckets = new Set(requested.map((item) => item[0]));
  const bucketRows = REQUIRED_BASELINE_BUCKETS.map((bucket) => {
    if (!requestedBuckets.has(bucket)) {
      const unconfiguredReferences = UNCONFIGURED_PUBLIC_REFERENCES.filter(
        (entry) => entry.bucket === bucket,
      );
      if (scanMode === "BROAD_BASELINE" && unconfiguredReferences.length > 0) {
        return bucketRow({
          bucket,
          instrumentAttempts: unconfiguredReferences.map((reference) =>
            unconfiguredReferenceAttempt(reference, observedAtVn),
          ),
          observedAtVn,
        });
      }
      const reasonCode =
        scanMode === "ACTIVE_SESSION_REFRESH"
          ? "NOT_IN_REFRESH_SCOPE"
          : "NOT_REQUESTED_BY_CALLER";
      return nonScopedBucketRow({
        bucket,
        reasonCode,
        scanMode,
        observedAtVn,
      });
    }

    const instrumentAttempts = [
      ...(attemptsByBucket.get(bucket) || []),
    ];
    if (scanMode === "BROAD_BASELINE") {
      for (const reference of UNCONFIGURED_PUBLIC_REFERENCES.filter(
        (entry) => entry.bucket === bucket,
      )) {
        instrumentAttempts.push(unconfiguredReferenceAttempt(reference, observedAtVn));
      }
    }
    return bucketRow({ bucket, instrumentAttempts, observedAtVn });
  });
  const allInstrumentAttempts = bucketRows.flatMap(
    (bucket) => bucket.instrument_attempts,
  );
  const baselineReuse =
    scanMode === "ACTIVE_SESSION_REFRESH"
      ? {
          reuse_status: "NOT_REUSED",
          baseline_acquisition_id: null,
          baseline_acquired_at_vn: null,
          baseline_age_seconds: null,
          reused_fields: [],
          refreshed_fields: [
            "public_quotes",
            "completed_bars",
            "provider_market_state",
            "mechanical_shortlist_ranking",
          ],
          disclosure:
            "Bộ quét độc lập không lưu hoặc nhận acquisition_id nền; đây chỉ là làm mới lõi phiên, không chứng minh một quét nền đầy đủ mới.",
        }
      : {
          reuse_status: "NOT_APPLICABLE",
          baseline_acquisition_id: null,
          baseline_acquired_at_vn: null,
          baseline_age_seconds: null,
          reused_fields: [],
          refreshed_fields: [],
          disclosure:
            "Bộ quét độc lập không tái sử dụng acquisition_id nền đã lưu.",
        };

  return {
    audit_version: COVERAGE_AUDIT_VERSION,
    scan_mode: scanMode,
    generated_at_vn: observedAtVn,
    timezone: "Asia/Ho_Chi_Minh",
    session: {
      session_id: null,
      window: options.session,
      assessed_at_vn: observedAtVn,
      ict_timezone: "Asia/Ho_Chi_Minh",
      requested_session: options.session,
      ict_observed_at_vn: observedAtVn,
    },
    required_bucket_ids: REQUIRED_BASELINE_BUCKETS,
    provider_market_state_enum: PROVIDER_MARKET_STATES,
    baseline_reuse: baselineReuse,
    totals: {
      required_bucket_count: REQUIRED_BASELINE_BUCKETS.length,
      bucket_row_count: bucketRows.length,
      attempted_instrument_count: results.length,
      succeeded_instrument_count: results.filter((item) => !item.error).length,
      failed_instrument_count: results.filter((item) => item.error).length,
      configured_reference_gap_count: allInstrumentAttempts.filter((attempt) =>
        attempt.reason_codes.includes("NO_CONFIGURED_PUBLIC_REFERENCE"),
      ).length,
      covered_bucket_count: bucketRows.filter(
        (bucket) => bucket.coverage_outcome === "COVERED",
      ).length,
      partial_bucket_count: bucketRows.filter(
        (bucket) => bucket.coverage_outcome === "PARTIAL",
      ).length,
      gap_bucket_count: bucketRows.filter(
        (bucket) => bucket.coverage_outcome === "GAP",
      ).length,
      skipped_bucket_count: bucketRows.filter(
        (bucket) => bucket.coverage_outcome === "SKIPPED",
      ).length,
      not_scanned_bucket_count: bucketRows.filter(
        (bucket) => bucket.coverage_outcome === "NOT_SCANNED",
      ).length,
      promoted_instrument_count: allInstrumentAttempts.filter(
        (attempt) => attempt.promotion_state === "PROMOTED",
      ).length,
      not_promoted_instrument_count: allInstrumentAttempts.filter(
        (attempt) => attempt.promotion_state === "NOT_PROMOTED",
      ).length,
      rejected_instrument_count: allInstrumentAttempts.filter(
        (attempt) => attempt.promotion_state === "REJECTED",
      ).length,
    },
    bucket_rows: bucketRows,
    material_unpromoted_or_rejected: allInstrumentAttempts.filter(
      (attempt) =>
        ["NOT_PROMOTED", "REJECTED", "NOT_SCANNED"].includes(
          attempt.promotion_state,
        ) && attempt.reason_codes.length > 0,
    ),
  };
}

const options = parseArgs(process.argv.slice(2));
if (options.selfTest) {
  runSelfTest();
  process.exit(0);
}
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
const coverageAudit = buildCoverageAudit({ options, requested, results, ranked });

process.stdout.write(
  `${JSON.stringify(
    {
      schema_version: SCANNER_SCHEMA_VERSION,
      observed_at_vn: formatIct(Math.floor(Date.now() / 1000)),
      elapsed_seconds: Math.floor(Date.now() / 1000) - scanStarted,
      source_mode: "PUBLIC_NON_EXECUTABLE",
      scan_scope: options.symbols ? "CUSTOM_SYMBOLS" : options.session,
      scan_mode: scanModeFor(options),
      entry_timing_mode: options.entryTiming,
      methodology_warning:
        options.entryTiming === "HYBRID_M5"
          ? "Mechanical Yahoo-reference breadth ranking only. HYBRID_M5 uses H1/M15 for context and M5 only for a completed entry trigger. A public M5 lag of five minutes or more cannot produce READY_NOW and requires user-provided realtime. Deep-check promoted candidates with publicly visible Investing.com data and official events. Never treat this as XTB data; current XTB values must come from the user."
          : "Mechanical Yahoo-reference breadth ranking using the completed-M15 baseline. Deep-check promoted candidates with publicly visible Investing.com data and official events. Never treat this as XTB data; current XTB values must come from the user.",
      requested_count: requested.length,
      success_count: ranked.length,
      failure_count: failures.length,
      shortlist: ranked.slice(0, options.top),
      failures,
      coverage_audit: coverageAudit,
    },
    null,
    2,
  )}\n`,
);
