## redis-cluster

### install redis-server

    cwd=`pwd`
    wget http://download.redis.io/releases/redis-3.0.7.tar.gz
    tar xvf redis-3.0.7.tar.gz
    cd redis-3.0.7 && make && sudo make install

### copy `redis-trib.rb` to `$PATH`

    sudo cp src/redis-trib.rb /usr/local/bin/
    sudo `which gem` install redis

### 开始设置集群
#### 准备工作

    IPADDR=`hostname --ip-address`
    sudo mkdir -p /etc/redis/
    sudo mkdir -p /data/redis
    sudo cp $cwd/redis-3.0.7/redis.conf /etc/redis/7000.conf

    # sudo vim /etc/redis/7000.conf

    daemonize yes
    port 7000
    pidfile /data/redis/7000.pid
    dir /data/redis/7000/
    appendonly yes
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 15000

    for port in {7001..7005}; do sudo cp /etc/redis/{7000.conf,$port.conf} && sudo sed -i "s/7000/$port/g" /etc/redis/$port.conf; done

##### 7000,7001,7002关闭持久化

    #save 900 1
    #save 300 10
    #save 60 10000
    appendonly no

##### 开启所有端口服务

    sudo mkdir -p /data/redis/{7000..7005}
    for port in {7000..7005}; do sudo `which redis-server` /etc/redis/$port.conf; done

#### 设置集群

    redis-trib.rb create --replicas 1 $IPADDR:7000 $IPADDR:7001 $IPADDR:7002 $IPADDR:7003 $IPADDR:7004 $IPADDR:7005
    # 按提示输入"yes"
    [OK] All nodes agree about slots configuration.
    >>> Check for open slots...
    >>> Check slots coverage...
    [OK] All 16384 slots covered.
    # now check the cluster
    redis-trib.rb check 192.168.1.240:7000

### testing

    redis-cli -c -p 7000 -h $IPADDR
    192.168.1.240:7000> set 20160101 "Fri Jan  1 00:00:00 CST 2016"
    OK
    192.168.1.240:7000> set 20160102 "Sat Jan  2 00:00:00 CST 2016"
    -> Redirected to slot [13896] located at 192.168.1.240:7002
    OK
    192.168.1.240:7002> set 20160103 "Sat Jan  3 00:00:00 CST 2016"
    -> Redirected to slot [9833] located at 192.168.1.240:7001
    OK
    192.168.1.240:7001> get 20160102
    -> Redirected to slot [13896] located at 192.168.1.240:7000
    "Sat Jan  2 00:00:00 CST 2016"

如上可以看到所有数据是怎么存储
now we'll test the failover, let's stop one of the master node

    ps -fe | grep *:7000
    root     11267     1  0 10:35 ?        00:00:10 /usr/local/bin/redis-server *:7000 [cluster]
    kill -s 9 11267
    #check port 7000
    redis-trib.rb check $IPADDR:7000
    [ERR] Sorry, can't connect to node 192.168.1.240:7000
    #then check port 7001
    M: 587e4e1ae8cd5d41fb624722ac08ba6370fab9b1 192.168.1.240:7001
       slots:5461-10922 (5462 slots) master
       1 additional replica(s)
    M: c4dab37dad48585098ea3af9d8581ce7d0e73d6e 192.168.1.240:7003
       slots:0-5460 (5461 slots) master
       0 additional replica(s)
    S: f9d920af7dfd6dedbcfe3d10ca8cf2b676dfbaf1 192.168.1.240:7004
       slots: (0 slots) slave
       replicates 587e4e1ae8cd5d41fb624722ac08ba6370fab9b1
    M: fdfd0d3ff70d8031a584e6ee702e87c8806f2876 192.168.1.240:7002
       slots:10923-16383 (5461 slots) master
       1 additional replica(s)
    S: 3b976d3b7f13bb82c654448fe576ab0598f3078b 192.168.1.240:7005
       slots: (0 slots) slave
       replicates fdfd0d3ff70d8031a584e6ee702e87c8806f2876
    [OK] All nodes agree about slots configuration.
    >>> Check for open slots...
    >>> Check slots coverage...
    [OK] All 16384 slots covered.

now we found that node 7003 replaced node 7000 and became a master node, but it doesn't have any slave. `0 additional replica(s)`
we check some datas stored in before

    redis-cli -c -p 7003 -h $IPADDR
    192.168.1.240:7003> GET 20160101
    "Fri Jan  1 00:00:00 CST 2016"
    192.168.1.240:7003> SET 20160105 "Fri Jan  5 00:00:00 CST 2016"
    OK

或者

    rsync -avz /data/redis/7003/{appendonly.aof,dump.rdb} /data/redis/7000/

启动完成后会发现7000节点自动变成了7003的slave节点。因为7003开启了持久化，为了保证性能，关闭并重新启动7003节点，使7000重新成为master。

#### 添加新主节点7006

    sudo mkdir -p /data/redis/7006
    sudo cp 7000.conf 7006.conf
    sudo sed -i 's/7000/7006/g' 7006.conf
    sudo `which redis-server` /etc/redis/7006.conf
    redis-trib.rb add-node $IPADDR:7006 $IPADDR:7000
    redis-trib.rb check $IPADDR:7006
    # 7006成为一个master节点, but `slots: (0 slots) master`
    # 要使用它的话需要`reshard`
    redis-trib.rb reshard $IPADDR:7000
    # 16384/(the number of master nodes), eg.16384/4=4096, choose `all` means the other nodes are the source. after all thing been done
    redis-trib.rb check $IPADDR:7006
    M: 4fc3806eaa91775126ebd337e9d8403bbc30486f 192.168.1.240:7006
       slots:0-1364,5461-6826,10923-12287 (4096 slots) master
       0 additional replica(s)

#### 添加从节点(类似于`添加新节点7006`)

    # 自动选择了`7006`作为`master`节点。
    redis-trib.rb add-node --slave $IPADDR:7007 $IPADDR:7000
    # 指定master的ID。
    redis-trib.rb add-node --slave --master-id 4fc3806eaa91775126ebd337e9d8403bbc30486f $IPADDR:7007 $IPADDR:7000

#### 移除节点
##### 移除主节点
    redis-trib.rb del-node $IPADDR:7000 4fc3806eaa91775126ebd337e9d8403bbc30486f
    # 出错
    [ERR] Node 192.168.1.240:7000 is not empty! Reshard data away and try again.
    # 需`reshard`
    redis-trib.rb reshard $IPADDR:7000
    # 按提示需要移动多少slot,`slots:0-1364,5461-6826,10923-12287 (4096 slots) master`,所以输入`4096`
    # 移动到哪个node,输入其他主节点ID皆可
    # source node ID,即要删除的节点ID,再输入`done`,之后再次检查可以看到`7006`状态为`slots: (0 slots) master`
    # 再次删除
    redis-trib.rb del-node $IPADDR:7000 4fc3806eaa91775126ebd337e9d8403bbc30486f
    # 成功删除并且将它设置为移动到目标节点的从节点。

##### 移除从节点

    # 从节点不涉及到数据迁移所以可以直接删除
    redis-trib.rb del-node $IPADDR:7000 502a92e3cbda8dce25c3ccc16186a09a3861f9d7

## HA
### HAPROXY

    sudo yum -y install haproxy
    #vim /etc/haproxy/haproxy.cfg
    global
        log         127.0.0.1 local3

        chroot      /var/lib/haproxy
        pidfile     /var/run/haproxy.pid
        maxconn     65535
        user        haproxy
        group       haproxy
        daemon

        # turn on stats unix socket
        stats socket /var/lib/haproxy/stats

    defaults
        mode                    tcp
        log                     global
        retries                 3
        timeout connect         5s
        timeout client          30s
        timeout server          30s
        timeout check           10s
        maxconn                 65535

    #---------------------------------------------------------------------
    # main frontend which proxys to the backends
    #---------------------------------------------------------------------
    frontend http *:8888
        default_backend stats

    backend stats
        mode http
        stats enable
        stats uri /?stats
        stats refresh 3s
        stats show-legends
        stats hide-version

    frontend redis-cluster
        bind *:6666
        option tcplog
        default_backend redis-cluster

    backend redis-cluster
        mode tcp
        balance roundrobin
        option tcp-check

        tcp-check send PING\r\n
        tcp-check expect string +PONG
        # tcp-check send info\ replication\r\n
        # tcp-check expect string role:master

        server redis_6380 192.168.1.240:7000 maxconn 1024 check inter 1s
        server redis_6381 192.168.1.240:7001 maxconn 1024 check inter 1s
        server redis_6382 192.168.1.240:7002 maxconn 1024 check inter 1s
        server redis_6383 192.168.1.240:7003 maxconn 1024 check inter 1s
        server redis_6384 192.168.1.240:7004 maxconn 1024 check inter 1s
        server redis_6385 192.168.1.240:7005 maxconn 1024 check inter 1s

客户端仅需连接6666端口即可。

ps.[redis-py-cluster][1]

[1]: https://github.com/Grokzen/redis-py-cluster
