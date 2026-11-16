/*
 * ЛР3, разделы 2.2 и 2.4: UTF-8 и wide strings.
 *
 * Главная мысль: strlen() считает байты до '\0', а не видимые символы.
 * wchar_t — платформенно-зависимый целочисленный тип, а не «UTF-32 по
 * стандарту».
 */
#include <locale.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>

static void dump_bytes(const char *label, const char *text, size_t object_size)
{
    printf("%s\n", label);
    printf("  text:        %s\n", text);
    printf("  strlen:      %zu (байты до '\\0', не число глифов)\n",
           strlen(text));
    printf("  object size: %zu (sizeof массива, включая '\\0')\n",
           object_size);

    printf("  bytes:       ");
    for (size_t i = 0; i < strlen(text); ++i) {
        printf("%02X ", (unsigned char)text[i]);
    }
    puts("");

    printf("  object:      ");
    for (size_t i = 0; i < object_size; ++i) {
        printf("%02X ", (unsigned char)text[i]);
    }
    puts("\n");
}

static void dump_wide(const char *label, const wchar_t *text)
{
    size_t length = wcslen(text);

    printf("%s\n", label);
    printf("  visible:         %ls\n", text);
    printf("  sizeof(wchar_t): %zu байт\n", sizeof(wchar_t));
    printf("  sizeof(array):   %zu байт\n", (length + 1) * sizeof(wchar_t));
    printf("  wcslen():        %zu кодовых единиц (не глифов)\n", length);
    printf("  code units:      ");
    for (size_t i = 0; i < length; ++i) {
        printf("U+%04lX ", (unsigned long)text[i]);
    }
    puts("\n");
}

int main(void)
{
    /*
     * Пустая строка локали заставляет setlocale() выбрать окружение
     * пользователя. Это нужно для корректной печати %ls в UTF-8-терминале.
     */
    if (setlocale(LC_ALL, "") == NULL) {
        fputs("warning: setlocale(LC_ALL, \"\") failed\n", stderr);
    }

    char hello[]   = "Hello";
    char privet[]  = "Привет";
    char yozh[]    = "ёж";
    char daigaku[] = "大学";
    char spaces[]  = "     ";

    puts("=== UTF-8: одна и та же модель, разные длины ===\n");
    dump_bytes("Hello (ASCII)", hello, sizeof hello);
    dump_bytes("Привет (кириллица)", privet, sizeof privet);
    dump_bytes("ёж (2 буквы, 4 байта UTF-8)", yozh, sizeof yozh);
    dump_bytes("大学 (2 иероглифа, 6 байт UTF-8)", daigaku, sizeof daigaku);
    dump_bytes("пять пробелов", spaces, sizeof spaces);

    puts("Вывод: strlen() возвращает число байтов UTF-8, поэтому для\n"
         "«Привет» получается 12, а не 6. sizeof() массива на 1 больше:\n"
         "он включает завершающий нулевой байт.\n");

    puts("=== wchar_t и wide strings ===\n");
    printf("sizeof(wchar_t) = %zu байт на этой платформе\n\n",
           sizeof(wchar_t));

    wchar_t wide_hello[]  = L"Hello";
    wchar_t wide_privet[] = L"Привет";
    wchar_t wide_yozh[]   = L"ёж";
    wchar_t wide_combining[] = L"е\u0301"; /* е + combining acute accent */

    dump_wide("L\"Hello\"", wide_hello);
    dump_wide("L\"Привет\"", wide_privet);
    dump_wide("L\"ёж\"", wide_yozh);
    dump_wide("L\"е\\u0301\" (e + комбинируемый знак)", wide_combining);

    puts("wchar_t на macOS имеет размер 4 байта, на Windows обычно 2.\n"
         "Это свойство реализации, а не гарантия «wchar_t = UTF-32».\n"
         "В последней строке две кодовые единицы (wcslen = 2), но один\n"
         "визуальный графемный кластер.");

    return 0;
}
