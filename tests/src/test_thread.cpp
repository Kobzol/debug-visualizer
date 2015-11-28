#include <pthread.h>
#include <iostream>
#include <unistd.h>

void* test(void* param)
{
    while (true)
    {
        int a = 5;
    }
}

int main()
{
    pthread_t thread;
    int result = pthread_create(&thread, NULL, test, NULL);

    sleep(1);

    while (true)
    {
        int b = 5;
    }

    pthread_join(thread, NULL);

    return 0;
}