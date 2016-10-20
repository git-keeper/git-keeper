/*

Write a program which prints out a pyramid of asterisks (*'s) with a size
specified by the user. If the size specified by the user is n, then there must
be n rows of asterisk where the first row has 1 asterisk, the second has 3, and
so on. Each row must be centered. Here is an example run:


Enter the size of the pyramid: 4
   *
  ***
 *****
*******

For this one, think about how many spaces and how many spaces and how many
asterisks you need in each row. You will need two separate loops nested inside
the main loop.

 */

#include <stdio.h>

int main() {
  printf("Enter the size of the pyramid: ");

  int size;

  scanf("%i", &size);

  for(int i = 0; i < size; i++) {
    int space_count = size - (i + 1);
    int star_count = 2 * (i + 1) - 1;

    for(int j = 0; j < space_count; j++) {
      printf(" ");
    }

    for(int j = 0; j < star_count; j++) {
      printf("*");
    }
    
    printf("\n");
  }

  return 0;
}
