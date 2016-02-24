## REDIS持久化

目前REDIS持久化方式有两种，`RDB`和`AOF`
`RDB`是`snapshot`快照存储，是默认的持久化方式，通过配置文件中的`save`参数来定义快照周期。

    #   save <seconds> <changes>
    #   after 900 sec (15 min) if at least 1 key changed
    #   after 300 sec (5 min) if at least 10 keys changed
    #   after 60 sec if at least 10000 keys changed
    save 900    1
    save 300    10
    save 60 10000

RDB文件为`dbfilename dump.rdb`，路径通过`dir /your/path`设置。
当然也可手动执行`SAVE`|`BGSAVE`|`FLUSHALL`

`SAVE`时，Redis同步进行快照操作，期间阻塞所有来自客户端的请求。
`BGSAVE`该命令的快照是后台异步进行的，仍然能处理请求，可使用`LASTSAVE`查询最后一次成功执行快照的UNIX时间戳。
---
`AOF`(Append-Only File)比`RDB`方式有更好的持久性，使用`AOF`时，Redis会将每一个写命令通过`WRITE`函数追加到`appendfilename`里。

    appendonly yes
    appendfilename appendonly.aof
    appendfsync everysec

但这样会导致AOF文件越来越大，比如你`set myname a`->`set myname b`->`set myname c`，其实只需保存`set myname c`即可。为了压缩AOF持久化文件，Redis提供了`BGREWRITEAOF`或者以下配置项

    # that will prevent fsync() from being called in the main process while a
    # BGSAVE or BGREWRITEAOF is in progress.
    no-appendfsync-on-rewrite yes
    # This base size is compared to the current size. If the current size is
    # bigger than the specified percentage, the rewrite is triggered. Also
    # you need to specify a minimal size for the AOF file to be rewritten, this
    # is useful to avoid rewriting the AOF file even if the percentage increase
    # is reached but it is still pretty small.
    auto-aof-rewrite-percentage 100
    auto-aof-rewrite-min-size 64mb

## 主从灾难恢复
**master上关闭RDB和AOF，保证读写性能，slave上同时开启RDB和AOF持久化。**
#### 配置
master(10.0.0.3)

    port  7000
    #save 900 1
    #save 300 10
    #save 60 10000
    appendonly no

slave(10.0.0.4)

    port 7000
    save 900 1
    save 300 10
    save 60 10000
    slaveof 10.0.0.3 7000
    appendonly yes
    appendfilename appendonly.aof
    appendfsync everysec
    no-appendfsync-on-rewrite yes
    auto-aof-rewrite-percentage 100
    auto-aof-rewrite-min-size 64mb

#### 启动master和slave并模拟数据

    while(( $i < 8888 ));do redis-cli -p 7000 set _test_$i `echo "$i"|md5sum|awk '{print $1}'`;i=$(($i+1));done

查看master的`dir`目录中的`dump.rdb`并没有增大，slave上的RDB和AOF文件在增长，查看主从上的`key`值均为8887，现在杀掉master进程`ps aux|grep *:6379|awk '{print $2}'|xargs kill -s 9`，在slave上`info`查看`master_link_status:down`

#### 恢复
先关闭slave的同步`SLAVEOF NO ONE`
之后传输RDB文件和AOF文件到master的`dir`目录

    rsync -avz appendonly.aof dump.rdb fengxsong@10.0.0.2:/your/path

在master节点确认传输完成后重启启动redis-server，`info`查看keys已经恢复完成。
slave节点再次开启`SLAVEOF 10.0.0.3 7000`
