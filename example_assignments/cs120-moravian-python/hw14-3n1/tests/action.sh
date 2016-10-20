#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_match {
    FILEPATH=$1
    USER_N=$2
    EXPECTED_FILENAME="$USER_N.txt"

    echo -e "$USER_N" | timeout "$TIMEOUT" python3 $FILEPATH 1> output.txt 2> /dev/null
    if [ $? -ne 0 ]
    then
        echo
        echo "Your code exited with an error."
        echo
        echo "Please try again."
        exit 0
    fi
    
    # Check that the expected output is a substring of the student's output
    if [[ $(cat output.txt) != *"$(cat $EXPECTED_FILENAME)"* ]]
    then
        echo "Your output does not match the expected output with n = $USER_N."
	      echo ""
        echo "Expected this to be in your output:"
        echo ""
        cat "$EXPECTED_FILENAME"
        echo ""
        echo "Your output was this:"
        echo ""
        cat output.txt
        exit 0
    fi
}

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=3n1.py
FILEPATH="$1/$FILENAME"

TEST_PATH=$(pwd)

# make sure the student's file exists
if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

# Run the tests
test_match "$FILEPATH" "13"
test_match "$FILEPATH" "1000"

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
