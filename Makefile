# Лабораторная работа №3: строки, кодировки, Base64, регулярные выражения, URI.
#
# На macOS системный gcc — это Apple clang, поэтому по умолчанию используется
# Homebrew GCC. На Linux достаточно `make CC=gcc`.

# := (а не ?=) важно: GNU Make уже определяет CC=cc; командная строка
# по-прежнему может переопределить значение: make CC=gcc.
CC       := gcc-16
CLANG    ?= clang
CFLAGS   ?= -std=c17 -Wall -Wextra -Wpedantic -O2
PYTHON   ?= python3
NODE     ?= node
MKDIR    := mkdir -p

OUT      := out
REPORT   := report
STRINGS  := strings
REGEX    := regex
WEB      := web

C_BINS   := $(OUT)/ascii $(OUT)/utf8 $(OUT)/types $(OUT)/generator \
            $(OUT)/unicode_identifiers_gcc $(OUT)/unicode_identifiers_clang

.PHONY: all strings regex web probes run run-strings run-regex report regenerate \
        versions clean distclean

all: strings regex web

# ---------------------------------------------------------------------------
# Сборка
# ---------------------------------------------------------------------------

$(OUT):
	$(MKDIR) $(OUT)

$(OUT)/ascii: $(STRINGS)/ascii.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/utf8: $(STRINGS)/utf8.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/types: $(STRINGS)/types.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/generator: $(REGEX)/generator.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/unicode_identifiers_gcc: $(STRINGS)/unicode_identifiers.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/unicode_identifiers_clang: $(STRINGS)/unicode_identifiers.c | $(OUT)
	$(CLANG) $(CFLAGS) $< -o $@

strings: $(OUT)/ascii $(OUT)/utf8 $(OUT)/types
regex: $(OUT)/generator
web:
probes: $(OUT)/unicode_identifiers_gcc $(OUT)/unicode_identifiers_clang

# ---------------------------------------------------------------------------
# Запуск демонстраций
# ---------------------------------------------------------------------------

run-strings: strings
	./$(OUT)/ascii
	./$(OUT)/utf8
	./$(OUT)/types
	$(PYTHON) $(STRINGS)/encoding.py
	$(PYTHON) $(STRINGS)/base64_demo.py

run-regex: regex
	./$(OUT)/generator > $(REGEX)/VPD_Lab3.txt
	$(PYTHON) $(REGEX)/regex.py

run: run-strings run-regex probes
	$(NODE) $(WEB)/validation.test.js
	$(NODE) $(WEB)/uri_demo.js
	$(PYTHON) $(WEB)/uri_demo.py

# ---------------------------------------------------------------------------
# Генерация файлов задания и сохранённых выводов
# ---------------------------------------------------------------------------

# Детерминированный генератор: фиксированное зерно делает отчёт воспроизводимым.
$(REGEX)/VPD_Lab3.txt: $(OUT)/generator
	@$(MKDIR) $(REPORT)
	./$(OUT)/generator > $@
	@control=$$(./$(OUT)/generator --print-control); \
	count=$$(grep -o "$$control" $@ | wc -l | tr -d ' '); \
	bytes=$$(wc -c < $@ | tr -d ' '); \
	printf 'control=%s\noccurrences=%s\nbytes=%s\nrandom_digits=100000\n' \
	  "$$control" "$$count" "$$bytes" > $(REPORT)/generator_check.txt; \
	test "$$count" = "3" || { echo "control sequence occurs $$count times, expected 3" >&2; exit 1; }

$(REPORT)/ascii.txt: $(OUT)/ascii
	@$(MKDIR) $(REPORT)
	./$(OUT)/ascii > $@

$(REPORT)/utf8.txt: $(OUT)/utf8
	@$(MKDIR) $(REPORT)
	./$(OUT)/utf8 > $@

$(REPORT)/types.txt: $(OUT)/types
	@$(MKDIR) $(REPORT)
	./$(OUT)/types > $@

$(REPORT)/encoding.txt: $(STRINGS)/encoding.py
	@$(MKDIR) $(REPORT)
	$(PYTHON) $(STRINGS)/encoding.py > $@

$(REPORT)/base64.txt: $(STRINGS)/base64_demo.py
	@$(MKDIR) $(REPORT)
	$(PYTHON) $(STRINGS)/base64_demo.py > $@

$(REPORT)/unicode_identifiers.txt: probes
	@$(MKDIR) $(REPORT)
	{ \
	  echo '=== C, GCC ==='; ./$(OUT)/unicode_identifiers_gcc; \
	  echo '=== C, Clang ==='; ./$(OUT)/unicode_identifiers_clang; \
	  echo '=== Python ==='; $(PYTHON) $(STRINGS)/unicode_identifiers.py; \
	  echo '=== JavaScript (Node.js) ==='; $(NODE) $(STRINGS)/unicode_identifiers.js; \
	} > $@

$(REPORT)/regex.txt: $(REGEX)/regex.py $(REGEX)/VPD_Lab3.txt
	@$(MKDIR) $(REPORT)
	$(PYTHON) $(REGEX)/regex.py > $@

$(REPORT)/web_validation.txt: $(WEB)/validation.test.js $(WEB)/validation.js
	@$(MKDIR) $(REPORT)
	$(NODE) $(WEB)/validation.test.js > $@

$(REPORT)/uri.txt: $(WEB)/uri_demo.js $(WEB)/uri.js
	@$(MKDIR) $(REPORT)
	$(NODE) $(WEB)/uri_demo.js > $@

$(REPORT)/uri_python.txt: $(WEB)/uri_demo.py
	@$(MKDIR) $(REPORT)
	$(PYTHON) $(WEB)/uri_demo.py > $@

report: $(REPORT)/ascii.txt $(REPORT)/utf8.txt $(REPORT)/types.txt \
        $(REPORT)/encoding.txt $(REPORT)/base64.txt \
        $(REPORT)/unicode_identifiers.txt $(REPORT)/regex.txt \
        $(REPORT)/web_validation.txt $(REPORT)/uri.txt $(REPORT)/uri_python.txt \
        $(REPORT)/versions.txt

$(REPORT)/versions.txt:
	@$(MKDIR) $(REPORT)
	{ \
	  echo 'date:'; date; \
	  echo 'os:'; sw_vers | sed 's/^/  /'; \
	  echo 'arch:'; uname -m; \
	  echo 'gcc:'; $(CC) --version | head -1; \
	  echo 'clang:'; $(CLANG) --version | head -1; \
	  echo 'python:'; $(PYTHON) --version; \
	  echo 'node:'; $(NODE) --version; \
	  echo 'make:'; make --version | head -1; \
	  echo 'locale:'; locale | head -3; \
	} > $@

# Полная перегенерация данных задания и отчёта.
regenerate: $(REGEX)/VPD_Lab3.txt report
	$(PYTHON) $(REGEX)/regex.py > $(REPORT)/regex.txt

clean:
	rm -rf $(OUT)
	rm -rf $(WEB)/__pycache__ $(STRINGS)/__pycache__ $(REGEX)/__pycache__

# Сохранённые результаты и сгенерированные файлы задания не удаляем:
# они являются частью отчёта.
distclean: clean
	rm -rf $(REPORT)
