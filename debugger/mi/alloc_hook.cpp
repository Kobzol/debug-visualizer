#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <dlfcn.h>

#include <cassert>
#include <cstdlib>
#include <cstdio>

#include <mutex>

#define ALLOC_FILE_TMP_VALUE ((FILE*) 1)

typedef void* (*malloc_orig_t)(size_t size);
static malloc_orig_t malloc_orig = NULL;

typedef void* (*calloc_orig_t)(size_t num, size_t size);
static calloc_orig_t calloc_orig = NULL;

typedef void* (*realloc_orig_t)(void* addr, size_t size);
static realloc_orig_t realloc_orig = NULL;

typedef void (*free_orig_t)(void* addr);
static free_orig_t free_orig = NULL;

static FILE* alloc_file = NULL;

static std::mutex alloc_mutex;

template <typename T>
void load_symbol(T& target, const char* name)
{
    std::lock_guard<std::mutex> guard(alloc_mutex);

    if (!target)
    {
        target = (T) dlsym(RTLD_NEXT, name);
    }
}

void close_file(void)
{
    if (alloc_file)
    {
        fclose(alloc_file);
    }
}

void open_alloc_file()
{
    std::lock_guard<std::mutex> guard(alloc_mutex);

    if (!alloc_file)
    {
        alloc_file = ALLOC_FILE_TMP_VALUE; // to prevent stack overflow for malloc in fopen

        char* path = getenv("DEVI_ALLOC_FILE_PATH");
        assert(path);

        alloc_file = fopen(path, "w");

        assert(alloc_file);
        atexit(close_file);
    }
}

void* malloc(size_t size)
{
    if (!malloc_orig)
    {
        load_symbol(malloc_orig, "malloc");
    }

    if (!alloc_file)
    {
        open_alloc_file();
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        void* addr = malloc_orig(size);
        fprintf(alloc_file, "malloc %p %d\n", addr, size);
        fflush(alloc_file);

        return addr;
    }
    else return malloc_orig(size);
}

void* calloc(size_t num, size_t size)
{
    if (!calloc_orig)
    {
        load_symbol(calloc_orig, "calloc");
    }

    if (!alloc_file)
    {
        open_alloc_file();
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        void* addr = calloc_orig(num, size);
        fprintf(alloc_file, "calloc %p %d\n", addr, num * size);
        fflush(alloc_file);

        return addr;
    }
    else return calloc_orig(num, size);
}

void* realloc(void* addr, size_t size)
{
    if (!realloc_orig)
    {
        load_symbol(realloc_orig, "realloc");
    }

    if (!alloc_file)
    {
        open_alloc_file();
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        void* addr_new = realloc_orig(addr, size);
        fprintf(alloc_file, "realloc %p %p %d\n", addr, addr_new, size);
        fflush(alloc_file);

        return addr_new;
    }
    else return realloc_orig(addr, size);
}

void free(void* addr)
{
    if (!free_orig)
    {
        load_symbol(free_orig, "free");
    }

    if (!alloc_file)
    {
        open_alloc_file();
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        if (addr == NULL)
        {
            fprintf(alloc_file, "free NULL\n");
        }
        else fprintf(alloc_file, "free %p\n", addr);
        fflush(alloc_file);
    }

    free_orig(addr);
}