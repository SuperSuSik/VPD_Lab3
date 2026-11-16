"use strict";

// Автоматическая проверка правил формы без браузера.
// Запуск: node web/validation.test.js

const assert = require("node:assert/strict");
const {
  exampleCases,
  validateField,
  validateFormData,
} = require("./validation.js");

let passed = 0;
const rows = [];

for (const example of exampleCases) {
  const error = validateField(example.field, example.value);
  const actual = error === "";
  const ok = actual === example.expected;
  assert.equal(ok, true,
    `${example.field}: ${example.value}; ` +
    `expected ${example.expected}, got ${actual}; error=${error}`);
  if (ok) passed += 1;
  rows.push({
    field: example.field,
    value: example.value,
    expected: example.expected ? "valid" : "invalid",
    actual: actual ? "valid" : "invalid",
    note: example.note,
  });
}

const validForm = {
  fullName: "Илья Сучков",
  group: "М3О-119БВ-26",
  phone: "+7 (999) 123-45-67",
  email: "ilya.suchkov@example.org",
  date: "2026-11-16",
  uri: "https://example.org:8443/api/v1/student-profile?id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results",
};

const validResult = validateFormData(validForm);
assert.deepEqual(validResult, { valid: true, errors: {} });

const invalidForm = {
  ...validForm,
  group: "M3O-119BV-26",
  phone: "8 (999) 123-45-67",
  email: "student@example",
  date: "2026-02-31",
  uri: "not a uri",
};
const invalidResult = validateFormData(invalidForm);
assert.equal(invalidResult.valid, false);
assert.deepEqual(Object.keys(invalidResult.errors).sort(), [
  "date", "email", "group", "phone", "uri",
]);

console.log("=== Автоматические проверки формы ===");
console.log("поле       значение                                                                 ожидание  факт      результат");
console.log("-".repeat(125));
for (const row of rows) {
  const value = row.value.length > 70 ? `${row.value.slice(0, 67)}...` : row.value;
  console.log(
    `${row.field.padEnd(10)} ${value.padEnd(72)} ${row.expected.padEnd(9)} ` +
    `${row.actual.padEnd(9)} OK`,
  );
}
console.log("-".repeat(125));
console.log(`Пройдено проверок: ${passed}/${exampleCases.length}`);
console.log(`Валидная форма: ${validResult.valid ? "прошла" : "не прошла"}`);
console.log(`Невалидная форма: ошибки в полях ${Object.keys(invalidResult.errors).sort().join(", ")}`);
console.log("Все утверждения assert пройдены.");
