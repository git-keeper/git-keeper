import os
import sys

from gkeepcore.shell_command import run_command


def non_negative_integers():
    def generate_desired_output(n):
        desired_output = ''
        for x in range(n):
            desired_output += '{0}\n'.format(x)
        return desired_output

    for x in range(5, 1000, 50):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for non_negative_integers.c')
            print()
            return False

    print('Tests passed for non_negative_integers.c')
    print()

    return True


def multiples_of_5_not_3():
    desired_output = ''
    multiple = 5
    while multiple < 1000:
        if multiple % 3 != 0:
            desired_output += '{0}\n'.format(multiple)
        multiple += 5

    output = run_command('./a.out')

    if desired_output not in output:
        print('Incorrect output for multiples_of_5_not_3.c')
        print()
        return False

    print('Tests passed for multiples_of_5_not_3.c')
    print()

    return True


def powers_of_2():
    def generate_desired_output(n):
        desired_output = ''
        for x in range(n):
            desired_output += '{0}\n'.format(2 ** x)
        return desired_output

    for x in range(5, 20, 3):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for powers_of_2.c')
            print()
            print(generate_desired_output(x))
            return False

    print('Tests passed for powers_of_2.c')
    print()

    return True


def main(submission_dir):
    all_passed = True

    test_functions = {
        'non_negative_integers.c': non_negative_integers,
        'multiples_of_5_not_3.c': multiples_of_5_not_3,
        'powers_of_2.c': powers_of_2,
    }

    for filename in test_functions:
        path = os.path.join(submission_dir, filename)

        if not os.path.isfile(path):
            print(filename, 'does not exist.')
            all_passed = False
            continue

        try:
            run_command(['gcc', '-std=c99', path])
        except Exception:
            print(filename, 'did not compile.')
            print()
            all_passed = False
            continue

        try:
            if not test_functions[filename]():
                all_passed = False
        except Exception:
            print('Problems running', filename)
            print()
            all_passed = False

    if all_passed:
        print('All tests passed, hooray!')
    else:
        print('There were test failures.')


if __name__ == '__main__':
    main(sys.argv[1])
