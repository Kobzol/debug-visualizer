all: cpython cpp_test clean

cpp_test:
	gcc -g -S -c test.c
	gcc test.s -o test

cpython:
	gcc -c -fPIC ptrace.c -o ptrace.o
	gcc -shared -Wl,-soname,libptrace.so -o libptrace.so ptrace.o

clean:
	rm *.o
	rm *.s
