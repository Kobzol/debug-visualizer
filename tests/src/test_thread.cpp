#include <pthread.h>
#include <iostream>
#include <unistd.h>

volatile int a = 0;

void* test(void* param)
{
    while (true)
    {
        a++;

        if (a == 5)
        {
            a--;
        }
    }
}

int main()
{
    pthread_t thread;
    int result = pthread_create(&thread, NULL, test, NULL);

    sleep(1);

    while (true)
    {
        a++;

        if (a == 5)
        {
            a--;
        }
    }

    pthread_join(thread, NULL);

    return 0;
}