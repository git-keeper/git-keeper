#!/bin/bash

TIMEOUT=5

# Set $TIMEOUT_CMD to be timeout or gtimeout
if command -v timeout &> /dev/null
then
    TIMEOUT_CMD=timeout
elif command -v gtimeout &> /dev/null
then
    TIMEOUT_CMD=gtimeout
else
    echo "Could not find timeout or gtimeout commands"
    exit 1
fi

DIRECTORY=$1
CLASSNAME=PowersOf2

javac -cp "$DIRECTORY/src/" "$DIRECTORY/src/$CLASSNAME.java" &> compiler_output.txt
if [ $? -ne 0 ]
then
    echo "There was an error compiling your code. Please try again."
    echo
    echo "Compiler output:"
    cat compiler_output.txt
    exit 0
fi

"$TIMEOUT_CMD" "$TIMEOUT" java -cp "$DIRECTORY/src" "$CLASSNAME" &> output.txt

if [ $? -eq 124 ]
then
    echo "Your code took too long to run. Perhaps you have an infinte loop? Please try again."
    exit 0
fi

diff correct_output.txt output.txt &> /dev/null

if [ $? -ne 0 ]
then
    echo "Your output was not correct. Please try again."
    exit 0
fi

echo "All tests passed, good job!"
exit 0
