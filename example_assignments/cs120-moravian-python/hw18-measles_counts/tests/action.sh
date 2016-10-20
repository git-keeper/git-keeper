#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=measles_counts.py

FILEPATH="$SUBMISSION_DIR/$FILENAME"

# make sure the student's file exists
if [ ! -f $FILEPATH ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

#timeout "$TIMEOUT" python3 "$FILEPATH" 1> student_output.txt 2> /dev/null
python3 "$FILEPATH" 1> student_output.txt 2> /dev/null

if [ $? -ne 0 ]
then
    echo
    echo "Your program exited with an error."
    echo
    echo "Please try again."
    exit 0
fi

diff -w <(sort solution_list.txt) <(sort student_output.txt) &> /dev/null

if [ $? -ne 0 ]
then
    echo
    echo "Expected these countries:"
    echo
    cat solution_list.txt | sort
    echo
    echo "Please try again."
    exit 0
fi

echo "All tests passed, good job!"

# Make sure to exit 0!
exit 0
