/*
 * Contains tests for testing the functions in triangle.h
 */

#include <stdio.h>

#include "triangle.h"

void test_is_triangle(double side_a, double side_b, double side_c,
                      int expected);

void test_is_isoceles(double side_a, double side_b, double side_c,
                      int expected);

int main() {
    // Tests for is_triangle

    // a + b == c
    test_is_triangle(3, 7, 10, 0);
    // a + b < c
    test_is_triangle(3.9, 6, 10, 0);
    // a + c == b
    test_is_triangle(3, 6, 3, 0);
    // a + c < b
    test_is_triangle(3, 6, 2.9, 0);
    // b + c == a
    test_is_triangle(40, 20, 20, 0);
    // b + c < a
    test_is_triangle(40, 19.9, 20, 0);

    // All sides equal
    test_is_triangle(1, 1, 1, 1);
    // a + b is slightly larger than c
    test_is_triangle(1.001, 2, 3, 1);
    // a + c is slightly larger than b
    test_is_triangle(2, 3, 1.001, 1);
    // b + c is slightly larger than a
    test_is_triangle(3, 1.001, 2, 1);

    // Tests for is_isoceles

    // not a triangle
    test_is_isoceles(1, 2, 3, 0);
    // triangle, but not isoceles
    test_is_isoceles(3, 4, 5, 0);

    // a == b
    test_is_isoceles(2, 2, 3, 1);
    // a == c
    test_is_isoceles(2, 3, 2, 1);
    // b == c
    test_is_isoceles(3, 2, 2, 1);
}

void test_is_triangle(double side_a, double side_b, double side_c,
                      int expected) {
    int result = is_triangle(side_a, side_b, side_c);

    if(result != expected) {
        printf("Expected %d when calling is_triangle(%lf, %lf, %lf), got %d\n",
               expected, side_a, side_b, side_c, result);
    }
}

void test_is_isoceles(double side_a, double side_b, double side_c,
                      int expected) {
    int result = is_isoceles(side_a, side_b, side_c);

    if(result != expected) {
        printf("Expected %d when calling is_isoceles(%lf, %lf, %lf), got %d\n",
               expected, side_a, side_b, side_c, result);
    }
}
