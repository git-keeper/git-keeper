/*

Write a program which prints out a checkerboard of asterisks (*'s) with a size
specified by the user. This program will be much like the square program that
you wrote for the previous homework except that every other entry in each row
will be a space instead of an asterisk. The first row must start with an
asterisk, the second with a space, the third with an asterisk, etc. Each row
must have the same number of characters, so if the row ends with an empty space
you must print a space there even though it will not have a visible effect.

For this program, your prompt must have the exact same text as my prompt in the
example output.

Example output:

Enter the size of the checkerboard: 6
* * *
 * * *
* * *
 * * *
* * *
 * * *

 */

#include <stdio.h>

int main() {
  printf("Enter the size of the checkerboard: ");

  int size;

  scanf("%i", &size);

  for(int i = 0; i < size; i++) {
    for(int j = 0; j < size; j++) {
      if(i % 2 == j % 2)
        printf("*");
      else
        printf(" ");
    }
    printf("\n");
  }

  return 0;
}
