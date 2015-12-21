#!/usr/bin/env bash

tac access.log|head -n1000 >/tmp/xxxxx

start_time=`head -n1 /tmp/xxxxx |awk '{print $4}' |awk -F/ '{print $NF}' |cut -d: -f 2-`
end_time=`tac /tmp/xxxxx |head -n1 |awk '{print $4}' |awk -F/ '{print $NF}' |cut -d: -f 2-`

start_time=`date -d $start_time +%s`
end_time=`date -d $end_time +%s`

time_diff=$(($start_time-$end_time))

if [ $time_diff lt 60 ];then

    cat /tmp/xxxxx |egrep "css|js" |awk '{print $1}' |sort |uniq -c |sort -rn >/tmp/xxxstatic
    cat /tmp/xxxxx |egrep "php?" |awk '{print $1}' |sort |uniq -c |sort -rn >/tmp/xxxdym

    cat /tmp/xxxdym|while read line
    do
        times=`echo "$line"|awk '{print $1}'`
        if [ $times -gt 100 ];then
            ip=`echo "$line"|awk '{print $2}'`
            check_st=`grep "$ip" /tmp/xxxstatic|wc -l`
            if [ $check_st -eq 0 ];then
                iptables=`which iptables`
                $iptables -I INPUT -s $ip -j DROP
            fi;
        fi;
    done;
fi;