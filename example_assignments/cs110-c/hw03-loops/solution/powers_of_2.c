/* 

Write a program below which prints consecutive powers of 2, starting with 2^0,
which is 1. Ask the user for the number of powers of 2 to print, and then print
that many. Use a for loop. Here is what an example run should look like:

How many powers of 2? 5
1
2
4
8
16

*/

#include <stdio.h>

int main() {
  int n;

  printf("How many powers of 2? ");

  scanf("%i", &n);

  int power = 1;

  for(int i = 0; i < n; i++) {
    printf("%i\n", power);
    power *= 2;
  }

  return 0;
}
