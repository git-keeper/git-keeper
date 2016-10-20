#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_match {
    INPUT=$1
    PATTERN=$2

    OUTPUT="$(timeout "$TIMEOUT" ./a.out <<< "$INPUT")"
    if [ $? -ne 0 ]
    then
        echo "Your code exited with an error."
        exit 0
    fi
    
    echo "$OUTPUT" | grep -E -- "$PATTERN" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Incorrect output. When given the value $INPUT I expected to see $PATTERN. Please try again."
        exit 0
    fi
}

function test_mismatch {
    INPUT=$1
    PATTERN=$2

    OUTPUT="$(timeout "$TIMEOUT" ./a.out <<< "$INPUT")"
    if [ $? -ne 0 ]
    then
        echo "Your code exited with an error."
        exit 0
    fi
    
    echo "$OUTPUT" | grep -E -- "$PATTERN" &> /dev/null
    if [ $? -eq 0 ]
    then
        echo "Incorrect output. When given the value $INPUT I expected NOT to see $PATTERN. Please try again."
        exit 0
    fi
}

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=fahrenheit_to_celsius.c

cd $SUBMISSION_DIR

# make sure the student's file exists
if [ ! -f $FILENAME ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

gcc -std=c99 $FILENAME &> compilation_output.txt

if [ $? -ne 0 ]
then
    echo "There were errors compiling your code:"
    cat compilation_output.txt
    exit 0
fi

# Run the tests
test_match "92" "33"
test_match "92" "hot"
test_mismatch "92" "cold"
test_match "91" "32"
test_mismatch "91" "hot"
test_mismatch "91" "cold"
test_match "212" "100"
test_match "212" "hot"
test_mismatch "212" "cold"
test_match "31" "0"
test_mismatch "31" "hot"
test_mismatch "31" "cold"
test_match "30" "-1"
test_mismatch "30" "hot"
test_match "30" "cold"

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
