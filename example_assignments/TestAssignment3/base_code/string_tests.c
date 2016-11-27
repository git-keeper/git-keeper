/*
 * Contains tests for testing the functions in string_student.h
 */

#include <stdio.h>

#include "string_student.h"

void test_num(char* p);
void test_len(char* p);


int main()
{
    char source[] = "This is an example."; //size 20
    test_num(source)
    test_len(source)
}

void test_len(char* p, int expected);
{
    int result = myStringLen(char* myString) ;
    if (result != expected)
    {
    printf("Expected %d and got %d\n", expected,  result);
    }
}

void test_num(char* p, int expected)
{
    int result = stringToInt(char* myString);
    if (result != expected)
    {
    printf("Expected %d and got %d\n", expected,  result);
    }
}



void test_is_triangle(double side_a, double side_b, double side_c,
                      int expected) {
    int result = is_triangle(side_a, side_b, side_c);

    if(result != expected) {
        printf("Expected %d when calling is_triangle(%lf, %lf, %lf), got %d\n",
               expected, side_a, side_b, side_c, result);
    }
}

