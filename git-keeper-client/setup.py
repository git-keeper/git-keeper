# setup.py for git-keeper-client

from setuptools import setup
from gkeepclient.version import __version__

with open('README.md') as f:
    long_description = f.read()

setup(
    name='git-keeper-client',
    version=__version__,
    description=('A git-based system for distributing and collecting '
                 'programming assignments with automatic feedback.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/git-keeper/git-keeper',
    author='Nathan Sommer and Ben Coleman',
    author_email='git-keeper@googlegroups.com',
    license='GPL 3',
    classifiers=[
        'Development Status :: 4 - Beta',
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
)
