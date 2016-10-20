#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_match {
    FILEPATH=$1
    INPUT=$2
    PATTERN1=$3
    PATTERN2=$4

    OUTPUT="$(timeout "$TIMEOUT" python3 $FILEPATH <<< "$INPUT")"
    if [ $? -ne 0 ]
    then
        echo
        echo "Your code exited with an error."
        echo
        echo "Please try again."
        exit 0
    fi
    
    echo "$OUTPUT" | grep "$PATTERN1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "When given the year $INPUT the number of countries should be $PATTERN1"
	echo ""
	echo "Please try again."
        exit 0
    fi

    echo "$OUTPUT" | grep "$PATTERN2" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "When given the year $INPUT the average should be (about) $PATTERN2"
	echo ""
	echo "Please try again."
        exit 0
    fi

}

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=year_average.py

FILEPATH="$SUBMISSION_DIR/$FILENAME"

# make sure the student's file exists
if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

# Run the tests
test_match "$FILEPATH" "1980" "164" "18.04"
test_match "$FILEPATH" "1990" "166" "74.23"
test_match "$FILEPATH" "2000" "191" "80.96"

timeout "$TIMEOUT" python3 "$FILEPATH" <<< 1900 > /dev/null

if [ $? -ne 0 ]
then
    echo
    echo "Your program should not crash when given the year 1900."
    echo
    echo "Please try again."
    exit 0
fi

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
