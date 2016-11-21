/*
 * This module contains functions dealing with triangles.
 */

// Given the lengths of 3 sides of a triange, return 1 if those lengths could
// form a triangle, 0 otherwise.
int is_triangle(double side_a, double side_b, double side_c);

// Given the lengths of 3 sides of a triangle, return 1 if the lengths form an
// isoceles triangle, 0 otherwise.
int is_isoceles(double side_a, double side_b, double side_c);
