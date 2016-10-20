#!/usr/bin/env python3

import os
import sys

from gkeepcore.shell_command import run_command


def calculate_pay(hours, rate):
    pay = 0

    if hours <= 40:
        pay += hours * rate
    else:
        pay += 40 * rate
        pay += (hours - 40) * (rate * 1.5)

    return pay


def main(submission_dir):
    os.chdir(submission_dir)

    if not os.path.isfile('paycheck.c'):
        print('paycheck.c does not exist.')
        return

    try:
        run_command(['gcc', '-std=gnu99', 'paycheck.c'])
    except Exception:
        print('paycheck.c did not compile.')
        return

    rate_hours_pairs = [
        (10, 10),
        (10.5, 10),
        (10, 40),
        (10, 50),
        (10, 40.1),
        (10.44, 30),
        (10.44, 41),
        (10.44, 50.5)
    ]

    for rate, hours in rate_hours_pairs:
        command = './a.out <<< "{0} {1}"'.format(hours, rate)

        try:
            output = run_command(command)
        except Exception as e:
            output = str(e)

        expected_output = '${0:.2f}'.format(calculate_pay(hours, rate))

        if expected_output not in output:
            print('Expected to see {0} when entering {1} for hours and {2} for rate'.format(expected_output, hours, rate))
            return

    print('All tests passed!\n\nThe organization of your code will be graded separately.')
        
if __name__ == '__main__':
    main(sys.argv[1])
