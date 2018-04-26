from gkeeprobot.dectorators import polling
import glob
import sys


@polling
def no_email_to(to):
    if len(glob.glob('/email/{}_*.txt'.format(to))) is 0:
        return True
    return False


print(no_email_to(sys.argv[1]))