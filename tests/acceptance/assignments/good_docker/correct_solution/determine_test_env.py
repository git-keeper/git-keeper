import os
if os.path.isfile('/.dockerenv'):
    print('In Docker')
else:
    print('On Host')
