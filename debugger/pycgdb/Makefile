all: cpython

cpython: ptrace
	gcc -c -fPIC ptrace.c -o ptrace.o
	gcc -shared -Wl,-soname,libptrace.so -o libptrace.so  ptrace.o
