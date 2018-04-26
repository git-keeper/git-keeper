import time
import glob
import sys


def no_email_to(to):
    for tries in range(10):
        if len(glob.glob('/email/{}_*.txt'.format(to))) is not 0:
            return False
        time.sleep(.1)

    return True


print(no_email_to(sys.argv[1]))