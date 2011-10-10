#!/bin/bash
#
# Bash script for starting and stopping pyxis.
#
# Usage:
# ./run.sh command
#  - command - one of start, stop, status
#
. ./comp.conf

export PYTHONPATH=`python ./build_python_path.py ./`:$PYTHONPATH

# Function for checking whether some component is running or not.
# It matches component process among other processes by {component_name}_match_string from comp.conf file.
# Takes a single argument - component name.
get_running () {
    item=$1
    matchstr=$(eval "echo \${$(echo ${item}_match_string)}")
    filename=$item.pid
    running=false
    pid=0
    if [ -e $filename ]
    then
        pid=$(eval "cat $filename")
        proc_details=$(eval "ps ax | grep -v grep | grep $pid | grep $matchstr")
        if [ "${#proc_details}" -gt 0 ]
        then
            running=true
        else
            rm $filename
            pid=0
        fi
    fi
    echo $pid
}

# Function that echoes to console whether some component is running or not.
# Takes a single argument - component name.
show_running () {
    running=`get_running $1`
    if [ $running -gt 0 ]
    then
        echo "$1 is running."
    else
        echo "$1 is not running."
    fi
}

# Function for starting components. It is uses {component_name}_start from comp.conf file for running components.
# Takes a single argument - component name.
start_process () {
    program=$1
    echo "Starting $program..."
    $(eval "echo \${$(echo ${program}_start)}") &
    echo $! > $program.pid
}

# Function for stopping components. It just kills components processes by PID.
# Takes a single argument - component name.
stop_process () {
    program=$1
    pid=`get_running $1`
    if [ $pid -gt 0 ]
    then
        echo "Stopping $program..."
        kill $pid
        rm $program.pid
    fi
}

# Applies some function for all components.
# Takes a single argument - function name.
for_each () {
    for server in "${servers[@]}"
    do
        $1 $server
    done
    for service in "${services[@]}"
    do
        $1 $service
    done
    for component in "${components[@]}"
    do
        $1 $component
    done
}

if [ $# -eq 0 ]
then
    echo "Usage:"
    echo "run.sh command"
    echo " - command - one of start, stop, status"
else
    case "$1" in
    start)
        for_each start_process
        ;;
    stop)
        for_each stop_process
        ;;
    status)
        for_each show_running
        ;;
    *)
        echo "Bad command"
        ;;
    esac
fi
