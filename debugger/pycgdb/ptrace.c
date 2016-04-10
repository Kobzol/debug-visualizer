/*
    Copyright (C) 2015-2016 Jakub Beranek

    This file is part of Devi.

    Devi is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License, or
    (at your option) any later version.

    Devi is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
*/

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