#!/usr/bin/env bash

md5_str=$1

for i in `seq 1 60`; do
    ssh_pid=`ps -ef | grep $md5_str | grep -v $0 | grep -v sshpass | grep -v grep | awk '{print $2}'`
    if [ "$ssh_pid" = "" ]; then
        sleep 0.5;
        continue;
    else
        today=`date '+%Y_%m_%d'`
        today_audit_dir="logs/audit/$today"
        if [ ! -d "$today_audit_dir" ]; then
            echo "dir not exist!"
            echo "tody dir: $today_audit_dir"
            mkdir -p $today_audit_dir
        fi;
        log_file="$today_audit_dir/$md5_str.log"
        echo "ssh_pid: $ssh_pid"
        echo "log_file: $log_file"
        echo 1111 | sudo -S /usr/bin/strace -ttt -p $ssh_pid -o $log_file
        break;
    fi;
done;
