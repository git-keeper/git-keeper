
from gkeeprobot.dectorators import polling
import glob
import sys


@polling
def email(to, contains):
    for file in glob.glob('/email/{}_*.txt'.format(to)):
        with open(file) as f:
            if contains in f.read():
                return True
    return False


print(email(sys.argv[1], sys.argv[2]))