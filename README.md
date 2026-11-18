# VPD Lab 3 — Строки, кодировки, Base64, регулярные выражения и URI

Лабораторная работа №3 по курсу «Введение в профессиональную деятельность»:
путь от байтов и кодировок к строкам, Base64, регулярным выражениям,
валидации HTML/JavaScript и разбору URI.

**Студент:** Илья Сучков, группа М3О-119БВ-26, номер в списке 21.

**Репозиторий:** https://github.com/SuperSuSik/VPD_Lab3

**Сайт (GitHub Pages):** https://supersusik.github.io/VPD_Lab3/ — интерактивная
форма валидации из каталога `web/`, опубликованная через GitHub Actions.

## Окружение

| Компонент | Версия / значение |
|---|---|
| ОС | macOS 26.3 (Darwin 25.x), Apple Silicon |
| Архитектура | arm64 (AArch64) |
| Компилятор C | Homebrew GCC 16.2.0 (`gcc-16`) |
| Проверочный C-компилятор | Apple clang 21.0.0 |
| Python | 3.15.0 |
| Node.js | 26.12.1 |
| GNU Make | 3.81 |
| Кодировка исходных файлов | UTF-8 (без BOM) |
| Локаль | `C.UTF-8` |

На macOS системная команда `gcc` — это Apple clang, поэтому в `Makefile`
явно выбран `gcc-16`. На Linux можно переопределить компилятор:

```sh
make CC=gcc
```

## Структура проекта

```text
VPD_Lab3/
├── strings/
│   ├── ascii.c                 # sizeof/strlen и dec/hex-коды символов
│   ├── utf8.c                  # пять UTF-8-строк, байты, wchar_t, wcslen
│   ├── types.c                 # char/short/int/unsigned long long и <stdint.h>
│   ├── encoding.py             # UTF-8/16/32, BOM, 0xB8, гомоглифы, HTML-коды
│   ├── base64_demo.py          # Base64, padding, Base64URL, бинарный round-trip
│   ├── entities.html           # «ё» как символ, dec- и hex-сущность
│   ├── unicode_identifiers.c   # Unicode-идентификаторы в GCC и Clang
│   ├── unicode_identifiers.py  # Unicode-идентификаторы в Python
│   └── unicode_identifiers.js  # Unicode-идентификаторы в JavaScript
├── regex/
│   ├── generator.c             # 100 000 цифр + 3 контрольные последовательности
│   ├── VPD_Lab3.txt            # сохранённый stdout генератора
│   ├── regex.py                # re.findall, re.sub, перекрытия, re.ASCII
│   └── VPD_Lab3_final.txt      # результат удаления степеней двойки
├── web/
│   ├── index.html              # форма, таблица примеров, URI-демонстрация
│   ├── validation.js           # валидация ФИО, группы, телефона, e-mail, даты, URI
│   ├── validation.test.js      # автоматические проверки формы в Node.js
│   ├── uri.js                  # URI: regex + new URL(), percent-encoding
│   ├── uri_demo.js             # демонстрация URI в Node.js
│   └── uri_demo.py             # URI через urllib.parse для сравнения
├── .github/
│   └── workflows/
│       └── pages.yml           # публикация web/ на GitHub Pages
├── report/                     # сохранённые выводы программ
├── Makefile
├── NAMING.md                   # исправление стиля и семантики имён
├── REPORT.md                   # полный отчёт
├── COMMANDS.md                 # все команды сборки, запуска и проверки
├── DEFENSE.md                  # сценарий защиты и вопросы с ответами
└── README.md
```

## Сборка и запуск

Все команды выполняются из корня репозитория.

```sh
make strings       # собрать ascii, utf8, types
make probes        # собрать C-проверки Unicode-идентификаторов
make regex         # собрать generator
make all           # strings + regex + web
```

### Часть I. Байты, символы, кодировки

```sh
make run-strings
# или по отдельности:
./out/ascii
./out/utf8
./out/types
python3 strings/encoding.py
python3 strings/base64_demo.py
```

Ручная сборка одного файла:

```sh
gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 strings/ascii.c -o out/ascii
./out/ascii
```

HTML-сущности:

```sh
open strings/entities.html        # macOS
# или: python3 -m http.server 8000 и открыть /strings/entities.html
```

### Часть II. Генератор и регулярные выражения

```sh
make regex/VPD_Lab3.txt
./out/generator > regex/VPD_Lab3.txt   # команда из задания
python3 regex/regex.py
```

`make regex/VPD_Lab3.txt` дополнительно проверяет, что контрольная
последовательность встречается ровно три раза, и пишет
`report/generator_check.txt`. Генератор детерминирован: фиксированное зерно
PRNG делает файл и отчёт воспроизводимыми.

### Часть III. HTML/JavaScript-валидация

```sh
open web/index.html
# или:
python3 -m http.server 8000
# затем открыть http://localhost:8000/web/index.html
node web/validation.test.js
```

Опубликованная версия формы: https://supersusik.github.io/VPD_Lab3/

В форме есть кнопка «Заполнить валидный пример» и кнопка «Проверить набор
примеров». Ошибки подсвечиваются на месте, без перезагрузки страницы.

### Часть IV. URI и percent-encoding

```sh
node web/uri_demo.js
python3 web/uri_demo.py
```

### Полная перегенерация отчёта

```sh
make -B report      # принудительно пересобрать все сохранённые выводы
# или:
make clean && make report && make run
```

## Ключевые результаты

| Что | Результат |
|---|---|
| `sizeof("Hello")` / `strlen("Hello")` | 6 / 5; разница — завершающий `'\0'` |
| `strlen("Привет")` | 12 байт UTF-8, а не 6 букв |
| `sizeof(wchar_t)` на macOS | 4 байта; на Windows обычно 2 |
| UTF-32 для `大学` | 8 байт (два скаляра по 4 байта) |
| BOM в `utf-32` | `FF FE 00 00` + LE-данные на этой машине |
| `0xB8` | `ё` в cp1251; в UTF-8 — ошибка, корректно `D1 91` |
| Base64 для `大学` | `5aSn5a2m` (6 байт UTF-8 → 8 ASCII-символов) |
| Base64URL для `FB FF EF 01 02` | `-__vAQI=` вместо `+//vAQI=` |
| Контрольная последовательность | `73108121978311799104107111118`, 3 вхождения |
| `VPD_Lab3.txt` | 100 087 байт (100 000 цифр + 3×29) |
| Степени двойки | 43 116 неперекрывающихся вхождений (сумма по 2^0…2^64) |
| `VPD_Lab3_final.txt` | 57 039 байт |
| Проверки формы | 15/15 автоматических примеров |
| Percent-encoding группы | `%D0%9C3%D0%9E-119%D0%91%D0%92-26` |

Подробные таблицы, объяснения и сырые выводы — в [REPORT.md](REPORT.md) и
каталоге [`report/`](report/). Правила нейминга и исправленные примеры —
в [NAMING.md](NAMING.md). Все команды — в [COMMANDS.md](COMMANDS.md),
подготовка к защите — в [DEFENSE.md](DEFENSE.md).

## Важные ограничения

* `wchar_t` не равен UTF-32 по стандарту: размер и модель wide characters
  зависят от реализации.
* Base64 — не кодировка Unicode, а представление произвольных байтов
  ASCII-текстом. Сначала текст кодируется, например, в UTF-8.
* Упрощённая проверка e-mail не реализует полностью RFC 5322.
* Регулярное выражение проверяет форму даты, но существование даты
  проверяется отдельно через `Date`.
* Для реальных URI нужен специализированный парсер (`new URL()`,
  `urllib.parse`), а не самописная регулярка.
* Приблизительный счётчик графемных кластеров не реализует все правила
  UAX #29 (флаги, keycap, модификаторы тона кожи).
