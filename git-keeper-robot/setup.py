from setuptools import setup
from gkeepcore.version import __version__

setup(
    name='git-keeper-robot',
    version=__version__,
    description='Modules used for testing git-keeper.',
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
    packages=['gkeeprobot'],
)
