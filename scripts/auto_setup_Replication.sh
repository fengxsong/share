#!/bin/bash

MYSQL_ENV_FILE="`pwd`/.mysql_env"
if [ -f $MYSQL_ENV_FILE ];then
    source $MYSQL_ENV_FILE
else
    echo "Please make sure `pwd`/.mysql_env exists!"
    exit
fi

MYSQL=`which mysql`
MYSQLADMIN=`which mysqladmin`
MYSQLDUMP=`which mysqldump`

#skip-name-resolve
slave_status=`$MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS -e "show slave status"`
if [ ${#slave_status} != 0 ];then
    $MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS -e "stop slave"
    $MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS -e "reset slave all"
    echo "stop and reset slave."
fi

for db in $DBS;do
    $MYSQLADMIN -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS drop -f $db
    $MYSQLADMIN -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS create $db
    # $MYSQLDUMP -h$MYSQL_MASTER_HOST -u$MYSQL_MASTER_USER -p$MYSQL_MASTER_PASS --opt $db | gzip > "$db"_`date +%F`.sql.zip
    # zcat "$db"_`date +%F`.sql.zip | $MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS $db
    # rm -f "$db"_`date +%F`.sql.zip && echo "restore $db complete."
    # or
    $MYSQLDUMP -h$MYSQL_MASTER_HOST -u$MYSQL_MASTER_USER -p$MYSQL_MASTER_PASS --opt $db | $MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS $db
done

master_log_file=`$MYSQL -h$MYSQL_MASTER_HOST -u$MYSQL_MASTER_USER -p$MYSQL_MASTER_PASS -e "show master status" | awk 'END{print $1}'`
read_master_log_pos=`$MYSQL -h$MYSQL_MASTER_HOST -u$MYSQL_MASTER_USER -p$MYSQL_MASTER_PASS -e "show master status" | awk 'END{print $2}'`

cmd="CHANGE MASTER TO MASTER_HOST='$MYSQL_MASTER_HOST', MASTER_PORT=3306, MASTER_USER='$MYSQL_REPL_USER', MASTER_PASSWORD='$MYSQL_REPL_PASS', \
    MASTER_LOG_FILE='$master_log_file', MASTER_LOG_POS=$read_master_log_pos"

$MYSQL -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS -e "$cmd"
$MYSQLADMIN -h$MYSQL_SLAVE_HOST -u$MYSQL_SLAVE_USER -p$MYSQL_SLAVE_PASS start-slave
