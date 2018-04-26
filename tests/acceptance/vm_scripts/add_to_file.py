import sys


def add_to_file(file_name, to_add):
    with open(file_name, "a") as f:
        f.write(to_add + '\n')

add_to_file(sys.argv[1], sys.argv[2])