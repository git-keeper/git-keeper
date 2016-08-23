#!/bin/bash

GLOBAL_TIMEOUT=300
GLOBAL_MEM_LIMIT_MB=1024

GLOBAL_MEM_LIMIT_KB=$(($GLOBAL_MEM_LIMIT_MB * 1024))

ulimit -v $GLOBAL_MEM_LIMIT_KB

trap 'kill -INT -$pid' INT

timeout $GLOBAL_TIMEOUT bash action.sh "$@" &

pid=$!

wait $pid
