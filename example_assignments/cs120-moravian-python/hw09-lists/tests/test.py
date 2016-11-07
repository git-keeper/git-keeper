import sys
import subprocess


def run_tests(py_file, input_filename):
    number_list = []

    with open(input_filename) as f:
        first_skipped = False
        for line in f:
            if not first_skipped:
                first_skipped = True
                continue

            number_list.append(eval(line.rstrip()))

    print('Running by entering this list: {0}'.format(number_list))

    command = 'python3 {0} < {1}'.format(py_file, input_filename)

    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print('There was an error_message running your program.')
        sys.exit()
        
    output = output.decode()

    errors = 0

    if str(min(number_list)) not in output:
        print('Did not print the min ({0})'.format(min(number_list)))
        errors += 1
    if str(max(number_list)) not in output:
        print('Did not print the max ({0})'.format(max(number_list)))
        errors += 1
    if str(sum(number_list)) not in output:
        print('Did not print the sum ({0})'.format(sum(number_list)))
        errors += 1
    if str(sum(number_list)/len(number_list)) not in output:
        print('Did not print the average ({0})'.format(sum(number_list)/len(number_list)))
        errors += 1

    if errors == 1:
        print('1 error_message\n')
    else:
        print('{0} errors\n'.format(errors))
    


def main():
    py_file = sys.argv[1]

    for filename in ['input1.txt', 'input2.txt']:
        run_tests(py_file, filename)

    
if __name__ == '__main__':
    main()
