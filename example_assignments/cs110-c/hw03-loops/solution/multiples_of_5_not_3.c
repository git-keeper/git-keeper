/* 

Write a program below which prints out all the multiples of 5 less than 1000
that are not also multiples of 3. Use a while loop. The output should start out
like this:

5
10
20
25
35
40
... and so on

*/

#include <stdio.h>

int main() {
  int multiple = 5;

  while(multiple < 1000) {
    if(multiple % 3 != 0)
      printf("%i\n", multiple);

    multiple += 5;
  }

  return 0;
}
    
