/*
 * ЛР3, раздел 2.1: базовый эксперимент с ASCII.
 *
 * Показывает разницу между размером массива (sizeof), длиной C-строки
 * (strlen) и числовыми кодами отдельных байтов.
 */
#include <stdio.h>
#include <string.h>

int main(void)
{
    char text[] = "Hello";

    printf("=== ASCII: sizeof() и strlen() ===\n");
    printf("text:            %s\n", text);
    printf("sizeof(text):    %zu\n", sizeof(text));
    printf("strlen(text):    %zu\n", strlen(text));
    printf("sizeof - strlen: %zu (место под завершающий '\\0')\n",
           sizeof(text) - strlen(text));

    puts("\nсимвол | десятичный код | шестнадцатеричный код | байт");
    puts("-------+----------------+-----------------------+-----");

    for (size_t i = 0; i < strlen(text); ++i) {
        unsigned char byte = (unsigned char)text[i];
        printf("  %c    |      %3u       |        0x%02X           | %zu\n",
               text[i], byte, byte, i);
    }

    printf("\ntext[%zu] = %d — завершающий нулевой символ '\\0'\n",
           strlen(text), text[strlen(text)]);
    printf("Каждый символ 'Hello' занимает 1 байт в ASCII/UTF-8; "
           "strlen() не считает '\\0'.\n");

    return 0;
}
