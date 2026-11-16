"use strict";

// Демонстрация URI-разбора в Node.js.
// Запуск: node web/uri_demo.js

const assert = require("node:assert/strict");
const {
  URI_EXAMPLE,
  parseWithRegex,
  parseWithURL,
  formatParsed,
  formatPercentDemo,
  percentEncodingDemo,
} = require("./uri.js");

const byRegex = parseWithRegex(URI_EXAMPLE);
const byUrl = parseWithURL(URI_EXAMPLE);

if (!byRegex) throw new Error("regex parser returned null");
assert.equal(byRegex.protocol, "https:");
assert.equal(byRegex.hostname, "example.org");
assert.equal(byRegex.port, "8443");
assert.equal(byRegex.pathname, "/api/v1/student-profile");
assert.equal(byRegex.hash, "#results");

const regexParams = Object.fromEntries(byRegex.queryParams);
const urlParams = Object.fromEntries(byUrl.queryParams);
assert.equal(regexParams.id, "304");
assert.equal(regexParams.group, "М3О-304БВ-26");
assert.deepEqual(regexParams, urlParams);

console.log("=== URI: учебная регулярка ===");
console.log(formatParsed("regex", byRegex));
console.log();
console.log("=== URI: штатный URL ===");
console.log(formatParsed("URL", byUrl));
console.log();
console.log(`Декодированная группа: ${regexParams.group}`);
console.log(`Совпадение query-параметров: ${JSON.stringify(regexParams) === JSON.stringify(urlParams)}`);
console.log();
console.log(formatPercentDemo(percentEncodingDemo()));
console.log("\nВсе утверждения assert пройдены.");
