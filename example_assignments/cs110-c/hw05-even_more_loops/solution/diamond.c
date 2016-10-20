/*

Write a program which prints out an empty diamond of asterisks (*'s) with a
size specified by the user. On each line there must not be any spaces between
the last asterisk and the newline.

The size specifies the number of rows from the first row to the widest row.

For this program, your prompt must have the exact same text as my prompt in the
example output.

Example output:

Enter the size of the diamond: 4
   *
  * *
 *   *
*     *
 *   *
  * *
   *

*/

#include <stdio.h>

int main() {
  printf("Enter the size of the diamond: ");

  int size;

  scanf("%i", &size);

  int first_star_pos = size - 1;
  int second_star_pos = size - 1;

  int first_star_direction = -1;
  int second_star_direction = 1;

  for(int i = 0; i < 2 * size - 1; i++) {
    for(int j = 0; j <= second_star_pos; j++) {
      if(j == first_star_pos || j == second_star_pos)
        printf("*");
      else
        printf(" ");
    }

    if(first_star_pos == 0) {
      first_star_direction = 1;
      second_star_direction = -1;
    }

    first_star_pos += first_star_direction;
    second_star_pos += second_star_direction;

    printf("\n");
  }

  return 0;
}
