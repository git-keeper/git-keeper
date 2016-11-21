/*
 * This module contains functions dealing with triangles.
 */

#include "triangle.h"

int is_triangle(double a, double b, double c) {
    return a + b > c && a + c > b && b + c > a;
}

// Write your implementation of is_isoceles() here.
