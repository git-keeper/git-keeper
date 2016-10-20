/* 

Write a program below which prints consecutive non-negative integers, starting
with 0. Ask the user for the number of integers to print, and then print that
many. Use a for loop. Here is what an example run should look like:

How many non-negative integers? 6
0
1
2
3
4
5

*/

#include <stdio.h>

int main() {
  int n;

  printf("How many non-negative integers? ");

  scanf("%i", &n);

  for(int i = 0; i < n; i++) {
    printf("%i\n", i);
  }

  return 0;
}
