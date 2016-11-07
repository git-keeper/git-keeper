import sys
import subprocess


def print_tests_passed(correct_count, total_count):
    print()
    print(correct_count, 'out of', total_count, 'tests passed')


def main():
    print("Your program was run with the strings 'Computer' and 'Science' as input.")
    print()

    correct_count = 0
    test_count = 7

    command = 'python3 {0} < input.txt'.format(sys.argv[1])

    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print('There was an error_message running your program.')
        print_tests_passed(correct_count, total_count)
        sys.exit()

    output = output.decode().split('\n')

    if len(output) == 0:
        print('There was an error_message running your program.')
        print_tests_passed(correct_count, total_count)
        sys.exit()

    if output[0].endswith('Computer'):
        correct_count += 1
    else:
        print("Expected to see the string 'Computer'")

    expected_lines = ['Science', 'COMPUTERscience', 'ScienceScienceScience',
                      'Ce', 'CoSc', 'C o m p u t e r ']

    for line in expected_lines:
        if line in output:
            correct_count += 1
        else:
            print("Expected to see the string '{0}'".format(line))

    print_tests_passed(correct_count, test_count)

    
if __name__ == '__main__':
    main()
