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

FILENAME=weeks_and_days.py

FILEPATH="$SUBMISSION_DIR/$FILENAME"

echo "Running tests for $FILENAME"

if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

test_match "$FILEPATH" "39" "That is 5 weeks and 4 days."
test_match "$FILEPATH" "0" "That is 0 weeks and 0 days."
test_match "$FILEPATH" "14" "That is 2 weeks and 0 days."
test_match "$FILEPATH" "20" "That is 2 weeks and 6 days."
test_match "$FILEPATH" "123456790" "That is 17636684 weeks and 2 days."


echo "All tests passed, good job!"

exit 0
