all: cpython cpp_test

cpp_test: test
	gcc -g -S -c test.c
	gcc test.s -o test

cpython: ptrace
	gcc -c -fPIC ptrace.c -o ptrace.o
	gcc -shared -Wl,-soname,libptrace.so -o libptrace.so  ptrace.o
