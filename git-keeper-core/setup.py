# setup.py for git-keeper-core

from setuptools import setup
from gkeepcore.version import __version__

setup(
    name='git-keeper-core',
    version=__version__,
    description='Core modules for git-keeper-client and git-keeper-server.',
    url='https://github.com/git-keeper/git-keeper',
    license='GPL 3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
        'Topic :: Education :: Testing',
        'Topic :: Education'
    ],
    packages=['gkeepcore'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
