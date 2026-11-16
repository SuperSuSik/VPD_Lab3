/*
 * ЛР3, раздел 2.10: Unicode-идентификаторы в C.
 *
 * GCC и Clang в UTF-8-локали принимают extended identifiers. Это
 * эксперимент, а не рекомендация называть так переменные в командном
 * проекте.
 */
#include <stdio.h>

int main(void)
{
    int студент = 304;
    int 学生 = 7;

    printf("C (%s): студент=%d, 学生=%d, __STDC_VERSION__=%ld\n",
#if defined(__clang__)
           "Clang",
#elif defined(__GNUC__)
           "GCC",
#else
           "unknown compiler",
#endif
           студент, 学生, (long)__STDC_VERSION__);

    return 0;
}
