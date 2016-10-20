#include <stdio.h>


double calculate_pay(double hours, double rate);


int main() {
  double hours, pay;

  printf("Enter hours worked: ");
  scanf("%lf", &hours);

  printf("Enter the rate of pay: ");
  scanf("%lf", &pay);

  printf("You earned $%.2lf\n", calculate_pay(hours, pay));

  return 0;
}


double calculate_pay(double hours, double rate) {
  double pay;

  if(hours > 40.0) {
    double extra = hours - 41;
    pay = 40 * rate + extra * (1.5 * rate);
  }
  else
    pay = hours * rate;

  return pay;
}


