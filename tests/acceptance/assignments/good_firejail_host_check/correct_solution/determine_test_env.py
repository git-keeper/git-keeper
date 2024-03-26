
proc_data = open('/proc/1/cgroup').read()
if 'docker' in proc_data:
    print('In Docker')
else:
    print('On Host')
