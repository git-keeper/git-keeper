#!/bin/bash

DIRECTORY=$1
CLASSNAMES="Gradebook"
REQUIRED_FILES="src/Gradebook.java src/AssignmentGrade.java"

for f in $REQUIRED_FILES
do
    if [ ! -f "$DIRECTORY/$f" ]
    then
        echo "$f does not exist. Please add it and submit again."
        echo
        echo "All files must be in place before your code will be tested. This push will not count as one of your tested submissions."
        exit 0
    fi
done

for CLASSNAME in $CLASSNAMES
do
    CLASSFILE="${CLASSNAME}.java"
    CLASSFILEPATH="$1/src/${CLASSFILE}"

    TESTCLASS="${CLASSNAME}Test"
    TESTFILEPATH="tests/${TESTCLASS}.java"

    javac -cp $1/src/ $CLASSFILEPATH &> compiler_output.txt
    if [ $? -ne 0 ]
    then
        echo "Errors while trying to compile $CLASSFILE:"
        echo
        cat compiler_output.txt
        exit 0
    fi

    javac -cp junit-4.12.jar:$1/src/ $TESTFILEPATH &> compiler_output.txt

    if [ $? -ne 0 ]
    then
        echo "Errors compiling your code with my tests:"
        echo
        cat compiler_output.txt
        exit 0
    fi

    echo "Below is the output from testing $CLASSNAME:"
    echo

    java -cp $1/src/:tests/:junit-4.12.jar:hamcrest-core-1.3.jar org.junit.runner.JUnitCore $TESTCLASS
done

exit 0
