#!/usr/bin/env python3

import os
import sys

from gkeepcore.shell_command import run_command


def checkerboard():
    def generate_desired_output(size):
        desired_output = ''

        for i in range(size):
            for j in range(size):
                if i % 2 == j % 2:
                    desired_output += '*'
                else:
                    desired_output += ' '
            desired_output += '\n'

        return desired_output

    for x in range(5, 10):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for checkerboard.c')
            print()
            return False

    print('Tests passed for checkerboard.c')
    print()

    return True


def diamond():
    def generate_desired_output(size):
        desired_output = ''

        first_star_pos = size - 1
        second_star_pos = size - 1

        first_star_direction = -1
        second_star_direction = 1

        for i in range(2 * size - 1):
            for j in range(second_star_pos + 1):
                if j == first_star_pos or j == second_star_pos:
                    desired_output += '*'
                else:
                    desired_output += ' '

            if first_star_pos == 0:
                first_star_direction = 1
                second_star_direction = -1
                
            first_star_pos += first_star_direction
            second_star_pos += second_star_direction

            desired_output += '\n'

        return desired_output

    for x in range(5, 10):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for diamond.c')
            print()
            return False

    print('Tests passed for diamond.c')
    print()

    return True


def main(submission_dir):
    all_passed = True

    test_functions = {
        'diamond.c': diamond,
        'checkerboard.c': checkerboard
    }

    for filename in test_functions:
        path = os.path.join(submission_dir, filename)

        if not os.path.isfile(path):
            print(filename, 'does not exist.')
            all_passed = False
            continue

        try:
            run_command(['gcc', '-std=gnu99', path])
        except Exception:
            print(filename, 'did not compile.')
            print()
            all_passed = False
            continue

        try:
            if not test_functions[filename]():
                all_passed = False
        except Exception as e:
            print('Problems running', filename)
            print(e)
            print()
            all_passed = False

    if all_passed:
        print('All tests passed, hooray!')
    else:
        print('There were test failures.')


if __name__ == '__main__':
    main(sys.argv[1])
