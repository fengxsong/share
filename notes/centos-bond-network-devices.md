## CentOS多网卡绑定

`cd /etc/sysconfig/network-scripts`

`cat ifcfg-eth0 ifcfg-eth1`

    DEVICE=eth0
    TYPE=Ethernet
    ONBOOT=yes
    BOOTPROTO=none
    DEVICE=eth1
    TYPE=Ethernet
    ONBOOT=yes
    BOOTPROTO=none

`cat ifcfg-bond0`

    DEVICE=bond0
    TYPE=Ethernet
    ONBOOT=yes
    BOOTPROTO=none
    IPADDR=10.0.0.10
    PREFIX=24
    GATEWAY=10.0.0.1
    DNS1=8.8.8.8
    DEFROUTE=yes
    IPV4_FAILURE_FATAL=yes
    NAME=bond0
    BONDING_OPTS="MODE=0 MIIMON=1000"

`MODE=1`表示`fault-tolerance (active-backup)`,`MODE=0`表示`round robin`

    echo "alias bond0 bonding" >> /etc/modprobe.d/bond0.conf
    echo "ifenslave bond0 eth0 eth1" >> /etc/rc.local
    reboot

`cat /proc/net/bonding/bond0`查看状态。
