# Нейминг: формальный стиль и смысл имени

ЛР3, раздел 6. Формально корректное имя ещё не означает хорошего имени:
важны единый естественный язык, отсутствие бессмысленных сокращений и
одинаковый стиль в пределах одного слоя.

## 1. Стили записи

| Стиль | Пример | Типичный контекст |
|---|---|---|
| `camelCase` | `studentName` | локальные переменные и поля в JavaScript, Java, C# |
| `PascalCase` | `StudentProfile` | типы и классы |
| `snake_case` | `student_name` | переменные и функции в C/Python |
| `SCREAMING_SNAKE_CASE` | `MAX_BUFFER_SIZE` | константы и макросы |
| `kebab-case` | `student-profile` | URI path, имена файлов, CSS |

`kebab-case` не является обычным идентификатором C: дефис в C — оператор
вычитания. В URI дефис допустим и читается лучше, чем `_` или `%20`.

## 2. Исправление плохих примеров

| Плохой пример | Исправление | Почему |
|---|---|---|
| `LK_employee` | `employee_account` (C/Python) или `employeeAccount` (JS) | `LK` — сокращение русского «личный кабинет», а `employee` — английское слово. Смешаны язык и сокращение. |
| `user_kabinet` | `user_account` | `kabinet` — транслитерация русского слова; в английском API лучше `account`. |
| `Student_name` | `student_name` | Нарушен стиль: PascalCase и snake_case в одном имени. |
| `lichnyKabinetEmployee` | `employeePersonalAccount` / `employee_personal_account` | Транслит русского «личный кабинет» + английское `employee`; в camelCase-контексте нужен один язык. |
| `/api/LK_employee/get-Dannye?user_Nomer=304` | `/api/employees/personal-account?employee-number=304` | В path и query смешаны регистр, `_`, русские слова транслитом и сокращение `LK`. |

## 3. Финальный URI

Исходный URI:

```text
https://server.example/LK_employee/get-Dannye?user_Nomer=304
```

Приведённый к одной системе (английский язык, нижний регистр,
kebab-case в URI):

```text
https://server.example/employees/personal-account?employee-number=304
```

Более RESTful-вариант с явным ресурсом и версией API:

```text
https://server.example/api/v1/employees/304/personal-account
```

Оба варианта допустимы. Выбранная система:

* один естественный язык — английский;
* осмысленные термины: `employee`, `personal-account`, `employee-number`;
* без сокращений, понятных только авторам (`LK`, `Dannye`, `Nomer`);
* единый регистр и разделитель в URI — нижний регистр и дефис;
* в коде — стиль, принятый в конкретном языке: `snake_case` в C/Python,
  `camelCase` для переменных JavaScript, `PascalCase` для типов.

## 4. Вывод

Техническая допустимость Unicode-идентификаторов (`студент`, `学生`) не
означает, что их нужно использовать в командном проекте без правил.
Идентификаторы должны быть понятны всем участникам, одинаково
отображаться в терминалах, поиске и Git-истории. Unicode уместен для
пользовательских данных и локализованного UI, а не как замена командному
соглашению о нейминге.
