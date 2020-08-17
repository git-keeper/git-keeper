# Developers

## Project Organization

There are 3 distributions in this project:

* `git-keeper-client`
* `git-keeper-core`
* `git-keeper-server`

Both `git-keeper-client` and `git-keeper-server` depend on `git-keeper-core`.

## Developer Setup

The preferred development environment is PyCharm on OSX or Linux.  The following steps will ensure that your development environment is isolated from the system Python and other Python projects.

### Prerequisites

* [Python 3.4 or greater](https://www.python.org/downloads/)

### Setup Process


* Fork the `git-keeper/git-keeper` repo to your personal GitHub account.
* Clone the repo from your GitHub account
* `cd git-keeper`
* Create a virtual environment named `.env`.  The `.gitignore` file ensures that the `.env` folder is ignored.

 ```
 python3 -m venv .env
 ```
 
* Activate the virtual environment.

 ```
 source .env/bin/activate
 ```
 
* Install the required dependencies.

 ```
 pip install -r requirements.txt
 ```
 
* Install the project modules `git-keeper-core`, `git-keeper-client`, and `git-keeper-server` as editable.  This will allow the IDE to recognize the `git-keeper` modules.

 ```
 pip install -e git-keeper-core
 pip install -e git-keeper-client
 pip install -e git-keeper-server
 pip install -e git-keeper-robot
 ```

* Open the project in PyCharm, and wait for it to index the packages.

If you clone the repo from within PyCharm, you will have to change the project interpreter after you create the virtual environment.  Also, if you have the project open in PyCharm when you install the `git-keeper` modules, you will have to restart PyCharm before it will recognize the names (this is a known bug in PyCharm).


## Style

We strive for consistent style within this project. Contributions may not be
accepted if they do not follow these guidelines.

* Project filenames
    * Most filenames should be all lowercase with words separated by
    underscores
    * Use all uppercase for files like `README.md` and `COPYING`
* Documentation
    * Place documentation in the `docs` directory. If you add a new file, add
    it to the table of contents in `mkdocs.yml`.
    * Use markdown
    * Limit lines of text to 80 characters
* Python
    * Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) whenever
    possible
    * Variable names
        * Avoid abbreviations unless the meaning remains clear or length gets
        way out of hand
            * `cls` is not ok for class
            * `config` is ok for configuration
        * Quantities
            * Use `item_count` vs `num_items`
        * Dictionaries
            * Use `<value>s_by_<key>` (i.e. `students_by_class`)
        * Indexes
            * For an index into a single list, use `i`
            * For nested loops and other situations with multiple indexes, use a
            variable name ending in `_i` (i.e. `student_i` and `class_i`)
        * Filenames, directory names, and full paths
            * File and directory basenames (no path)
                * End filename variable names with `_filename`
                * End directory name variable names with `_dir`
            * Full paths
                * End the variable name with `_path`. If it is ambiguous
                whether it is a file or directory, end it with `_file_path` or
                `_dir_path`
    * Type hinting
        * Use type hints for all parameters that are object references
    * Importing
        * Either import an entire module (`import os`) or import specific
        items (`from queue import Queue, Empty`) but do not import all items
        from a module (do not say `from os import *`)
        * Import system-level items first followed by imports that are
        internal to the project
