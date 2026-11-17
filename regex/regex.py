#!/usr/bin/env python3
"""ЛР3, разделы 3.3–3.5: регулярные выражения и степени двойки.

Скрипт:
  1. читает VPD_Lab3.txt;
  2. для каждого 2^n, n = 0..64, считает неперекрывающиеся вхождения
     через re.findall(re.escape(value), text);
  3. удаляет степени двойки через re.sub() от 2^64 к 2^0 и сохраняет
     VPD_Lab3_final.txt;
  4. показывает размеры файлов и суммарное число совпадений;
  5. сравнивает обычный и перекрывающийся поиск;
  6. дополнительно демонстрирует режимы re.ASCII и Unicode для \\w.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "VPD_Lab3.txt"
RESULT = BASE_DIR / "VPD_Lab3_final.txt"


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> int:
    configure_stdout()

    if not SOURCE.exists():
        print(f"error: {SOURCE} not found", file=sys.stderr)
        print("Сначала запустите: make regex/VPD_Lab3.txt", file=sys.stderr)
        return 1

    text = SOURCE.read_text(encoding="utf-8").strip()
    if not text:
        print(f"error: {SOURCE} is empty", file=sys.stderr)
        return 1
    if not text.isdigit():
        print("error: source contains non-digit characters", file=sys.stderr)
        return 1

    powers = [str(2 ** n) for n in range(65)]
    counts: list[tuple[int, str, int]] = []

    section("3.3. Вхождения десятичных записей 2^0 … 2^64")
    print(f"{'n':>2}  {'2^n':>21}  {'вхождений':>10}")
    print("-" * 40)

    for exponent, value in enumerate(powers):
        count = len(re.findall(re.escape(value), text))
        counts.append((exponent, value, count))
        print(f"{exponent:>2}  {value:>21}  {count:>10}")

    total_found = sum(count for _, _, count in counts)
    print("-" * 40)
    print(f"{'':>2}  {'ИТОГО':>21}  {total_found:>10}")

    section("3.4. Удаление степеней двойки от 2^64 к 2^0")
    result = text
    for _, value, _ in reversed(counts):
        result = re.sub(re.escape(value), "", result)

    RESULT.write_text(result, encoding="utf-8")

    source_size = SOURCE.stat().st_size
    result_size = RESULT.stat().st_size
    removed = len(text) - len(result)

    print(f"исходный файл:      {SOURCE.name} — {source_size} байт")
    print(f"результат:          {RESULT.name} — {result_size} байт")
    print(f"найдено совпадений: {total_found}")
    print(f"удалено символов:   {removed}")
    print(f"осталось символов:  {len(result)}")
    print("Сумма вхождений по отдельным шаблонам может быть больше числа")
    print("удалённых символов: совпадения разных степеней пересекаются.")

    print("\nПочему порядок важен:")
    print("  Если удалить короткую запись раньше длинной, она может уничтожить")
    print("  часть длинной записи. Например, удаление «2» до «1024» разрывает")
    print("  «1024» на «104», и длинный шаблон уже не будет найден. Поэтому")
    print("  обработка идёт от 2^64 (самые длинные строки) к 2^0.")

    section("3.5. Обычный и перекрывающийся поиск")
    pattern_text = "1024"
    escaped = re.escape(pattern_text)
    normal = re.findall(escaped, text)
    overlapping = re.findall(rf"(?=({escaped}))", text)
    print(f"шаблон: {pattern_text}")
    print(f"обычный re.findall:        {len(normal)}")
    print(f"lookahead (?=(...)):       {len(overlapping)}")
    print("На случайных данных перекрытий может не быть; сравнение ниже")
    print("показывает разницу на специально построенной строке.")

    synthetic = "101010"
    synthetic_normal = re.findall(re.escape("1010"), synthetic)
    synthetic_overlapping = re.findall(r"(?=(1010))", synthetic)
    print(f"\nсинтетическая строка:      {synthetic!r}")
    print(f"шаблон:                    '1010'")
    print(f"обычный re.findall:        {len(synthetic_normal)}")
    print(f"lookahead (?=(...)):       {len(synthetic_overlapping)}")
    print("re.findall() не возвращает перекрывающиеся совпадения;")
    print("позитивная опережающая проверка возвращает их за счёт группы.")

    section("Дополнительно: re.ASCII и Unicode-режим для \\w")
    sample = "Привет 304 privet_304"
    unicode_words = re.findall(r"\w+", sample)
    ascii_words = re.findall(r"\w+", sample, re.ASCII)
    print(f"строка:       {sample!r}")
    print(f"Unicode \\w+:  {unicode_words}")
    print(f"re.ASCII \\w+: {ascii_words}")
    print("В Unicode-режиме \\w включает кириллицу, в re.ASCII — только")
    print("латинские буквы, цифры и подчёркивание.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
