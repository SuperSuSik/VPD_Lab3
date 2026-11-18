# ЛР3 — что показать на защите

Живая демонстрация по шагам: команда → что должно быть на экране → что
сказать. Все команды — из корня репозитория.

```sh
cd /Users/cts/VPD_Lab3
```

Полная теория и вопросы — в [`DEFENSE.md`](DEFENSE.md), все команды —
в [`COMMANDS.md`](COMMANDS.md). Этот файл — только порядок показа.

---

## Шаг 1. Репозиторий чистый, коммиты осмысленные

```sh
git status --short
git log --oneline -5
```

Ожидаемо: пустой `git status`, сверху коммиты про части работы.

Сказать: «Репозиторий разбит по частям: `strings/`, `regex/`, `web/`,
`report/`; сборка и проверки — через `Makefile`».

---

## Шаг 2. Собрать всё и прогнать проверки

```sh
make -B report && make run
```

Ожидаемо: код возврата `0`, без предупреждений компилятора. В конце:

```text
Пройдено проверок: 15/15
Совпадение query-параметров: true
Все утверждения assert пройдены.
```

Сказать: «`make -B report` пересобирает C-программы, генерирует
`VPD_Lab3.txt` и сохраняет все выводы в `report/`; `make run` прогоняет
демонстрации и автотесты».

---

## Шаг 3. Структура проекта

```sh
find . -maxdepth 2 -type f ! -path './.git/*' | sort
```

Ожидаемо: `strings/`, `regex/`, `web/`, `report/`, `Makefile`, отчёты.

Сказать: «В `report/` лежат сохранённые выводы — их можно показать, даже
если демо не запускается».

---

## Шаг 4. ASCII: `sizeof` против `strlen`

```sh
./out/ascii
```

Ожидаемо:

```text
sizeof(text):    6
strlen(text):    5
sizeof - strlen: 1 (место под завершающий '\0')
```

Сказать: «`sizeof` — размер массива вместе с `'\0'`, `strlen` — байты до
него. `text[5] == 0` — завершающий нулевой байт».

---

## Шаг 5. UTF-8 ломает «одна буква = один байт»

```sh
./out/utf8
printf 'Привет' | xxd -g1
printf 'ё' | xxd -g1
```

Ожидаемо: `strlen("Привет") = 12`, `sizeof(wchar_t) = 4`; байты
`d0 9f d1 80 …` и `d1 91`.

Сказать: «`strlen` считает байты, а не буквы: 6 кириллических букв — это
12 байт. `ё` в UTF-8 — `D1 91`, два байта».

---

## Шаг 6. Типы элементов и `<stdint.h>`

```sh
./out/types
```

Ожидаемо:

```text
sizeof(char[5])               =  5 байт
sizeof(short[5])              = 10 байт
sizeof(int[5])                = 20 байт
sizeof(unsigned long long[5]) = 40 байт
uint32_t            = 4 байт, 32 бит (exact-width)
```

Сказать: «Одинаковые ASCII-коды в `short[]`/`int[]` не делают их строками:
`printf("%s")` ждёт `char*`. `uint32_t` фиксирует ровно 32 бита, а
`unsigned int` — нет».

---

## Шаг 7. Кодировки, BOM, `0xB8`, гомоглифы

```sh
python3 strings/encoding.py
```

Ожидаемо (ключевые строки):

```text
utf-32    : FF FE 00 00 27 59 00 00 66 5B 00 00
cp1251: 'ё', U+0451 (CYRILLIC SMALL LETTER IO)
UTF-8 error: 'utf-8' codec can't decode byte 0xb8 ...
  cp1251    : B8
  UTF-8     : D1 91
строки равны: False
равны после NFKC: False
```

Сказать: «UTF-8 переменной длины, UTF-32 всегда 4 байта. BOM `FF FE 00 00`
сообщает порядок байтов. `0xB8` — это `ё` только в cp1251; в UTF-8 это
continuation-байт. NFKC не убирает гомоглифы: `М` U+041C ≠ `M` U+004D».

---

## Шаг 8. Base64: полный круг

```sh
python3 strings/base64_demo.py
```

Ожидаемо:

```text
Text:          大学
UTF-8 bytes:   E5 A4 A7 E5 AD A6 (6 байт)
Base64:        5aSn5a2m (8 символов)
Decoded text:  大学
Совпадение:    True
urlsafe_b64encode:-__vAQI=
файлы совпадают:   True
```

Сказать: «Base64 — это байты в ASCII, а не кодировка Unicode. Длина
`4 × ceil(n/3)`, рост около 33%. URL-safe заменяет `+` и `/` на `-` и `_`.
Бинарный round-trip 271 → 365 → 271 байт, SHA-256 совпал».

Быстрая проверка вживую:

```sh
python3 -c 'import base64;print(base64.b64encode("test".encode()).decode())'  # dGVzdA==
node -e 'console.log(Buffer.from("大学","utf8").toString("base64"))'          # 5aSn5a2m
```

---

## Шаг 9. HTML: один символ в трёх записях

```sh
open strings/entities.html
```

Ожидаемо: три строки визуально с одной и той же `ё`.

Сказать: «Обычный символ, `&#1105;` и `&#x451;` — это одна кодовая точка
U+0451; `D1 91` — её байты в UTF-8».

---

## Шаг 10. Unicode-идентификаторы

```sh
./out/unicode_identifiers_gcc
./out/unicode_identifiers_clang
python3 strings/unicode_identifiers.py
node strings/unicode_identifiers.js
```

Ожидаемо во всех четырёх:

```text
студент=304, 学生=7
```

Сказать: «Синтаксически допустимо в GCC, Clang, Python и JavaScript. Но в
командном проекте нужны единый язык и предсказуемый поиск, поэтому
Unicode-имена — не замена соглашению о нейминге».

---

## Шаг 11. Генератор: контрольная последовательность

```sh
./out/generator --print-control
wc -c regex/VPD_Lab3.txt
grep -bo "$(./out/generator --print-control)" regex/VPD_Lab3.txt
```

Ожидаемо:

```text
73108121978311799104107111118
100087 regex/VPD_Lab3.txt
0:73108121978311799104107111118
50029:73108121978311799104107111118
100058:73108121978311799104107111118
```

Сказать: «Последовательность — десятичные ASCII-коды `IlyaSuchkov`:
`73 108 121 …`, всего 29 цифр. 100 000 случайных цифр плюс три вставки:
в начало, в середину и в конец. `100087 = 100000 + 3×29`».

---

## Шаг 12. Степени двойки: `findall` и `sub`

```sh
python3 regex/regex.py > /tmp/regex_demo.txt
grep -E 'ИТОГО|исходный|результат|найдено|удалено|осталось' /tmp/regex_demo.txt
wc -c regex/VPD_Lab3_final.txt
```

Ожидаемо:

```text
ИТОГО       43116
исходный файл:      VPD_Lab3.txt — 100087 байт
результат:          VPD_Lab3_final.txt — 57039 байт
найдено совпадений: 43116
удалено символов:   43048
осталось символов:  57039
```

Сказать: «`re.findall` идёт по 2^0…2^64, сумма 43 116. `re.sub` идёт от
2^64 к 2^0, иначе короткий шаблон ломает длинный. Удалено 43 048 символов:
сумма вхождений больше, потому что совпадения разных степеней
пересекаются».

Показать порядок вживую:

```sh
python3 - <<'EOF'
import re
s = "1024"
print("сначала 2:   ", re.sub("2", "", s))   # 104
print("сначала 1024:", re.sub("1024", "", s)) # пусто
EOF
```

---

## Шаг 13. Перекрытия и `re.ASCII`

```sh
tail -30 /tmp/regex_demo.txt
python3 -c 'import re;print(len(re.findall("1010","101010")), len(re.findall("(?=(1010))","101010")))'
python3 -c 'import re;print(re.findall(r"\w+","Привет 304",re.ASCII))'
```

Ожидаемо:

```text
обычный re.findall:        1
lookahead (?=(...)):       2
1 2
['304']
```

Сказать: «`re.findall` не находит перекрытия; позитивный lookahead находит,
потому что не потребляет символы. `re.ASCII` исключает кириллицу из `\w`».

---

## Шаг 14. Форма: валидация в браузере

```sh
open web/index.html
```

В браузере:

1. «Заполнить валидный пример» → «Проверить форму» →
   «Все поля прошли валидацию».
2. Заменить группу на `M3O-119BV-26` (латинские `M`, `O`) → ошибка.
3. Ввести дату `2026-02-31` → «Такой даты не существует».
4. «Проверить набор примеров» → таблица, 15/15 зелёных строк.

Сказать: «Регулярка проверяет форму, `Date` — существование даты. Для URI
используется `new URL()` и проверка `http:`/`https:`, а не самописная
регулярка. Клиентская проверка — для UX, серверная всё равно нужна».

Автотесты без браузера:

```sh
node web/validation.test.js
```

Ожидаемо:

```text
Пройдено проверок: 15/15
Валидная форма: прошла
Невалидная форма: ошибки в полях date, email, group, phone, uri
```

---

## Шаг 15. URI и percent-encoding

```sh
node web/uri_demo.js
python3 web/uri_demo.py
node -e 'console.log(encodeURIComponent("М3О-119БВ-26"))'
```

Ожидаемо:

```text
protocol : https:
hostname : example.org
port     : 8443
pathname : /api/v1/student-profile
hash     : #results
query    : id = 304
query    : group = М3О-304БВ-26

Совпадение query-параметров: true
%D0%9C3%D0%9E-119%D0%91%D0%92-26
```

Сказать: «Учебная регулярка и `new URL()` дают одинаковые query-параметры.
Percent-encoding кодирует байты UTF-8 в `%XX`; это не Base64 и не
HTML-сущность».

---

## Шаг 16. Нейминг

```sh
sed -n '20,49p' NAMING.md
```

Ожидаемо: таблица «плохое имя → исправление» и финальный URI.

Сказать: «Один язык, нижний регистр, kebab-case в URI; `LK_employee`
заменяем на `employee_account`/`employeeAccount`, потому что смешаны
русское сокращение и английское слово».

---

## Шаг 17. Репозиторий и сайт

```sh
git status -sb
git log --oneline -3
open https://supersusik.github.io/VPD_Lab3/
```

Ожидаемо: `main...origin/main` без расхождений; сайт открывается.

Сказать: «Сайт — это тот же `web/index.html`, опубликованный через GitHub
Actions; репозиторий публичный».

---

## Сокращённый вариант на 3 минуты

Если времени мало — только это:

```sh
./out/ascii
./out/utf8 | grep -E 'strlen: +12|sizeof\(wchar_t\): 4' | head -2
python3 strings/base64_demo.py | sed -n '3,10p'
./out/generator --print-control
wc -c regex/VPD_Lab3.txt regex/VPD_Lab3_final.txt
node web/validation.test.js | tail -4
node web/uri_demo.js | grep -E 'Совпадение query|encodeURIComponent:|UTF-8 байты' | head -3
```

Ожидаемо: `6/5`, `strlen 12`, `sizeof(wchar_t)=4`, Base64 `5aSn5a2m`,
control `73108121978311799104107111118`, `100087` и `57039`, `15/15`,
`Совпадение query-параметров: true`.

---

## Если что-то сломалось

| Проблема | Что делать |
|---|---|
| Сборка не идёт | Показать `report/` и `REPORT.md`: выводы сохранены |
| Нет `gcc-16` | `make CC=gcc` или `brew install gcc` |
| Сайт не открылся | Показать локально `open web/index.html` |
| Испортили сгенерированный файл | `git checkout -- regex/VPD_Lab3.txt regex/VPD_Lab3_final.txt` |
| Не сходится число | `wc -c regex/VPD_Lab3.txt`, `python3 regex/regex.py \| tail` |
