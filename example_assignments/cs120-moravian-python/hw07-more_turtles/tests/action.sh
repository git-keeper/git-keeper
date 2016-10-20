SUBMISSION_DIR=$1

ASSIGNMENT_FILE="$1/more_turtles.py"

if [ ! -f "$ASSIGNMENT_FILE" ]
then
    echo "more_turtles.py does not exist!"
    exit 0
fi

line_count=$(wc -l "$ASSIGNMENT_FILE" | cut -f 1 -d " ")

if [ $line_count == "0" ]
then
    echo "more_turtles.py is an empty file!"
    exit 0
fi

grep -i turtle "$ASSIGNMENT_FILE" &> /dev/null

if [ $? -ne 0 ]
then
    echo "The string 'turtle' was nowhere to be found in more_turtles.py."
    exit 0
fi

echo "Your assignment was received. You will get feedback from your instructor."
exit 0
