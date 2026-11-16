#!/usr/bin/env python3
"""ЛР3, разделы 2.6, 2.7, 2.9, 2.11 и дополнительные задания.

Демонстрирует:
  * UTF-8 / UTF-16 / UTF-32 LE / UTF-32 BE для пяти строк;
  * BOM в общем варианте UTF-32;
  * байт 0xB8 в cp1251 и UTF-8;
  * гомоглифы «М/О» (кириллица) и «M/O» (латиница);
  * HTML-сущности для «ё»;
  * ручной подсчёт кодовых точек UTF-8 и приблизительный подсчёт
    графемных кластеров.
"""

from __future__ import annotations

import sys
import unicodedata


SAMPLES = ["Hello", "Привет", "ёж", "大学", "     "]


def configure_stdout() -> None:
    """Принудительно печатаем в UTF-8, чтобы вывод не зависел от локали."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def hex_bytes(data: bytes) -> str:
    return data.hex(" ").upper()


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def utf8_code_points(data: bytes) -> list[int]:
    """Строгий декодер UTF-8 без готовой Unicode-библиотеки.

    Проверяет continuation-байты, overlong-формы, суррогаты и предел
    U+10FFFF. Возвращает список скалярных значений Unicode.
    """
    result: list[int] = []
    i = 0
    minimum = {1: 0x00, 2: 0x80, 3: 0x800, 4: 0x10000}

    while i < len(data):
        first = data[i]

        if first < 0x80:
            width, code_point = 1, first
        elif 0xC2 <= first <= 0xDF:
            width, code_point = 2, first & 0x1F
        elif 0xE0 <= first <= 0xEF:
            width, code_point = 3, first & 0x0F
        elif 0xF0 <= first <= 0xF4:
            width, code_point = 4, first & 0x07
        else:
            raise ValueError(f"invalid UTF-8 start byte 0x{first:02X} at {i}")

        if i + width > len(data):
            raise ValueError(f"truncated UTF-8 sequence at {i}")

        for offset in range(1, width):
            continuation = data[i + offset]
            if continuation & 0xC0 != 0x80:
                raise ValueError(
                    f"invalid continuation byte 0x{continuation:02X} at {i + offset}"
                )
            code_point = (code_point << 6) | (continuation & 0x3F)

        if code_point < minimum[width]:
            raise ValueError(f"overlong UTF-8 sequence at {i}")
        if 0xD800 <= code_point <= 0xDFFF:
            raise ValueError(f"UTF-8 surrogate at {i}")
        if code_point > 0x10FFFF:
            raise ValueError(f"code point above U+10FFFF at {i}")

        result.append(code_point)
        i += width

    return result


def grapheme_clusters_approx(text: str) -> int:
    """Приблизительное число графемных кластеров.

    Учитывает комбинируемые знаки, variation selectors и ZWJ. Это не полная
    реализация UAX #29: флаги, keycap-последовательности и модификаторы тона
    кожи здесь не объединяются.
    """
    count = 0
    join_next = False

    for char in text:
        code_point = ord(char)

        if code_point == 0x200D:  # ZERO WIDTH JOINER
            join_next = True
            continue
        if join_next:
            join_next = False
            continue
        if unicodedata.combining(char):
            continue
        if 0xFE00 <= code_point <= 0xFE0F:  # variation selectors
            continue
        if 0xE0100 <= code_point <= 0xE01EF:  # variation selectors supplement
            continue

        count += 1

    return count


def main() -> None:
    configure_stdout()

    section("2.6. UTF-8, UTF-16 и UTF-32 LE/BE для пяти строк")
    print(f"{'text':<12} {'UTF-8':>7} {'UTF-16 LE':>10} {'UTF-16 BE':>10} "
          f"{'UTF-32 LE':>10} {'UTF-32 BE':>10}")
    print("-" * 78)

    for text in SAMPLES:
        utf8 = text.encode("utf-8")
        utf16le = text.encode("utf-16-le")
        utf16be = text.encode("utf-16-be")
        utf32le = text.encode("utf-32-le")
        utf32be = text.encode("utf-32-be")
        print(f"{text!r:<12} {len(utf8):>7} {len(utf16le):>10} {len(utf16be):>10} "
              f"{len(utf32le):>10} {len(utf32be):>10}")
        print(f"  UTF-8     : {hex_bytes(utf8)}")
        print(f"  UTF-16 LE : {hex_bytes(utf16le)}")
        print(f"  UTF-16 BE : {hex_bytes(utf16be)}")
        print(f"  UTF-32 LE : {hex_bytes(utf32le)}")
        print(f"  UTF-32 BE : {hex_bytes(utf32be)}")

    print("\nUTF-8 переменной длины: ASCII — 1 байт, кириллица — 2, "
          "иероглифы — 3.")
    print("UTF-16: BMP-символы — 2 байта (суррогатная пара — 4).")
    print("UTF-32: всегда 4 байта на скалярное значение; цена — память.")

    section("2.6. BOM и порядок байтов в UTF-32")
    text = "大学"
    generic = text.encode("utf-32")
    little = text.encode("utf-32-le")
    big = text.encode("utf-32-be")

    print(f"utf-32    : {hex_bytes(generic)}")
    print(f"utf-32-le : {hex_bytes(little)}")
    print(f"utf-32-be : {hex_bytes(big)}")
    print(f"sys.byteorder = {sys.byteorder}")

    if generic.startswith(b"\xff\xfe\x00\x00"):
        print("BOM: FF FE 00 00 — UTF-32 little-endian (BOM присутствует).")
    elif generic.startswith(b"\x00\x00\xfe\xff"):
        print("BOM: 00 00 FE FF — UTF-32 big-endian (BOM присутствует).")
    else:
        print("BOM не найден.")

    print("BOM сообщает порядок 32-битных кодовых единиц. Явные utf-32-le/be")
    print("BOM не добавляют: порядок уже задан именем кодировки.")

    section("2.7. История одного байта: 0xB8")
    data = bytes([0xB8])
    print(f"data = {hex_bytes(data)}")

    decoded_cp1251 = data.decode("cp1251")
    print(f"cp1251: {decoded_cp1251!r}, U+{ord(decoded_cp1251):04X} "
          f"({unicodedata.name(decoded_cp1251)})")

    try:
        print(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        print(f"UTF-8 error: {error}")

    print("\nБуква «ё» в трёх представлениях:")
    print(f"  cp1251    : {hex_bytes('ё'.encode('cp1251'))}")
    print(f"  UTF-8     : {hex_bytes('ё'.encode('utf-8'))}")
    print(f"  UTF-32 LE : {hex_bytes('ё'.encode('utf-32-le'))}")

    print("\n0xB8 — однобайтовый код «ё» только в Windows-1251. В UTF-8")
    print("байт 0xB8 — continuation-байт (10xxxxxx), а не начало символа;")
    print("поэтому отдельно он не образует корректную UTF-8-последовательность.")
    print("Корректная UTF-8-запись «ё»: D1 91 (два байта).")

    section("2.9. Гомоглифы: кириллические М/О и латинские M/O")
    cyrillic = "М3О-304БВ-26"
    latin = "M3O-304БВ-26"

    for label, value in (("кириллица", cyrillic), ("латиница ", latin)):
        codes = [f"U+{ord(ch):04X}" for ch in value[:3]]
        names = [unicodedata.name(ch, "?") for ch in value[:3]]
        print(f"{label}: {value}")
        print(f"  первые 3 кода: {', '.join(codes)}")
        print(f"  имена:         {', '.join(names)}")
        print(f"  UTF-8:         {hex_bytes(value.encode('utf-8'))}")

    print(f"\nстроки равны: {cyrillic == latin}")
    print(f"равны после NFKC: "
          f"{unicodedata.normalize('NFKC', cyrillic) == unicodedata.normalize('NFKC', latin)}")
    print("NFKC не устраняет гомоглифы: это разные кодовые точки с похожими")
    print("начертаниями. Для безопасности нужны политики смешанных алфавитов,")
    print("confusable-проверки и ограничения на домены/идентификаторы.")

    section("2.11. HTML: один символ в трёх представлениях")
    yo = "ё"
    print(f"обычный символ: {yo}")
    print("HTML dec:       &#1105;")
    print("HTML hex:       &#x451;")
    print(f"кодовая точка:  U+{ord(yo):04X} = {ord(yo)}")
    print(f"UTF-8:          {hex_bytes(yo.encode('utf-8'))}")
    print("Все три HTML-записи ссылаются на один и тот же U+0451.")

    section("Дополнительно: байты, кодовые точки и графемные кластеры")
    examples = [
        "Hello",
        "Привет",
        "ёж",
        "大学",
        "е\u0301",           # е + combining acute
        "👨\u200d👩\u200d👧\u200d👦",  # семейный эмодзи (ZWJ)
        "🇷🇺",                # флаг (два regional indicator)
    ]

    print(f"{'text':<16} {'bytes':>6} {'code points':>12} {'graphemes≈':>11}")
    print("-" * 52)
    for value in examples:
        encoded = value.encode("utf-8")
        points = utf8_code_points(encoded)
        clusters = grapheme_clusters_approx(value)
        label = value if len(value) <= 12 else value[:9] + "..."
        print(f"{label!r:<16} {len(encoded):>6} {len(points):>12} {clusters:>11}")

    print("\nРучной декодер проверил UTF-8 без сторонних Unicode-библиотек.")
    print("Ограничения приблизительного счётчика графем: не реализованы все")
    print("правила UAX #29 (флаги, keycap, модификаторы тона кожи). Для")
    print("продакшена нужен специализированный segmentation API.")

    print("\nPython len(str) считает кодовые точки, len(bytes) — байты, а")
    print("визуальные глифы требуют анализа графемных кластеров.")


if __name__ == "__main__":
    main()
