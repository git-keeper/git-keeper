py_file="$1/strings_hw.py"

if [ ! -f $py_file ]
then
    echo "strings_hw.py does not exist."
    exit 0
fi

python3 test.py "$py_file" 2> /dev/null

exit 0

