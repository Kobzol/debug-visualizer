#include <sys/ptrace.h>
#include <errno.h>

long py_ptrace(int request, int pid, void* addr, void* data)
{
    return ptrace(request, pid, addr, data);
}

int py_errno()
{
    return errno;
}

int main(int argc, char** argv)
{
    return 0;
}