/*

Write a program which prints out a triangle of asterisks (*'s) with a size
specified by the user. If the size specified by the user is n, then there must
be n rows of asterisk where the first row has 1 asterisk, the second has 2, and
so on. Here is an example run:


Enter the size of the triangle: 6
*
**
***
****
*****
******

 */

#include <stdio.h>

int main() {
  printf("Enter the size of the triangle: ");

  int size;

  scanf("%i", &size);

  int row_length = 1;

  for(int i = 0; i < size; i++) {
    for(int j = 0; j < row_length; j++) {
      printf("*");
    }
    printf("\n");
    row_length++;
  }

  return 0;
}
