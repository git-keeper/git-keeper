#!/bin/bash

TIMEOUT=5

function test_match {
    DIRECTORY="$1"
    INPUT="$2"
    EXPECTED="$3"

    echo -e "$INPUT" | timeout "$TIMEOUT" java -cp "$1/src" Main 1> output.txt 2> /dev/null
    if [ $? -ne 0 ]
    then
        echo
        echo "Your code exited with an error."
        echo
        echo "Please try again."
        exit 0
    fi
    
    # Check that the expected output is a substring of the student's output
    if [[ $(cat output.txt) != *"$EXPECTED"* ]]
    then
        echo "Expected to find $EXPECTED in your output when entering the following names:"
        echo -e "$INPUT"
        echo
        echo "Please try again."
        exit 0
    fi
}

function test_no_match {
    DIRECTORY="$1"
    INPUT="$2"
    EXPECTED="$3"

    echo -e "$INPUT" | timeout "$TIMEOUT" java -cp "$1/src" Main 1> output.txt 2> /dev/null
    if [ $? -ne 0 ]
    then
        echo
        echo "Your code exited with an error."
        echo
        echo "Please try again."
        exit 0
    fi
    
    # Check that the expected output is not a substring of the student's output
    if [[ $(cat output.txt) == *"$EXPECTED"* ]]
    then
        echo "Should not have found $EXPECTED in your output when entering the following names:"
        echo -e "$INPUT"
        echo
        echo "Please try again."
        exit 0
    fi
}

DIRECTORY=$1
CLASSNAME=Main
MYTESTS=Main

javac -cp $1/src/ $1/src/$CLASSNAME.java &> compiler_output.txt
if [ $? -ne 0 ]
then
    echo "Errors while trying to compile your code:"
    echo
    cat compiler_output.txt
    exit 0
fi

# Run the tests
test_match "$DIRECTORY" "Sue\nGrace\nWilma\nDora\n"  "Grace"
test_match "$DIRECTORY" "Sue\nGrace\nWilma\nDora\n"  "Wilma"
test_no_match "$DIRECTORY" "Sue\nGrace\nWilma\nDora\n"  "Sue"
test_no_match "$DIRECTORY" "Sue\nGrace\nWilma\nDora\n"  "Dora"

test_match "$DIRECTORY" "Larry\nBob\nGary\nSteve\n"  "Larry"
test_match "$DIRECTORY" "Larry\nBob\nGary\nSteve\n"  "Steve"
test_no_match "$DIRECTORY" "Larry\nBob\nGary\nSteve\n"  "Bob"
test_no_match "$DIRECTORY" "Larry\nBob\nGary\nSteve\n"  "Gary"

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
