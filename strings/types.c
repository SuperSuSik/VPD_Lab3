/*
 * ЛР3, разделы 2.3 и 2.5:
 *   - одинаковые ASCII-коды в массивах char/short/int/unsigned long long;
 *   - <stdint.h>, CHAR_BIT, exact-width, least и fast типы.
 */
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

#define PRINT_AS_CHARS(label, array)                                      \
    do {                                                                  \
        printf("%-22s: ", (label));                                       \
        for (size_t i = 0; i < sizeof(array) / sizeof((array)[0]); ++i) { \
            unsigned char ch = (unsigned char)(array)[i];                 \
            putchar(ch);                                                  \
        }                                                                 \
        putchar('\n');                                                    \
    } while (0)

int main(void)
{
    /*
     * Пять элементов без завершающего '\0': это массивы символов,
     * а не C-строки. %s с ними использовать нельзя.
     */
    char a[] = {'H', 'e', 'l', 'l', 'o'};
    short b[] = {'H', 'e', 'l', 'l', 'o'};
    int c[] = {'H', 'e', 'l', 'l', 'o'};
    unsigned long long d[] = {'H', 'e', 'l', 'l', 'o'};

    puts("=== Одинаковые ASCII-коды в разных типах элементов ===\n");
    PRINT_AS_CHARS("char[]", a);
    PRINT_AS_CHARS("short[]", b);
    PRINT_AS_CHARS("int[]", c);
    PRINT_AS_CHARS("unsigned long long[]", d);

    printf("\nsizeof(char[5])               = %2zu байт\n", sizeof a);
    printf("sizeof(short[5])              = %2zu байт\n", sizeof b);
    printf("sizeof(int[5])                = %2zu байт\n", sizeof c);
    printf("sizeof(unsigned long long[5]) = %2zu байт\n", sizeof d);

    char hello_string[] = "Hello";
    printf("\nchar hello_string[] = \"Hello\"; sizeof = %zu (5 букв + '\\0')\n",
           sizeof hello_string);
    puts("Только char-массив с '\\0' является C-строкой. Массивы short/int/\n"
         "unsigned long long содержат те же числа, но не являются строкой:\n"
         "printf(\"%s\", ...) ожидает char*, а не short* или int*.\n");

    puts("=== <stdint.h>: ширина типов ===\n");
    printf("CHAR_BIT           = %d бит в одном байте\n", CHAR_BIT);
    printf("sizeof(char)       = %zu байт\n", sizeof(char));
    printf("sizeof(short)      = %zu байт\n", sizeof(short));
    printf("sizeof(int)        = %zu байт\n", sizeof(int));
    printf("sizeof(long)       = %zu байт\n", sizeof(long));
    printf("sizeof(long long)  = %zu байт\n", sizeof(long long));
    printf("sizeof(unsigned int) = %zu байт\n", sizeof(unsigned int));
    puts("");

#ifdef UINT8_MAX
    printf("uint8_t            = %zu байт, %zu бит (exact-width)\n",
           sizeof(uint8_t), sizeof(uint8_t) * CHAR_BIT);
#endif
#ifdef UINT16_MAX
    printf("uint16_t           = %zu байт, %zu бит (exact-width)\n",
           sizeof(uint16_t), sizeof(uint16_t) * CHAR_BIT);
#endif
#ifdef UINT32_MAX
    printf("uint32_t           = %zu байт, %zu бит (exact-width)\n",
           sizeof(uint32_t), sizeof(uint32_t) * CHAR_BIT);
#endif
#ifdef UINT64_MAX
    printf("uint64_t           = %zu байт, %zu бит (exact-width)\n",
           sizeof(uint64_t), sizeof(uint64_t) * CHAR_BIT);
#endif

    printf("\nuint_least32_t     = %zu байт, минимум 32 бита\n",
           sizeof(uint_least32_t));
    printf("uint_fast32_t      = %zu байт, минимум 32 бита, выбран для скорости\n",
           sizeof(uint_fast32_t));
    printf("uint_least16_t     = %zu байт\n", sizeof(uint_least16_t));
    printf("uint_fast16_t      = %zu байт\n", sizeof(uint_fast16_t));
    printf("uintmax_t          = %zu байт\n", sizeof(uintmax_t));

    puts("\nuint32_t существует только там, где есть ровно 32-битный\n"
         "беззнаковый тип без padding-битов. unsigned int обычно тоже\n"
         "4 байта, но стандарт не гарантирует ровно 32 бита. Для\n"
         "аппаратного регистра или поля протокола uint32_t информативнее:\n"
         "он фиксирует и ширину, и отсутствие знака.");

    return 0;
}
