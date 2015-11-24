#include <cstdlib>

int test(int b)
{
    int a = rand() * b;
    return a + b;
}

int main()
{
    test(5);
    int b = 6;
    int c = 7;

    while (true);

    return 0;
}