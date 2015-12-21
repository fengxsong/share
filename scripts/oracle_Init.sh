#!/bin/bash
#安装所需依赖软件包
yum -y install compat-libstdc++-33 elfutils elfutils-libelf-devel gcc gcc-c++ glibc glibc-common glibc-devel glibc-headers ksh libaio libaio-devel libgcc libstdc++ libstdc++-devel make 
#修改系统打开文件句柄数
cat >>/etc/security/limits.conf<<EOF
oracle soft nproc 2047
oracle hard nproc 16384
oracle soft nofile 8192
oracle hard nofile 65536
EOF
#授权认证模块
cat >>/etc/pam.d/login<<EOF
session required /lib/security/pam_limits.so
session required pam_limits.so
EOF
#系统内核参数优化
cat >/etc/sysctl.conf<<EOF
net.ipv4.ip_forward = 0
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.default.accept_source_route = 0
kernel.sysrq = 0
kernel.core_uses_pid = 1
net.ipv4.tcp_syncookies = 1
# Disable netfilter on bridges.
#net.bridge.bridge-nf-call-ip6tables = 0
#net.bridge.bridge-nf-call-iptables = 0
#net.bridge.bridge-nf-call-arptables = 0
kernel.msgmnb = 65536
kernel.msgmax = 65536
kernel.shmmax = 68719476736
#kernel.shmall = 4294967296
fs.file-max = 6815744
fs.aio-max-nr = 1048576
kernel.shmall = 2097152
#kernel.shmmax = 2147483648
kernel.shmmni = 4096
kernel.sem = 250 32000 100 128
net.ipv4.ip_local_port_range = 9000 65500
net.ipv4.tcp_syncookies = 1
net.core.rmem_default = 4194304
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
EOF
#使以上的内核参数生效
/sbin/sysctl –p
#设置文件句柄数
cat >>/etc/profile<<EOF
if [ $USER = "oracle" ]; then
    if [ $SHELL = "/bin/bash" ]; then
        ulimit -p 16384
        ulimit -n 65536
    else
        ulimit -u 16384 -n 65536
    fi
fi
EOF
#添加用户，用户组并创建目录设置权限
groupadd oinstall
groupadd dba
groupadd oper
groupadd asmadmin
groupadd asmoper
groupadd asmdba
useradd -g oinstall -G dba,asmdba,oper -m oracle
useradd -g oinstall -G asmadmin,asmdba,asmoper,oper,dba grid
id oracle
id grid
mkdir -p /u01/app/oracle
mkdir -p /u01/app/oradata
mkdir -p /u01/app/oracle/product
chown -R oracle:oinstall /u01/app
#设置oracle用户环境变量
cat >>/home/oracle/.bash_profile<<EOF
umask 022
export ORACLE_BASE=/u01/app
export ORACLE_HOME=$ORACLE_BASE/oracle/product/11.2.0/dbhome_1
export ORACLE_SID=orcl
export ORACLE_UNQNAME=$ORACLE_SID
export PATH=\$PATH:\$HOME/bin:\$ORACLE_HOME/bin
export LD_LIBRARY_PATH=\$ORACLE_HOME/lib:/usr/lib
EOF

echo "Oracle Setup Init Finished."
echo "now 'su - oracle' and run './runInstaller'"
echo "After finish install oracle,run dbca to configure a new sid."
echo "run 'netca' to configure listener lsnctrl"
#在database/response下复制修改db_install.rsp响应文件
#./runInstaller -silent -ignoreSysPrereqs -force -ignorePrereq -responseFile db_install.rsp#使用响应文件静默安装
