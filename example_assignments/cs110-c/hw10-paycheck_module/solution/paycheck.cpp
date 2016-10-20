#include "paycheck.h"

double calculate_pay(double hours, double rate) {
  double pay;

  if(hours > OVERTIME_THRESHOLD) {
    double overtime_hours = hours - OVERTIME_THRESHOLD;
    double overtime_rate = OVERTIME_MULTIPLIER * rate;
    pay = OVERTIME_THRESHOLD * rate + overtime_hours * overtime_rate;
  }
  else
    pay = hours * rate;

  return pay;
}

double calculate_biweekly_pay(double week1_hours, double week2_hours,
                              double rate) {
  return calculate_pay(week1_hours, rate) + calculate_pay(week2_hours, rate);
}
