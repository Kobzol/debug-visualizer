#include <iostream>

int main()
{
    int a = 5;
    int b = 6;
    int* p = &a;
    int& r = b;

    while (true)
    {
        // place break here, change the value of the pointer or the reference
        // and observe the output
        std::cout << *p << " " << r << std::endl;
    }

    return 0;
}