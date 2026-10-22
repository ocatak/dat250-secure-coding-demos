/* DAT250 memory-safety demo: a classic stack buffer overflow. */
#include <stdio.h>
#include <stddef.h>

struct session {
    char username[8];
    int  is_admin;           /* immediately after username */
};

/*
 * Deliberately unsafe strcpy-like function.
 *
 * We implement the copy ourselves because modern macOS/Apple Clang
 * may trap an overflowing strcpy() before we can demonstrate the
 * adjacent-variable corruption.
 */
__attribute__((noinline))
static void unsafe_copy(char *dst, const char *src)
{
    while (1) {
        char c = *src++;
        *dst++ = c;          /* NO bounds check */
        if (c == '\0')
            break;
    }
}

int main(int argc, char **argv)
{
    struct session s = {
        .username = {0},
        .is_admin = 0
    };

    const char *input = argc > 1 ? argv[1] : "guest";

    unsafe_copy(s.username, input);

    /*
     * Print input rather than s.username because after overflowing
     * username, treating it as a valid C string would itself be
     * another out-of-bounds read.
     */
    printf("user=%s  is_admin=%d\n", input, s.is_admin);

    if (s.is_admin)
        puts(">>> ADMIN ACCESS GRANTED");

    return 0;
}