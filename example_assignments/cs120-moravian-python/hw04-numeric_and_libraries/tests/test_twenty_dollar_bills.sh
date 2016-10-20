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
        echo "When given the value $INPUT the output should be this:
$PATTERN"
        exit 0
    fi
}

SUBMISSION_DIR=$1

FILENAME=twenty_dollar_bills.py

FILEPATH="$SUBMISSION_DIR/$FILENAME"

echo "Running tests for $FILENAME"

if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

test_match "$FILEPATH" "55.75" "You need 3 twenty dollar bills."
test_match "$FILEPATH" "0" "You need 0 twenty dollar bills."
test_match "$FILEPATH" "40" "You need 2 twenty dollar bills."
test_match "$FILEPATH" "100.01" "You need 6 twenty dollar bills."
test_match "$FILEPATH" "123456789" "You need 6172840 twenty dollar bills."

echo "All tests passed, good job!"

exit 0
