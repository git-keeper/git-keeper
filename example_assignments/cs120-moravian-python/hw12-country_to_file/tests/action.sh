#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_match {
    FILEPATH=$1
    COUNTRY=$2
    EXPECTED_FILENAME=$3
    STUDENT_FILENAME=$4

    echo -e "$COUNTRY\n$STUDENT_FILENAME" | timeout "$TIMEOUT" python3 $FILEPATH &> /dev/null
    if [ $? -ne 0 ]
    then
        echo
        echo "Your code exited with an error."
        echo
        echo "Please try again."
        exit 0
    fi
    
    if [ ! -f $STUDENT_FILENAME ]
    then
        echo "Your program did not produce the appropriate output file."
        exit 0
    fi

    diff "$EXPECTED_FILENAME" "$STUDENT_FILENAME" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Your output file does not match the expected output."
	      echo ""
        echo "Expected this:"
        echo ""
        cat "$EXPECTED_FILENAME"
        echo ""
        echo "Got this:"
        echo ""
        cat "$STUDENT_FILENAME"
        exit 0
    fi
}

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=country_to_file.py

TEST_PATH=$(pwd)

cd $SUBMISSION_DIR

# make sure the student's file exists
if [ ! -f $FILENAME ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

# Run the tests
test_match "$FILENAME" "Canada" "$TEST_PATH/canada.txt" "canada_test.txt"
test_match "$FILENAME" "Viet Nam" "$TEST_PATH/viet_nam.txt" "viet_name_test.txt"

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
