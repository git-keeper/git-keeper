#!/bin/bash

TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

function test_diff {
    PYTHON_FILE=$1
    EXPECTED_OUTPUT_FILE=$2
    OUTPUT_FILE=$(mktemp)

    timeout "$TIMEOUT" python3 "$PYTHON_FILE" &> "$OUTPUT_FILE"
    if [ $? -ne 0 ]
    then
        echo "Your code exited with an error:"
        cat "$OUTPUT_FILE"
        rm $OUTPUT_FILE
        return
    fi
    
    diff "$EXPECTED_OUTPUT_FILE" "$OUTPUT_FILE" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Incorrect output. Expected this:"
        cat "$EXPECTED_OUTPUT_FILE"
        echo
        echo "Got this:"
        cat "$OUTPUT_FILE"
        echo
    else
        echo "Test passed!"
    fi

    rm $OUTPUT_FILE
}

SUBMISSION_DIR=$1

echo "Testing simple_range.py"
test_diff "$SUBMISSION_DIR/simple_range.py" simple_range.txt
echo

echo "Testing range_starting_point.py"
test_diff "$SUBMISSION_DIR/range_starting_point.py" starting_point.txt
echo

echo "Testing range_square_evens.py"
test_diff "$SUBMISSION_DIR/range_square_evens.py" square_evens.txt
echo

exit 0
