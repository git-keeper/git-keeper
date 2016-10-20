/*
 * File: paycheck.h
 *
 * Defines functions used to calculate employee pay.
 */

// If an employee works more than this number of hours, they will get overtime
// pay.
#define OVERTIME_THRESHOLD 40

// An employee's normal pay rate will be multiplied by this when calculating
// overtime.
#define OVERTIME_MULTIPLIER 1.5

/*
 * Given a number of hours worked and a rate of pay, calculate the amount that
 * an employee should be paid for one week of work. If the employee works more
 * than 40 hours, the employee will be paid an overtime rate of 1.5 times the
 * normal rate for the hours worked above 40.
 *
 * Paramters:
 *   double hours - the number of hours worked
 *   double rate  - the hourly rate of pay
 *
 * Return value:
 *   A double representing the amount the employee is to be paid
 */
double calculate_pay(double hours, double rate);

/*
 * Given the number of hours worked for two separate weeks and a rate of pay,
 * calculate the amount that an employee should be paid for two weeks of
 * work. For each week, if the employee works more than 40 hours, the employee
 * will be paid an overtime rate of 1.5 times the normal rate for the hours
 * worked above 40.
 *
 * Paramters:
 *   double week1_hours - the number of hours worked in the first week
 *   double week2_hours - the number of hours worked in the second week
 *   double rate  - the hourly rate of pay
 *
 * Return value:
 *   A double representing the amount the employee is to be paid
 */
double calculate_biweekly_pay(double week1_hours, double week2_hours,
                              double rate);
