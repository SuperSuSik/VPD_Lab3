// ЛР3, часть IV: URI, percent-encoding и сравнение подходов.
//
// Сначала URI разбирается учебной регуляркой, затем — штатным URL-парсером.
// Для реальных задач предпочтителен специализированный парсер.
"use strict";

const URI_EXAMPLE =
  "https://example.org:8443/api/v1/student-profile?" +
  "id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results";

const URI_PATTERN =
  /^([a-z][a-z0-9+.-]*):\/\/([^/?#]+)([^?#]*)(?:\?([^#]*))?(?:#(.*))?$/iu;

function splitAuthority(authority) {
  let userinfo = "";
  let hostPort = authority;

  const at = authority.lastIndexOf("@");
  if (at !== -1) {
    userinfo = authority.slice(0, at);
    hostPort = authority.slice(at + 1);
  }

  let hostname = hostPort;
  let port = "";

  if (hostPort.startsWith("[")) {
    // IPv6-literal: [::1]:8443
    const close = hostPort.indexOf("]");
    if (close !== -1) {
      hostname = hostPort.slice(0, close + 1);
      if (hostPort[close + 1] === ":") port = hostPort.slice(close + 2);
    }
  } else {
    const colon = hostPort.lastIndexOf(":");
    if (colon !== -1) {
      hostname = hostPort.slice(0, colon);
      port = hostPort.slice(colon + 1);
    }
  }

  return { userinfo, hostname, port };
}

function parseWithRegex(value) {
  const match = URI_PATTERN.exec(value);
  if (!match) return null;

  const scheme = match[1];
  const authority = match[2];
  const pathname = match[3] || "/";
  const rawQuery = match[4] ?? "";
  const rawFragment = match[5] ?? "";
  const { userinfo, hostname, port } = splitAuthority(authority);

  return {
    protocol: `${scheme.toLowerCase()}:`,
    authority,
    userinfo,
    hostname,
    port,
    pathname,
    search: match[4] === undefined ? "" : `?${rawQuery}`,
    hash: match[5] === undefined ? "" : `#${rawFragment}`,
    queryParams: [...new URLSearchParams(rawQuery)],
    note: "учебная регулярка; не является полным RFC 3986-парсером",
  };
}

function parseWithURL(value) {
  const url = new URL(value);
  return {
    protocol: url.protocol,
    authority: url.host,
    userinfo: url.username
      ? `${url.username}${url.password ? ":••••" : ""}`
      : "",
    hostname: url.hostname,
    port: url.port,
    pathname: url.pathname,
    search: url.search,
    hash: url.hash,
    queryParams: [...url.searchParams],
    note: "штатный парсер URL (WHATWG URL)",
  };
}

function formatParsed(label, parsed) {
  if (!parsed) return `${label}: URI не разобран`;

  const lines = [
    `${label}:`,
    `  protocol : ${parsed.protocol}`,
    `  hostname : ${parsed.hostname}`,
    `  port     : ${parsed.port || "(не указан)"}`,
    `  pathname : ${parsed.pathname}`,
    `  search   : ${parsed.search || "(пусто)"}`,
    `  hash     : ${parsed.hash || "(пусто)"}`,
    `  note     : ${parsed.note}`,
  ];

  if (parsed.userinfo) lines.push(`  userinfo : ${parsed.userinfo}`);
  for (const [key, value] of parsed.queryParams) {
    lines.push(`  query    : ${key} = ${value}`);
  }
  return lines.join("\n");
}

function base64FromUtf8(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function percentEncodingDemo() {
  const group = "М3О-119БВ-26";
  const encoded = encodeURIComponent(group);
  const decoded = decodeURIComponent(encoded);
  const groupBytes = new TextEncoder().encode(group);
  const yo = "ё";

  return {
    group,
    encoded,
    decoded,
    roundTrip: decoded === group,
    groupBytes: [...groupBytes],
    groupBytesHex: [...groupBytes]
      .map((byte) => byte.toString(16).padStart(2, "0").toUpperCase())
      .join(" "),
    groupBase64: base64FromUtf8(group),
    yo,
    yoDecimalEntity: `&#${yo.codePointAt(0)};`,
    yoHexEntity: `&#x${yo.codePointAt(0).toString(16)};`,
    yoUtf8Hex: [...new TextEncoder().encode(yo)]
      .map((byte) => byte.toString(16).padStart(2, "0").toUpperCase())
      .join(" "),
    yoBase64: base64FromUtf8(yo),
  };
}

function formatPercentDemo(demo) {
  return [
    "percent-encoding (URI):",
    `  исходная группа : ${demo.group}`,
    `  encodeURIComponent: ${demo.encoded}`,
    `  decodeURIComponent: ${demo.decoded}`,
    `  полный круг     : ${demo.roundTrip ? "OK" : "ОШИБКА"}`,
    `  UTF-8 байты     : ${demo.groupBytesHex} (${demo.groupBytes.length} байт)`,
    `  Base64 группы   : ${demo.groupBase64}`,
    "",
    "HTML-сущности (HTML-документ):",
    `  символ          : ${demo.yo}`,
    `  десятичная      : ${demo.yoDecimalEntity}`,
    `  шестнадцатеричная: ${demo.yoHexEntity}`,
    `  UTF-8 байты     : ${demo.yoUtf8Hex}`,
    "",
    "Base64 (бинарь → ASCII):",
    `  Base64 «ё»      : ${demo.yoBase64}`,
    "",
    "Это разные уровни: percent-encoding кодирует байты в URI,",
    "HTML-сущность задаёт кодовую точку в HTML, Base64 представляет",
    "любые байты ограниченным ASCII-алфавитом.",
  ].join("\n");
}

function initUriDemo() {
  const regexOutput = document.getElementById("uri-regex");
  const urlOutput = document.getElementById("uri-url");
  const percentOutput = document.getElementById("percent-output");
  if (!regexOutput || !urlOutput || !percentOutput) return;

  const regexParsed = parseWithRegex(URI_EXAMPLE);
  const urlParsed = parseWithURL(URI_EXAMPLE);

  regexOutput.textContent = formatParsed("Регулярное выражение", regexParsed);
  urlOutput.textContent = formatParsed("Штатный URL", urlParsed);
  percentOutput.textContent = formatPercentDemo(percentEncodingDemo());
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    URI_EXAMPLE,
    URI_PATTERN,
    splitAuthority,
    parseWithRegex,
    parseWithURL,
    formatParsed,
    formatPercentDemo,
    percentEncodingDemo,
    base64FromUtf8,
  };
}

if (typeof window !== "undefined" && typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initUriDemo);
  } else {
    initUriDemo();
  }
}
