TIMEOUT=5
MEM_LIMIT_MB=400

MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

ulimit -v $MEM_LIMIT_KB

py_file="$1/lists_hw.py"

if [ ! -f $py_file ]
then
    echo "lists_hw.py does not exist."
    exit 0
fi

#timeout $TIMEOUT python3 test.py "$py_file" 2> /dev/null
python3 test.py "$py_file"

exit 0
