import os

proc_data = open('/proc/1/cgroup').read()

if 'docker' in proc_data:
    print('docker')
elif os.getcwd() == '/home/tester/tests':
    print('firejail')
else:
    print('host')
