// ЛР3, части III: валидация строковых данных в HTML/JavaScript.
//
// Файл работает и в браузере, и в Node.js: DOM-инициализация выполняется
// только при наличии document, а функции экспортируются для тестов.
"use strict";

const patterns = Object.freeze({
  // Кириллические М и О, три цифры, БВ, две цифры.
  group: /^М3О-\d{3}БВ-\d{2}$/u,
  phone: /^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$/,
  // Упрощённое учебное правило, а не полная реализация RFC 5322.
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  dateFormat: /^\d{4}-\d{2}-\d{2}$/,
  // Минимум два слова; допускаются дефис и до четырёх слов.
  fullName: /^[А-ЯЁ][а-яё]+(?:[ -][А-ЯЁ][а-яё]+){1,3}$/u,
});

const fieldTitles = Object.freeze({
  fullName: "ФИО",
  group: "номер группы",
  phone: "телефон",
  email: "e-mail",
  date: "дата",
  uri: "URI",
});

function normalize(value) {
  return String(value ?? "").trim().normalize("NFC");
}

function validateFullName(value) {
  const text = normalize(value);
  if (!text) return "Введите фамилию и имя.";
  if (!patterns.fullName.test(text)) {
    return "Нужны 2–4 слова на кириллице: например, Илья Сучков.";
  }
  return "";
}

function validateGroup(value) {
  const text = normalize(value);
  if (!text) return "Введите номер группы.";
  if (!patterns.group.test(text)) {
    return "Формат: М3О-119БВ-26 (М и О — кириллические, без пробелов).";
  }
  return "";
}

function validatePhone(value) {
  const text = normalize(value);
  if (!text) return "Введите телефон.";
  if (!patterns.phone.test(text)) {
    return "Формат: +7 (999) 123-45-67.";
  }
  return "";
}

function validateEmail(value) {
  const text = normalize(value);
  if (!text) return "Введите e-mail.";
  if (text.length > 254) return "E-mail длиннее 254 символов.";
  if (!patterns.email.test(text)) {
    return "Упрощённый формат: name@example.org.";
  }
  return "";
}

function isValidDate(value) {
  const text = normalize(value);
  if (!patterns.dateFormat.test(text)) return false;

  // Регулярка проверяет только форму. Date проверяет существование даты:
  // 2026-02-31 превращается в другую дату и не совпадёт с исходной строкой.
  const parsed = new Date(`${text}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) return false;
  return parsed.toISOString().slice(0, 10) === text;
}

function validateDate(value) {
  const text = normalize(value);
  if (!text) return "Введите дату.";
  if (!patterns.dateFormat.test(text)) return "Формат: YYYY-MM-DD.";
  if (!isValidDate(text)) return "Такой даты не существует (например, 2026-02-31).";
  return "";
}

function validateUri(value) {
  const text = normalize(value);
  if (!text) return "Введите URI.";
  try {
    const url = new URL(text);
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return "Поддерживаются только http:// и https://.";
    }
    if (!url.hostname) return "В URI отсутствует хост.";
  } catch {
    return "URI не разбирается штатным парсером URL.";
  }
  return "";
}

function validateField(field, value) {
  switch (field) {
    case "fullName": return validateFullName(value);
    case "group": return validateGroup(value);
    case "phone": return validatePhone(value);
    case "email": return validateEmail(value);
    case "date": return validateDate(value);
    case "uri": return validateUri(value);
    default: throw new Error(`unknown field: ${field}`);
  }
}

function validateFormData(data) {
  const errors = {};
  for (const field of Object.keys(fieldTitles)) {
    const error = validateField(field, data[field] ?? "");
    if (error) errors[field] = error;
  }
  return { valid: Object.keys(errors).length === 0, errors };
}

const exampleCases = Object.freeze([
  { field: "fullName", value: "Илья Сучков", expected: true, note: "кириллица" },
  { field: "fullName", value: "Ilya Suchkov", expected: false, note: "латиница" },
  { field: "group", value: "М3О-119БВ-26", expected: true, note: "кириллические М/О" },
  { field: "group", value: "М3О-304БВ-26", expected: true, note: "пример из задания" },
  { field: "group", value: "M3O-119BV-26", expected: false, note: "латинские M/O — гомоглифы" },
  { field: "phone", value: "+7 (999) 123-45-67", expected: true, note: "точный формат" },
  { field: "phone", value: "8 (999) 123-45-67", expected: false, note: "другой префикс" },
  { field: "email", value: "student@example.org", expected: true, note: "упрощённое правило" },
  { field: "email", value: "student@example", expected: false, note: "нет точки в домене" },
  { field: "date", value: "2024-02-29", expected: true, note: "существующая дата" },
  { field: "date", value: "2026-02-31", expected: false, note: "форма верна, даты нет" },
  { field: "date", value: "16.11.2026", expected: false, note: "неверный формат" },
  { field: "uri", value: "https://example.org:8443/api/v1/student-profile?id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results", expected: true, note: "полный URI" },
  { field: "uri", value: "not a uri", expected: false, note: "не URI" },
  { field: "uri", value: "ftp://example.org/file", expected: false, note: "не http/https" },
]);

function clearFieldError(field) {
  const input = document.getElementById(field);
  const output = document.getElementById(`error-${field}`);
  if (input) {
    input.classList.remove("invalid");
    input.removeAttribute("aria-invalid");
  }
  if (output) output.textContent = "";
}

function showFieldError(field, message) {
  const input = document.getElementById(field);
  const output = document.getElementById(`error-${field}`);
  if (input) {
    input.classList.add("invalid");
    input.setAttribute("aria-invalid", "true");
  }
  if (output) output.textContent = message;
}

function clearAllErrors() {
  for (const field of Object.keys(fieldTitles)) clearFieldError(field);
  const result = document.getElementById("form-result");
  if (result) {
    result.textContent = "";
    result.className = "result";
  }
}

function readForm(form) {
  const data = {};
  for (const field of Object.keys(fieldTitles)) {
    const element = form.elements.namedItem(field);
    data[field] = element ? element.value : "";
  }
  return data;
}

function renderExamples() {
  const container = document.getElementById("examples-output");
  if (!container) return;

  container.replaceChildren();
  let passed = 0;

  for (const example of exampleCases) {
    const error = validateField(example.field, example.value);
    const actual = error === "";
    const ok = actual === example.expected;
    if (ok) passed += 1;

    const row = document.createElement("tr");
    const cells = [
      fieldTitles[example.field],
      example.value,
      example.expected ? "валидно" : "невалидно",
      actual ? "валидно" : "невалидно",
      ok ? "OK" : "ОШИБКА",
      example.note,
    ];
    for (const text of cells) {
      const cell = document.createElement("td");
      cell.textContent = text;
      row.append(cell);
    }
    row.className = ok ? "row-ok" : "row-fail";
    container.append(row);
  }

  const summary = document.getElementById("examples-summary");
  if (summary) {
    summary.textContent = `Пройдено ${passed} из ${exampleCases.length} проверок.`;
  }
}

function init() {
  const form = document.getElementById("validation-form");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearAllErrors();

    const data = readForm(form);
    const result = validateFormData(data);
    const output = document.getElementById("form-result");

    if (!result.valid) {
      for (const [field, message] of Object.entries(result.errors)) {
        showFieldError(field, message);
      }
      if (output) {
        output.textContent = "Форма содержит ошибки. Исправьте подсвеченные поля.";
        output.className = "result error";
      }
      const first = Object.keys(result.errors)[0];
      const input = document.getElementById(first);
      if (input) input.focus();
      return;
    }

    if (output) {
      output.textContent = "Все поля прошли валидацию.";
      output.className = "result success";
    }
  });

  form.addEventListener("input", (event) => {
    if (event.target?.name in fieldTitles) {
      clearFieldError(event.target.name);
    }
  });

  document.getElementById("fill-valid")?.addEventListener("click", () => {
    const sample = {
      fullName: "Илья Сучков",
      group: "М3О-119БВ-26",
      phone: "+7 (999) 123-45-67",
      email: "ilya.suchkov@example.org",
      date: "2026-11-16",
      uri: "https://example.org:8443/api/v1/student-profile?id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results",
    };
    for (const [field, value] of Object.entries(sample)) {
      const input = document.getElementById(field);
      if (input) input.value = value;
    }
    clearAllErrors();
  });

  document.getElementById("run-examples")?.addEventListener("click", renderExamples);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    patterns,
    fieldTitles,
    exampleCases,
    normalize,
    validateFullName,
    validateGroup,
    validatePhone,
    validateEmail,
    validateDate,
    validateUri,
    validateField,
    validateFormData,
    isValidDate,
  };
}

if (typeof window !== "undefined" && typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}
