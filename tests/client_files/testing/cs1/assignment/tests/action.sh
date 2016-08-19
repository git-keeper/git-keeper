#!/bin/bash

# The path to the student's submission is the first argument to the script
SUBMISSION_DIR=$1

FILENAME=50names.py

# Copy the student's python file here, supressing output
cp $SUBMISSION_DIR/$FILENAME . > /dev/null 2>&1

# Check the return code of the copy. If it failed, print an error and exit.
if [ $? -ne 0 ]
then
    echo $FILENAME 'does not exist'
    exit 0
fi

numlines=`python3 $FILENAME | wc -l | awk '{print $1}'`;

if [ $numlines -ne 50 ]
then
    echo "Your program should output your name 50 times on separate lines."
    exit 0
fi

echo "Nice work!  Your output looks correct!"

# Make sure to exit 0!
exit 0




