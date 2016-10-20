#include <stdio.h>

int main() {
  int fahrenheit;

  printf("Enter degrees in fahrenheit: ");

  scanf("%i", &fahrenheit);

  int celsius = (fahrenheit - 32) * 5 / 9;

  printf("%i degrees Fahrenheit is approximately %i degrees Celsius\n",
         fahrenheit, celsius);

  if(celsius > 32) {
    printf("It's hot!\n");
  }
  else if(celsius < 0) {
    printf("It's cold!\n");
  }
}
