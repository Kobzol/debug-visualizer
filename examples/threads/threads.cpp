#include <iostream>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>

struct SyncData
{
public:
    SyncData() : buffer('\0'), bufferSize(0)
    {
        pthread_cond_init(&this->read_cond_var, NULL);
        pthread_cond_init(&this->write_cond_var, NULL);
    }
    ~SyncData()
    {
        pthread_cond_destroy(&this->read_cond_var);
        pthread_cond_destroy(&this->write_cond_var);
    }

    pthread_mutex_t mutex;
    pthread_cond_t read_cond_var;
    pthread_cond_t write_cond_var;
    char buffer;
    int bufferSize;
};

void* thread_fn(void* arg)
{
    SyncData* syncData = (SyncData*) arg;
    while (true)
    {
        pthread_mutex_lock(&syncData->mutex);

        while (syncData->bufferSize < 1)
        {
            pthread_cond_wait(&syncData->read_cond_var, &syncData->mutex);
        }

        if (!syncData->buffer)
        {
            pthread_mutex_unlock(&syncData->mutex);
            break;
        }

        std::cout << "Hello from the other side: " << syncData->buffer << std::endl;
        syncData->bufferSize = 0;

        pthread_cond_signal(&syncData->write_cond_var);
        pthread_mutex_unlock(&syncData->mutex);
    }
}

int main()
{
    SyncData syncData;

    pthread_t thread;
    int res = pthread_create(&thread, NULL, thread_fn, &syncData);

    if (res) exit(1);

    const char* msg = "hello";
    size_t len = strlen(msg) + 1;

    for (int i = 0; i < len; i++)
    {
        pthread_mutex_lock(&syncData.mutex);

        while (syncData.bufferSize > 0)
        {
            pthread_cond_wait(&syncData.write_cond_var, &syncData.mutex);
        }

        if (msg[i])
        {
            std::cout << "Main thread sends " << msg[i] << std::endl;
        }

        syncData.buffer = msg[i];
        syncData.bufferSize = 1;

        pthread_cond_signal(&syncData.read_cond_var);
        pthread_mutex_unlock(&syncData.mutex);
    }

    pthread_join(thread, NULL);

    return 0;
}