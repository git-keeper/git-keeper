#!/bin/bash

DIRECTORY=$1
CLASSNAME=DogPairPrinter
MYTESTS=DogPairPrinterTest

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

echo "Below is the output from testing your code:"
echo

java -cp $1/src/:tests/:junit-4.12.jar:hamcrest-core-1.3.jar org.junit.runner.JUnitCore $MYTESTS

exit 0
