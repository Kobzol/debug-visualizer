#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <dlfcn.h>

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

typedef void* (*malloc_orig_t)(size_t size);
static malloc_orig_t malloc_orig = NULL;

typedef void (*free_orig_t)(void* addr);
static free_orig_t free_orig = NULL;

typedef void* (*realloc_orig_t)(void* addr, size_t size);
static realloc_orig_t realloc_orig = NULL;

static FILE* alloc_file = NULL;

#define ALLOC_FILE_TMP_VALUE ((FILE*) 1)

void close_file(void)
{
    if (alloc_file)
    {
        fclose(alloc_file);
    }
}

void* malloc(size_t size)
{
    if (!malloc_orig)
    {
        malloc_orig = (malloc_orig_t) dlsym(RTLD_NEXT, "malloc");
    }

    if (!alloc_file)
    {
        alloc_file = ALLOC_FILE_TMP_VALUE; // to prevent stack overflow for malloc in fopen

        char* path = getenv("DEVI_ALLOC_FILE_PATH");
        assert(path);

        alloc_file = fopen(path, "w");

        assert(alloc_file);
        atexit(close_file);
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        void* addr = malloc_orig(size);
        fprintf(alloc_file, "malloc %p %d\n", addr, size);

        return addr;
    }
    else return malloc_orig(size);
}

void free(void* addr)
{
    if (!free_orig)
    {
        free_orig = (free_orig_t) dlsym(RTLD_NEXT, "free");
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        fprintf(alloc_file, "free %p\n", addr);
    }

    free_orig(addr);
}

void* realloc(void* addr, size_t size)
{
    if (!realloc_orig)
    {
        realloc_orig = (realloc_orig_t) dlsym(RTLD_NEXT, "realloc");
    }

    if (alloc_file && alloc_file != ALLOC_FILE_TMP_VALUE)
    {
        void* addr_new = realloc_orig(addr, size);
        fprintf(alloc_file, "realloc %p %p %d\n", addr, addr_new, size);

        return addr_new;
    }
    else return realloc_orig(addr, size);
}
