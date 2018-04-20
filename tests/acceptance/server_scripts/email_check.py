
import time
import glob
import sys

def email(to, contains):
    for tries in range(10):
        for file in glob.glob('/email/{}_*.txt'.format(to)):
            with open(file) as f:
                if contains in f.read():
                    return True
        time.sleep(.1)

    return False


print(email(sys.argv[1], sys.argv[2]))