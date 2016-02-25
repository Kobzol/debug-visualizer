#include <iostream>
#include <unistd.h>

int main(int argc, char** argv)
{
    std::cout << argc << std::endl;

    for (int i = 0; i < argc; i++)
    {
        std::cout << argv[i] << std::endl;
    }

    std::cout << getenv("DEVI_ENV_TEST") << std::endl;

    return 0;
}