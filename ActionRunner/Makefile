CFLAGS=-std=c99 -Wall
CC=gcc

triangle_tests: triangle.o triangle_tests.o
	$(CC) $(CFLAGS) triangle_tests.o triangle.o -o triangle_tests

triangle_tests.o: triangle_tests.c triangle.h
	$(CC) $(CFLAGS) -c triangle_tests.c

triangle.o: triangle.h triangle.c
	$(CC) $(CFLAGS) -c triangle.c

clean:
	rm -f triangle_tests *.o
