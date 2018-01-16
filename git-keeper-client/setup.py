# setup.py for git-keeper-client

from setuptools import setup
from gkeepclient.version import __version__

setup(
    name='git-keeper-client',
    version=__version__,
    description=('A git-based system for distributing and collecting '
                 'programming assignments with automatic feedback.'),
    url='https://github.com/git-keeper/git-keeper',
    license='GPL 3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
        'Topic :: Education :: Testing',
        'Topic :: Education'
    ],
    packages=['gkeepclient'],
    entry_points={
        'console_scripts': ['gkeep=gkeepclient.gkeep:main'],
    },
    install_requires=['git-keeper-core', 'paramiko', 'argcomplete'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
