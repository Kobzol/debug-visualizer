#include <cstdlib>

int main(int argc, char** argv)
{
    int* data = (int*) malloc(1024);

    if (data[0])    // without this the allocation is optimized away
    {
        data[5] = 8;
    }

    free(data);

    return 0;
}