#!/bin/bash
. ./comp.conf

export PYTHONPATH=`python ~/work/pyxis/pyxis/build_python_path.py ~/work/pyxis/pyxis/`:$PYTHONPATH

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

show_running () {
    running=`get_running $1`
    if [ $running -gt 0 ]
    then
        echo "$1 is running."
    else
        echo "$1 is not running."
    fi
}

start_process () {
    program=$1
    echo "Starting $program..."
    $(eval "echo \${$(echo ${program}_start)}") &
    echo $! > $program.pid
}

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
    for_each show_running
else
    case "$1" in
    start)
        for_each start_process
        ;;
    stop)
        for_each stop_process
        ;;
    *)
        echo "Bad command"
        ;;
    esac
fi
exit
