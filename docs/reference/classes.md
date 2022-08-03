# Classes

A class is owned by a single faculty user, and consists of a collection of
students and assignments.

A new class is created using the [`gkeep add`]() command, and the roster can be
modified using [`gkeep modify`]().

A class name may only contain the characters `A-Z`, `a-z`, `0-9`, `-`, and `_`.

The status of a class may be `open` or `closed`. If a student tries to submit
to a closed class, tests will not run and they will receive an email that the
class is closed.
