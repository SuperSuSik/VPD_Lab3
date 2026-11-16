/*
 * ЛР3, раздел 3.2: генератор большой контрольной строки.
 *
 * Формирует не менее 100 000 случайных десятичных цифр и трижды вставляет
 * персональную контрольную последовательность: в начало, приблизительно в
 * середину и в конец. В stdout не добавляются пробелы и переводы строки.
 *
 * Персональная последовательность строится программно: берутся десятичные
 * коды ASCII-байтов строки "IlyaSuchkov" и записываются подряд.
 *
 * Сборка:
 *   gcc-16 -std=c17 -Wall -Wextra -Wpedantic -O2 generator.c -o generator
 *
 * Запуск:
 *   ./generator > VPD_Lab3.txt
 *   ./generator --print-control       # только контрольная последовательность
 *   ./generator --digits 200000 ...   # больше цифр, если нужно
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IDENTITY "IlyaSuchkov"
#define DEFAULT_RANDOM_DIGITS 100000UL
#define CONTROL_CAPACITY 512

static unsigned long long rng_state = 0x9E3779B97F4A7C15ULL;

static unsigned rng_digit(void)
{
    /*
     * xorshift64* — простой детерминированный PRNG. Фиксированное зерно
     * делает файл и отчёт воспроизводимыми; для криптографии он не годится.
     */
    rng_state ^= rng_state >> 12;
    rng_state ^= rng_state << 25;
    rng_state ^= rng_state >> 27;
    rng_state *= 2685821657736338717ULL;
    return (unsigned)((rng_state >> 32) % 10U);
}

static int build_control(char *out, size_t capacity)
{
    size_t position = 0;

    for (const unsigned char *byte = (const unsigned char *)IDENTITY;
         *byte != '\0'; ++byte) {
        int written = snprintf(out + position, capacity - position, "%u",
                               (unsigned int)*byte);
        if (written < 0 || (size_t)written >= capacity - position) {
            return -1;
        }
        position += (size_t)written;
    }

    return (int)position;
}

static int parse_unsigned_long(const char *text, unsigned long *result)
{
    char *end = NULL;

    errno = 0;
    unsigned long value = strtoul(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return -1;
    }

    *result = value;
    return 0;
}

static int parse_unsigned_long_long(const char *text,
                                    unsigned long long *result)
{
    char *end = NULL;

    errno = 0;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return -1;
    }

    *result = value;
    return 0;
}

static void usage(const char *program)
{
    fprintf(stderr,
            "usage: %s [--digits N] [--seed N] [--print-control]\n"
            "  --digits N        number of random digits (N >= %lu)\n"
            "  --seed N          non-zero PRNG seed (default: %llu)\n"
            "  --print-control   print only the personal control sequence\n",
            program, DEFAULT_RANDOM_DIGITS, 0x9E3779B97F4A7C15ULL);
}

int main(int argc, char **argv)
{
    unsigned long random_digits = DEFAULT_RANDOM_DIGITS;
    int print_control_only = 0;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--print-control") == 0) {
            print_control_only = 1;
        } else if (strcmp(argv[i], "--digits") == 0) {
            if (i + 1 >= argc ||
                parse_unsigned_long(argv[++i], &random_digits) != 0) {
                fputs("error: --digits requires an unsigned integer\n", stderr);
                return 2;
            }
            if (random_digits < DEFAULT_RANDOM_DIGITS) {
                fprintf(stderr,
                        "error: --digits must be at least %lu\n",
                        DEFAULT_RANDOM_DIGITS);
                return 2;
            }
        } else if (strcmp(argv[i], "--seed") == 0) {
            unsigned long long seed = 0;

            if (i + 1 >= argc ||
                parse_unsigned_long_long(argv[++i], &seed) != 0 ||
                seed == 0) {
                fputs("error: --seed requires a non-zero unsigned integer\n",
                      stderr);
                return 2;
            }
            rng_state = seed;
        } else if (strcmp(argv[i], "--help") == 0) {
            usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "error: unknown argument: %s\n", argv[i]);
            usage(argv[0]);
            return 2;
        }
    }

    char control[CONTROL_CAPACITY];
    int control_length = build_control(control, sizeof control);

    if (control_length < 0) {
        fputs("error: control sequence does not fit into buffer\n", stderr);
        return 1;
    }

    if (print_control_only) {
        puts(control);
        return 0;
    }

    const unsigned long first_part = random_digits / 2;
    const unsigned long second_part = random_digits - first_part;

    fputs(control, stdout);

    for (unsigned long i = 0; i < first_part; ++i) {
        fputc('0' + (int)rng_digit(), stdout);
    }

    fputs(control, stdout);

    for (unsigned long i = 0; i < second_part; ++i) {
        fputc('0' + (int)rng_digit(), stdout);
    }

    fputs(control, stdout);

    if (ferror(stdout)) {
        fputs("error: failed to write stdout\n", stderr);
        return 1;
    }

    return 0;
}
