# HW 14 - 3n + 1 Problem

The 3n + 1 problem is based on an interesting pattern: Take an integer n and
apply the following rules:

* If n is even, then divide it by 2
* If n is odd, then multiply it by 3 and add 1

Take the resulting number and apply the same rules. Repeat. For example, if we
pick n = 22, then the pattern will be:

    22 11 34 17 52 26 13 40 20 10 5 16 8 4 2 1 4 2 1 ...

Notice that when the sequence reaches 1, it repeats. This pattern has generated
for a great many positive integers and so far nobody has found one that does
not eventually reach 1. However, mathematicians have also been unable to prove
that it will reach 1 for all positive integers.

Write a program that asks the user to enter a positive integer and then prints
out the 3n + 1 sequence starting with that integer until the sequence
reaches 1. Print each number of the sequence on its own line.
