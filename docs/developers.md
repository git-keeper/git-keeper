# Developers

## Project Organization

There are 3 distributions in this project:

* `git-keeper-client`
* `git-keeper-core`
* `git-keeper-server`

Both `git-keeper-client` and `git-keeper-server` depend on `git-keeper-core`.

When developing, all 3 distributions should be installed in development mode
by running `python setup.py develop` in the top level directory of all 3
distributions, starting with `git-keeper-core`.

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
