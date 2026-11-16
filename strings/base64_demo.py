#!/usr/bin/env python3
"""ЛР3, раздел 2.8: Base64 — кодирование байтов в текст.

Base64 не является символьной кодировкой Unicode. Сначала текст нужно
закодировать, например, в UTF-8, а затем байты представить в Base64.
"""

from __future__ import annotations

import base64
import hashlib
import math
import sys
import tempfile
from pathlib import Path


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    configure_stdout()

    section("2.8. Полный цикл: Unicode → UTF-8 → Base64 → байты → Unicode")
    text = "大学"
    utf8 = text.encode("utf-8")
    encoded = base64.b64encode(utf8)
    decoded_bytes = base64.b64decode(encoded)
    decoded_text = decoded_bytes.decode("utf-8")

    print(f"Text:          {text}")
    print(f"UTF-8 bytes:   {utf8.hex(' ').upper()} ({len(utf8)} байт)")
    print(f"Base64:        {encoded.decode('ascii')} ({len(encoded)} символов)")
    print(f"Decoded bytes: {decoded_bytes.hex(' ').upper()}")
    print(f"Decoded text:  {decoded_text}")
    print(f"Совпадение:    {decoded_bytes == utf8 and decoded_text == text}")

    print("\nЦепочка:")
    print("Unicode text → UTF-8 bytes → Base64 ASCII text → bytes → "
          "UTF-8 decode → Unicode text")

    section("Формула длины и накладные расходы")
    print("Для n байтов длина Base64 без переносов: 4 × ceil(n / 3).")
    print(f"{'n':>4} {'Base64 length':>14} {'4*ceil(n/3)':>12} {'overhead':>10}")
    print("-" * 46)

    for n in range(1, 10):
        raw = b"A" * n
        b64 = base64.b64encode(raw).decode("ascii")
        formula = 4 * math.ceil(n / 3)
        overhead = (len(b64) / n - 1) * 100
        print(f"{n:>4} {len(b64):>14} {formula:>12} {overhead:>9.2f}%")

    for n in (100, 1_000, 100_000):
        formula = 4 * math.ceil(n / 3)
        print(f"{n:>4} {formula:>14} {formula:>12} "
              f"{(formula / n - 1) * 100:>9.2f}%")

    section("Padding '=' на длинах, не кратных трём")
    for raw in (b"A", b"AB", b"ABC", b"ABCD", b"ABCDE"):
        b64 = base64.b64encode(raw).decode("ascii")
        padding = b64.count("=")
        print(f"{raw!r:<8} ({len(raw)} байт) -> {b64:<8} padding={padding}")

    print("\n1 входной байт → 2 символа + '=='; 2 байта → 3 символа + '=';")
    print("3 байта → ровно 4 символа без padding.")

    section("Обычный Base64 и URL-safe Base64")
    raw = bytes([251, 255, 239, 1, 2])
    standard = base64.b64encode(raw).decode("ascii")
    url_safe = base64.urlsafe_b64encode(raw).decode("ascii")

    print(f"raw bytes:        {raw.hex(' ').upper()}")
    print(f"base64:           {standard}")
    print(f"urlsafe_b64encode:{url_safe}")
    print(f"URL-safe replace: '+' -> '-', '/' -> '_'; '=' может сохраняться")
    print(f"decode standard:  {base64.b64decode(standard).hex(' ').upper()}")
    print(f"decode url-safe:  {base64.urlsafe_b64decode(url_safe).hex(' ').upper()}")

    section("Проверка полного круга на маленьком бинарном файле")
    raw_file = bytes(range(256)) + b"VPD-Lab3-Base64"
    expected_hash = hashlib.sha256(raw_file).hexdigest()

    with tempfile.TemporaryDirectory(prefix="vpd_lab3_base64_") as directory:
        source = Path(directory) / "source.bin"
        encoded_file = Path(directory) / "source.bin.b64"
        restored = Path(directory) / "restored.bin"

        source.write_bytes(raw_file)
        encoded_file.write_text(
            base64.b64encode(source.read_bytes()).decode("ascii") + "\n",
            encoding="ascii",
        )
        restored.write_bytes(base64.b64decode(encoded_file.read_text("ascii")))

        restored_hash = hashlib.sha256(restored.read_bytes()).hexdigest()

        print(f"исходный файл:     {source.name}, {source.stat().st_size} байт")
        print(f"Base64-файл:       {encoded_file.name}, "
              f"{encoded_file.stat().st_size} байт")
        print(f"восстановленный:   {restored.name}, {restored.stat().st_size} байт")
        print(f"SHA-256 исходный:  {expected_hash}")
        print(f"SHA-256 восстановл.: {restored_hash}")
        print(f"файлы совпадают:   {restored.read_bytes() == raw_file}")

    print("\nПочему Base64 удобен в JSON/API: JSON-строка должна быть")
    print("текстом, а Base64 использует только ASCII-символы и не ломается")
    print("при передаче через текстовые каналы. Это не значит, что бинарные")
    print("данные всегда нужно хранить в БД как текст: бинарный тип СУБД")
    print("обычно компактнее и не требует лишнего кодирования/декодирования.")


if __name__ == "__main__":
    main()
