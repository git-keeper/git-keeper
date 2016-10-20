/*

Write a program which prints out a "square" of asterisks (*'s) with a size
specified by the user. If the size specified by the user is n, then there must
be n rows of n asterisks each. Here is an example run:

Enter the size of the square: 5
*****
*****
*****
*****
*****

 */

#include <stdio.h>

int main() {
  printf("Enter the size of the square: ");

  int size;

  scanf("%i", &size);

  for(int i = 0; i < size; i++) {
    for(int j = 0; j < size; j++) {
      printf("*");
    }
    printf("\n");
  }

  return 0;
}
