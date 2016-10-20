#!/bin/bash

javac -cp $1/src/ $1/src/Main.java &> compiler_output.txt
if [ $? -ne 0 ]
then
    echo "Errors while trying to compile your code:"
    echo
    cat compiler_output.txt
    exit 0
fi

java -cp $1/src Main 1> output.txt 2> /dev/null
if [ $? -ne 0 ]
then
    echo "Running your main() method resulted in an error."
    echo
    echo "Please try again."
    exit 0
fi

grep Square output.txt &> /dev/null
if [ $? -ne 0 ]
then
    echo "Expected the output of your main() to contain \"Square\""
    echo
    echo "Please try again."
    exit 0
fi

grep 'Regular triangle' output.txt &> /dev/null
if [ $? -ne 0 ]
then
    echo "Expected the output of your main() to contain \"Regular triangle\""
    echo
    echo "Please try again."
    exit 0
fi

grep "Right triangle" output.txt &> /dev/null
if [ $? -ne 0 ]
then
    echo "Expected the output of your main() to contain \"Right triangle\""
    echo
    echo "Please try again."
    exit 0
fi

DIRECTORY=$1
CLASSNAME=RightTriangle
MYTESTS=RightTriangleTest

javac -cp $1/src/ $1/src/$CLASSNAME.java &> compiler_output.txt
if [ $? -ne 0 ]
then
    echo "Errors while trying to compile your code:"
    echo
    cat compiler_output.txt
    exit 0
fi

javac -cp junit-4.12.jar:$1/src/ tests/$MYTESTS.java &> compiler_output.txt

if [ $? -ne 0 ]
then
    echo "Errors compiling your code with my tests:"
    echo
    cat compiler_output.txt
    exit 0
fi

echo "Below is the output from testing $CLASSNAME:"
echo

java -cp $1/src/:tests/:junit-4.12.jar:hamcrest-core-1.3.jar org.junit.runner.JUnitCore $MYTESTS




exit 0
