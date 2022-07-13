# setup.py for git-keeper-core

from setuptools import setup
from gkeepcore.version import __version__

with open('README.md') as f:
    long_description = f.read()

setup(
    name='git-keeper-core',
    version=__version__,
    description='Core modules for git-keeper-client and git-keeper-server.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/git-keeper/git-keeper',
    author='Nathan Sommer and Ben Coleman',
    author_email='git-keeper@googlegroups.com',
    license='GPL 3',
    classifiers=[
        'Development Status :: 4 - Beta',
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
    install_requires=['pyyaml'],
)
