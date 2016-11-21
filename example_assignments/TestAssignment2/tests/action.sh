#!/bin/bash

TIMEOUT=10
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

SUBMISSION_DIR=$1

if [ ! -f "$SUBMISSION_DIR/triangle.h" ]
then
    echo "linked_list.h does not exist."
    exit 0
fi

if [ ! -f "$SUBMISSION_DIR/triangle.c" ]
then
    echo "linked_list.h does not exist."
    exit 0
fi

cp "$SUBMISSION_DIR/triangle.h" . &> /dev/null
cp "$SUBMISSION_DIR/triangle.c" . &> /dev/null

timeout $TIMEOUT make &> compilation_output.txt

if [ $? -ne 0 ]
then
    echo "Your triangle module does not compile correctly with my tests:"
    echo
    cat compilation_output.txt
    exit 0
fi

./triangle_tests > output.txt 2> /dev/null

if [ -s output.txt ]
then
    echo "There were errors:"
    echo
    cat output.txt
else
    echo "All tests passed!"
fi

exit 0
