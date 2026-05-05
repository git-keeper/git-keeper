# Checks that files in the tests folder and the base_code folder are or are
# not executable as appropriate.

base_code_dir="$1"

file_executable="executable"
file_not_executable="not_executable"

check_executable() {
    local file_path="$1"
    local should_be_executable="$2"

    if [ "$should_be_executable" = true ]; then
        if [ ! -x "$file_path" ]; then
            echo "$file_path should be executable"
            exit 1
        fi
    else
        if [ -x "$file_path" ]; then
            echo "$file_path should not be executable"
            exit 1
        fi
    fi
}

# Check the files in tests
check_executable "./$file_executable" true
check_executable "./$file_not_executable" false
check_executable "./subdir/$file_executable" true
check_executable "./subdir/$file_not_executable" false

# Check the files in base_code
check_executable "$base_code_dir/$file_executable" true
check_executable "$base_code_dir/$file_not_executable" false
check_executable "$base_code_dir/subdir/$file_executable" true
check_executable "$base_code_dir/subdir/$file_not_executable" false

echo "Success"

exit 0
