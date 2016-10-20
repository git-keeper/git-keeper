TIMEOUT=10
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

py_file="$1/print_countries.py"

if [ ! -f $py_file ]
then
    echo "print_countries.py does not exist."
    exit 0
fi

timeout $TIMEOUT python3 "$py_file" > output.txt 2> /dev/null

if [ $? -ne 0 ]
then
    echo "Your program exited with an error."
    exit 0
fi

diff correct_output.txt output.txt &> /dev/null

if [ $? -ne 0 ]
then
    echo "Your program's output is not correct."
    exit 0
fi

echo "All tests passed!"

exit 0
