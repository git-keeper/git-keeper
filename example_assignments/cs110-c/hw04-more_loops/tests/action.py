import os
import sys

from gkeepcore.shell_command import run_command


def square():
    def generate_desired_output(n):
        desired_output = ['*' * n for x in range(n)]
        desired_output = '\n'.join(desired_output)
        return desired_output

    for x in range(1, 10):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for square.c')
            print()
            return False

    print('Tests passed for square.c')
    print()

    return True


def triangle():
    def generate_desired_output(n):
        desired_output = ['*' * (x + 1) for x in range(n)]
        desired_output = '\n'.join(desired_output)
        return desired_output

    for x in range(1, 10):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for triangle.c')
            print()
            return False

    print('Tests passed for triangle.c')
    print()

    return True


def pyramid():
    def generate_desired_output(n):
        desired_output = ''

        for i in range(n):
            space_count = n - (i + 1)
            star_count = 2 * (i + 1) - 1

            for j in range(space_count):
                desired_output += ' '

            for j in range(star_count):
                desired_output += '*'

            desired_output += '\n'

        return desired_output


    for x in range(1, 10):
        output = run_command('./a.out <<< {0}'.format(x))

        if generate_desired_output(x) not in output:
            print('Incorrect output for pyramid.c')
            print()
            return False

    print('Tests passed for pyramid.c')
    print()

    return True


def main(submission_dir):
    all_passed = True

    test_functions = {
        'square.c': square,
        'triangle.c': triangle,
        'pyramid.c': pyramid
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
