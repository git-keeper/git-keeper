/*
 * This module contains functions dealing with triangles.
 */


/// CORRECT SOL:
//#include "triangle.h"
//
//int is_triangle(double side_a, double side_b, double side_c) {
//    return side_a + side_b > side_c &&
//           side_a + side_c > side_b &&
//           side_b + side_c > side_a;
//}
//
//int is_isoceles(double side_a, double side_b, double side_c) {
//    if(!is_triangle(side_a, side_b, side_c))
//        return 0;
//
//    return side_a == side_b || side_a == side_c || side_b == side_c;
//}


/// SOL MADE UP FOR TESTING: