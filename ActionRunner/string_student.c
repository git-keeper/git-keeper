/*
 * This module contains functions dealing with triangles.
 */

#include "string_student.h"

int myStringLen(char* myString) {
    size_t n = sizeof(myString) / sizeof(myString[0])
    return n;
}




void printMyString(char* myString){
    printf("p: %s",p);
}



int stringToInt(char* myString)
{
    int val = 0;
    int length = (int)strlen(myString);
    for (int i = 0; i < length; i++)
    {
        val = val + (int)myString[i];
    }

    return val;
}