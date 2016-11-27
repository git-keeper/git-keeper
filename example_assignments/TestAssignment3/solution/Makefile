CFLAGS=-std=c99 -Wall
CC=gcc

string_tests: string_student.o string_tests.o
	$(CC) $(CFLAGS) string_tests.o string_student.o -o string_tests

string_tests.o: string_tests.c string_student.h
	$(CC) $(CFLAGS) -c string_tests.c

string_student.o: string_student.h string_student.c
	$(CC) $(CFLAGS) -c string_student.c

clean:
	rm -f string_tests *.o
