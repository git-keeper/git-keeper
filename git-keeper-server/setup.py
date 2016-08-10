# setup.py for git-keeper-server

from setuptools import setup

setup(
    name='git-keeper-server',
    version='0.1.0',
    description=('A git-based system for distributing and collecting '
                 'programming assignments with automatic feedback.'),
    url='https://github.com/git-keeper/git-keeper',
    author='Nathan Sommer and Ben Coleman',
    author_email='git-keeper@googlegroups.com',
    license='GPL 3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
        'Topic :: Education :: Testing',
        'Topic :: Education'
    ],
    packages=['gkeepserver', 'gkeepserver.event_handlers'],
    entry_points={
        'console_scripts': ['gkeepd=gkeepserver.gkeepd:main'],
    },
    package_data={
        'gkeepserver': ['data/*']
    },
    install_requires=['git-keeper-core', 'paramiko', 'pyinotify'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
