#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_match {
    FILEPATH=$1
    INPUT=$2
    PATTERN=$3

    OUTPUT="$(timeout "$TIMEOUT" python3 $FILEPATH <<< "$INPUT")"
    if [ $? -ne 0 ]
    then
        echo "Your code exited with an error."
        exit 0
    fi
    
    echo "$OUTPUT" | grep -E "$PATTERN" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "When given the value $INPUT the output should be $PATTERN"
        exit 0
    fi
}

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=fahrenheit_to_celsius.py

FILEPATH="$SUBMISSION_DIR/$FILENAME"

# make sure the student's file exists
if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

# Run the tests
test_match "$FILEPATH" "95" "35.0"
test_match "$FILEPATH" "212" "100.0"

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
