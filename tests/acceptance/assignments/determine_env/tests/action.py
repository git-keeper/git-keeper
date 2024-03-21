import os

if os.path.isfile('/.dockerenv'):
    print('docker')
elif os.getcwd() == '/home/tester/tests':
    print('firejail')
else:
    print('host')
