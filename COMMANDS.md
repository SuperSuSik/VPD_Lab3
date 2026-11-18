# Команды ЛР3 — полный справочник

Все команды выполняются **из корня репозитория**:

```sh
cd /Users/cts/VPD_Lab3
```

На macOS системная команда `gcc` — это Apple clang, поэтому в `Makefile`
явно выбран `gcc-16`. На Linux: `make CC=gcc`.

---

## 0. Быстрый старт

```sh
cd /Users/cts/VPD_Lab3
make clean && make -B report && make run   # полная сборка, отчёт и проверки
open web/index.html                        # локальная форма
```

Сайт: <https://supersusik.github.io/VPD_Lab3/>

---

## 1. Проверка окружения

```sh
sw_vers
uname -m
gcc-16 --version | head -1
clang --version | head -1
python3 --version
node --version
make --version | head -1
locale
```

Если `gcc-16` нет:

```sh
brew install gcc
# или собрать системным компилятором:
make CC=gcc
```

---

## 2. Сборка

```sh
make all        # strings + regex + web
make strings    # out/ascii, out/utf8, out/types
make regex      # out/generator
make probes     # out/unicode_identifiers_gcc, out/unicode_identifiers_clang
make web        # web/ статический, сборки нет (no-op)
make clean      # удалить out/ и __pycache__
make distclean  # clean + удалить report/
```

Ручная сборка одного файла:

```sh
mkdir -p out
gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 strings/ascii.c -o out/ascii
gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 strings/utf8.c -o out/utf8
gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 strings/types.c -o out/types
gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 regex/generator.c -o out/generator
clang  -std=c17 -Wall -Wextra -Wpedantic -O2 strings/unicode_identifiers.c \
       -o out/unicode_identifiers_clang
```

---

## 3. Часть I. Байты, символы, кодировки

```sh
make run-strings

# то же по отдельности:
./out/ascii
./out/utf8
./out/types
python3 strings/encoding.py
python3 strings/base64_demo.py
```

Сохранённые выводы:

```sh
cat report/ascii.txt
cat report/utf8.txt
cat report/types.txt
cat report/encoding.txt
cat report/base64.txt
```

HTML-сущности:

```sh
open strings/entities.html
# или локальный сервер:
python3 -m http.server 8000
# затем http://localhost:8000/strings/entities.html
```

### Байты вживую

```sh
printf 'Привет' | xxd -g1
printf 'ё' | xxd -g1
printf '大学' | xxd -g1
xxd -g1 regex/VPD_Lab3.txt | head
```

Ожидаемо: `Привет` — 12 байт, `ё` — `d1 91`, `大学` — `e5 a4 a7 e5 ad a6`.

### Проверки Python

```sh
python3 -c 'print(len("Привет"), len("Привет".encode("utf-8")))'          # 6 12
python3 -c 'print("ё".encode("cp1251").hex(), "ё".encode("utf-8").hex(" "))'  # b8 d1 91
python3 -c 'print("ё".encode("utf-32").hex(" "))'                          # ff fe 00 00 51 04 00 00
python3 -c 'import base64; print(base64.b64encode("大学".encode()).decode())'  # 5aSn5a2m
python3 -c 'import base64; print(base64.b64decode("5aSn5a2m").decode())'       # 大学
```

### Гомоглифы

```sh
python3 -c 'print(hex(ord("М")), hex(ord("M")))'   # 0x41c 0x4d
python3 -c 'import unicodedata; print(unicodedata.name("М"), "|", unicodedata.name("M"))'
```

### Unicode-идентификаторы

```sh
make probes
./out/unicode_identifiers_gcc
./out/unicode_identifiers_clang
python3 strings/unicode_identifiers.py
node strings/unicode_identifiers.js
```

---

## 4. Часть II. Генератор и регулярные выражения

```sh
make regex
./out/generator --print-control        # 73108121978311799104107111118
./out/generator > regex/VPD_Lab3.txt   # 100087 байт
wc -c regex/VPD_Lab3.txt
```

Проверка трёх вхождений:

```sh
grep -o "$(./out/generator --print-control)" regex/VPD_Lab3.txt | wc -l   # 3
grep -bo "$(./out/generator --print-control)" regex/VPD_Lab3.txt          # 0, 50029, 100058
cat report/generator_check.txt
```

Другие параметры генератора:

```sh
./out/generator --digits 200000 --seed 42 > /tmp/big.txt
./out/generator --digits -1;  echo $?   # error, код 2
./out/generator --seed 0;     echo $?   # error, код 2
```

Полный анализ и удаление степеней двойки:

```sh
python3 regex/regex.py                 # печатает таблицу и пишет final-файл
make regex/VPD_Lab3_final.txt
wc -c regex/VPD_Lab3_final.txt         # 57039
tail -40 report/regex.txt
```

Только проверка через Makefile:

```sh
make regex/VPD_Lab3.txt
make report/generator_check.txt
make regex/VPD_Lab3_final.txt
```

---

## 5. Часть III. HTML/JavaScript-валидация

```sh
open web/index.html
# или:
python3 -m http.server 8000
# затем http://localhost:8000/web/index.html

node web/validation.test.js
cat report/web_validation.txt
```

Проверки правил вживую:

```sh
# Группа: кириллица проходит, латинские гомоглифы — нет
node -e 'const re=/^М3О-\d{3}БВ-\d{2}$/u;
console.log(re.test("М3О-119БВ-26"), re.test("M3O-119BV-26"))'   # true false

# Дата: форма верна, но даты не существует
node -e 'const s="2026-02-31";
const p=new Date(s+"T00:00:00Z");
console.log(/^\d{4}-\d{2}-\d{2}$/.test(s), p.toISOString().slice(0,10)===s)'  # true false

# URI: только http/https
node -e 'for (const s of ["https://example.org","ftp://example.org","not a uri"]) {
  try { const u=new URL(s);
    console.log(s, "->", u.protocol, ["http:","https:"].includes(u.protocol) ? "OK" : "REJECT");
  } catch { console.log(s, "-> parse error"); }
}'
```

---

## 6. Часть IV. URI и percent-encoding

```sh
node web/uri_demo.js
python3 web/uri_demo.py
cat report/uri.txt
cat report/uri_python.txt
```

Однострочники:

```sh
node -e 'console.log(encodeURIComponent("М3О-119БВ-26"))'
node -e 'console.log(decodeURIComponent("%D0%9C3%D0%9E-119%D0%91%D0%92-26"))'
node -e 'const u=new URL("https://example.org:8443/api/v1/student-profile?id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results");
console.log(u.protocol, u.hostname, u.port, u.pathname);
console.log(u.searchParams.get("id"), u.searchParams.get("group"), u.hash)'
```

---

## 7. Отчёт

```sh
make report                 # дособрать отсутствующее
make -B report              # принудительно перегенерировать всё
make regenerate             # то же, что report
make versions               # принудительно обновить report/versions.txt

ls -l report
cat report/versions.txt
```

Полный лог с кодом возврата:

```sh
make -B report > /tmp/report.log 2>&1; echo "rc=$?"
tail -30 /tmp/report.log
```

---

## 8. Полная проверка с нуля

```sh
make clean && make -B report && make run
echo "rc=$?"

node --check web/validation.js
node --check web/uri.js
node --check web/uri_demo.js
node --check web/validation.test.js
node --check strings/unicode_identifiers.js

python3 -m py_compile strings/*.py regex/regex.py web/*.py
echo "py_compile rc=$?"

git status --short
```

Ожидаемые ключевые строки:

```text
Пройдено проверок: 15/15
Совпадение query-параметров: true
Все утверждения assert пройдены.
```

---

## 9. Git

```sh
git status
git log --oneline --decorate -12
git diff
git diff --stat
git add -A
git commit -m "lab3: ..."
git push origin main
```

Синхронизация с remote:

```sh
git fetch origin
git rev-parse HEAD origin/main
git status -sb
```

---

## 10. Сайт GitHub Pages

```sh
open https://supersusik.github.io/VPD_Lab3/
curl -sI https://supersusik.github.io/VPD_Lab3/ | head -5
```

Публикация обновляется автоматически при `git push`, если изменён
`web/**` или `.github/workflows/pages.yml`. Workflow:
`.github/workflows/pages.yml`, прогоны:
<https://github.com/SuperSuSik/VPD_Lab3/actions>.

`gh` в системе не установлен. Если нужен:

```sh
brew install gh
gh auth login
gh repo view SuperSuSik/VPD_Lab3 --web
```

---

## 11. Диагностика

| Симптом | Решение |
|---|---|
| `gcc-16: command not found` | `brew install gcc` или `make CC=gcc` |
| `clang: command not found` | `xcode-select --install` |
| `node: command not found` | `brew install node` |
| Краковяки вместо кириллицы | `export LC_ALL=en_US.UTF-8`, `export PYTHONIOENCODING=utf-8` |
| `make: Nothing to be done for 'web'` | Это нормально: `web/` статический |
| Порт 8000 занят | `python3 -m http.server 8080` |
| Отчёт не обновляется | `make -B report` |
| Нужно вернуть сгенерированные файлы | `git checkout -- regex/VPD_Lab3.txt regex/VPD_Lab3_final.txt` |
| Сбросить всё сборочное | `make clean` (report/ сохраняется) |

---

## 12. Шпаргалка: команда → ожидаемый результат

| Проверка | Команда | Ожидаемо |
|---|---|---|
| `sizeof`/`strlen` | `./out/ascii` | 6 / 5 |
| `strlen("Привет")` | `./out/utf8` | 12 |
| `sizeof(wchar_t)` | `./out/utf8` | 4 |
| `0xB8` в cp1251 | `python3 strings/encoding.py` | `ё`, U+0451 |
| Base64 `大学` | `python3 strings/base64_demo.py` | `5aSn5a2m` |
| Control sequence | `./out/generator --print-control` | `73108121978311799104107111118` |
| Вхождений control | `grep -o ... \| wc -l` | 3 |
| Размер исходника | `wc -c regex/VPD_Lab3.txt` | 100087 |
| Степени двойки | `python3 regex/regex.py` | ИТОГО 43116 |
| Размер после `re.sub` | `wc -c regex/VPD_Lab3_final.txt` | 57039 |
| Форма | `node web/validation.test.js` | 15/15 |
| URI-парсеры | `node web/uri_demo.js` | `true` |
| Percent-encoding | `node web/uri_demo.js` | `%D0%9C3%D0%9E-119%D0%91%D0%92-26` |
