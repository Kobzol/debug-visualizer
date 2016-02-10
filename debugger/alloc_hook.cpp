#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <dlfcn.h>
#include <unistd.h>

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
static bool load_in_progress = false;

static std::mutex alloc_mutex;
typedef std::mutex devi_mutex;

#define STATIC_BUFFER_SIZE (1024)
static char static_buffer[STATIC_BUFFER_SIZE] = { 0 };
static size_t static_buffer_index = 0;

template <typename T>
void load_symbol(T& target, const char* name)
{
    if (!target)
    {
        target = (T) dlsym(RTLD_NEXT, name);
        assert(target);
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

void load_symbols()
{
    std::lock_guard<devi_mutex> lock(alloc_mutex);

    if (load_in_progress)
    {
        return;
    }

    load_in_progress = true;

    if (!malloc_orig) load_symbol(malloc_orig, "malloc");
    if (!calloc_orig) load_symbol(calloc_orig, "calloc");
    if (!realloc_orig) load_symbol(realloc_orig, "realloc");
    if (!free_orig) load_symbol(free_orig, "free");
    if (!alloc_file) open_alloc_file();

    load_in_progress = false;
}

void* static_alloc(size_t size)
{
    assert(static_buffer_index + size <= STATIC_BUFFER_SIZE);
    size_t index = static_buffer_index;
    static_buffer_index += size;
    return static_buffer + index;
}

void* malloc(size_t size)
{
    if (load_in_progress)
    {
        return static_alloc(size);
    }
    else load_symbols();

    void* addr = malloc_orig(size);
    fprintf(alloc_file, "malloc %p %zu\n", addr, size);
    fflush(alloc_file);

    return addr;
}

void* calloc(size_t num, size_t size)
{
    if (load_in_progress)
    {
        return static_alloc(size);
    }
    else load_symbols();

    void* addr = calloc_orig(num, size);
    fprintf(alloc_file, "calloc %p %zu\n", addr, num * size);
    fflush(alloc_file);

    return addr;
}

void* realloc(void* addr, size_t size)
{
    if (load_in_progress)
    {
        return static_alloc(size);
    }
    else load_symbols();

    void* addr_new = realloc_orig(addr, size);
    fprintf(alloc_file, "realloc %p %p %zu\n", addr, addr_new, size);
    fflush(alloc_file);

    return addr_new;
}

void free(void* addr)
{
    if (addr >= static_buffer && addr <= static_buffer + STATIC_BUFFER_SIZE)
    {
        return;
    }

    if (!load_in_progress)
    {
        load_symbols();
    }

    if (addr == NULL)
    {
        fprintf(alloc_file, "free NULL\n");
    }
    else fprintf(alloc_file, "free %p\n", addr);
    fflush(alloc_file);

    free_orig(addr);
}