### full backup & restore

    db_user=root
    db_pass=p@55w0rd
    datadir=/data/mysql
    backup_dir=/data/backup
    conf_file=/usr/local/mysql/my.cnf
    [ -d $backup_dir ] || mkdir -p $backup_dir
    backup_today=$backup_dir/`date +%Y%m%d`
    opt_args="--user=$db_user --password=$db_pass"
    # backup
    innobackupex $opt_args --no-timestamp $backup_today
    # backup the list of databases
    innobackupex $opt_args --databases="test01 test02 test03" ......
    # prepare to restore
    innobackupex --apply-log $backup_today
    # restore
    service mysqld stop
    rm -rf $datadir/*
    innobackupex --defaults-file=$conf_file --copy-back $backup_today
    chown -R mysql. $datadir
    service mysqld start
---
### incremental backup

    # tomorrow
    innobackupex $opt_args --no-timestamp --incremental $backup_dir/`date +%Y%m%d` --incremental-basedir=$backup_dir/`date --date="-1 day" +%Y%m%d`

    # the day after tomorrow
    innobackupex $opt_args --no-timestamp --incremental $backup_dir/`date +%Y%m%d` --incremental-basedir=$backup_dir/`date --date="-1 day" +%Y%m%d`
    .
    .
    .

    # prepare full backup log file
    innobackupex --apply-log --redo-only $backup_dir/$full_backup
    # prepare incremental backup log file to full backup_dir
    innobackupex --apply-log --redo-only $backup_dir/$full_backup --incremental-dir=$backup_dir/$second_day
    innobackupex --apply-log --redo-only $backup_dir/$full_backup --incremental-dir=$backup_dir/$third_day
    # copy back data files
    innobackupex --defaults-file=$conf_file --copy-back $backup_dir/$full_backup

    chown -R mysql. $datadir
---
