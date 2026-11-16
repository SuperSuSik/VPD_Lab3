#!/usr/bin/env python3
"""ЛР3, часть IV: URI-разбор через urllib.parse для сравнения с JavaScript."""

from __future__ import annotations

import sys
from urllib.parse import parse_qsl, quote, unquote, urlsplit


URI = (
    "https://example.org:8443/api/v1/student-profile?"
    "id=304&group=%D0%9C3%D0%9E-304%D0%91%D0%92-26#results"
)


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    configure_stdout()
    parts = urlsplit(URI)
    params = parse_qsl(parts.query, keep_blank_values=True)

    print("=== URI: Python urllib.parse ===")
    print(f"scheme   : {parts.scheme}")
    print(f"netloc   : {parts.netloc}")
    print(f"hostname : {parts.hostname}")
    print(f"port     : {parts.port}")
    print(f"path     : {parts.path}")
    print(f"query    : {parts.query}")
    print(f"fragment : {parts.fragment}")
    for key, value in params:
        print(f"query    : {key} = {value}")

    group = "М3О-119БВ-26"
    encoded = quote(group, safe="-")
    decoded = unquote(encoded)

    print("\n=== percent-encoding в Python ===")
    print(f"group          : {group}")
    print(f"quote(group)   : {encoded}")
    print(f"unquote        : {decoded}")
    print(f"round trip     : {decoded == group}")
    print(f"UTF-8 bytes    : {group.encode('utf-8').hex(' ').upper()}")

    print("\nСравнение: JavaScript URL и Python urllib.parse дают одинаковые")
    print("компоненты; percent-encoding зависит от набора safe-символов.")
    print("Для реальных URI оба специализированных парсера предпочтительнее")
    print("самописной регулярки.")


if __name__ == "__main__":
    main()
