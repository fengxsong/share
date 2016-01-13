#!/bin/bash
# __author__="fengxsong"

set_unlimit() {
    echo "*    soft    nofile    65535" >> /etc/security/limits.conf
    echo "*    hard    nofile    65535" >> /etc/security/limits.conf
    echo "*    soft    nproc    65535" >> /etc/security/limits.conf
    echo "*    hard    nproc    65535" >> /etc/security/limits.conf
}

cwd=`pwd`
procs=`grep processor /proc/cpuinfo | wc -l`
src=$cwd/src
ngx_openresty_version="1.9.7.1"
mariadb_version="10.1.10"
redis_version="3.0.6"
openresty_basedir=/usr/local/openresty
mysql_basedir=/usr/local/mysql
mysql_datadir=/data/mysql

[ ! -d "$src" ] && mkdir -p $src

upgrade() {
    rpm -Uvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
    yum update -y
    yum groupinstall -y Development Tools
    yum install -y lsof iptables-services unzip lrzsz wget cmake lua-devel expat-devel openssl-devel libevent-devel libaio-devel \
    libxml2-devel gd-devel libmcrypt-devel libcurl-devel bison-devel ncurses-devel vim python-devel dos2unix net-tools
}

disable_services() {
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
    systemctl disable firewalld.service
    systemctl disable iptables.service
}

check_exists() {
    [ -d "$1" -o -f "$1" ] && echo "$1 already exists!" && exit 1
}

openresty() {
    check_exists "$openresty_basedir"
    cd $src
    useradd -m -s /sbin/nologin www
    curl http://labs.frickle.com/files/ngx_cache_purge-2.3.tar.gz -o ngx_cache_purge-2.3.tar.gz
    tar xvf ngx_cache_purge-2.3.tar.gz
    curl https://openresty.org/download/ngx_openresty-$ngx_openresty_version.tar.gz -o ngx_openresty.tar.gz
    tar xvf ngx_openresty.tar.gz
    cd ngx_openresty-$ngx_openresty_version
    ./configure \
    --with-http_realip_module \
    --with-http_image_filter_module \
    --with-http_sub_module \
    --with-http_gzip_static_module \
    --with-http_auth_request_module \
    --with-http_stub_status_module \
    --with-pcre \
    --with-http_ssl_module \
    --add-module=../ngx_cache_purge-2.3
    gmake && gmake install
    cp $cwd/nginx.conf $openresty_basedir/nginx/conf/
    cp $cwd/nginx_init /etc/init.d/nginx
    chmod 755 !$
    mkdir -p $openresty_basedir/nginx/conf/site_enabled
}

mariadb() {
    check_exists "$mysql_basedir"
    cd $src
    useradd -m -s /sbin/nologin mysql
    wget http://mirrors.opencas.cn/mariadb//mariadb-$mariadb_version/source/mariadb-$mariadb_version.tar.gz
    tar xvf mariadb-$mariadb_version.tar.gz
    cd mariadb-$mariadb_version
    cmake . \
    -DCMAKE_INSTALL_PREFIX=$mysql_basedir \
    -DMYSQL_DATADIR=$mysql_datadir \
    -DDEFAULT_CHARSET=utf8 \
    -DDEFAULT_COLLATION=utf8_general_ci \
    -DEXTRA_CHARSETS=all \
    -DENABLED_LOCAL_INFILE=1
    make -j$procs && make install
    ln -s $mysql_basedir/lib/libmysqlclient.so.18.0.0 /usr/lib64/libmysqlclient.so.18
    $mysql_basedir/scripts/mysql_install_db --user=mysql --basedir=$mysql_basedir --datadir=$mysql_datadir
    rm -f /etc/my.cnf
    cp support-files/my-large.cnf $mysql_basedir/my.cnf
    cp support-files/mysql.server /etc/init.d/mysqld
}

redis() {
    check_exists `which redis-server`
    cd $src
    wget http://download.redis.io/releases/redis-$redis_version.tar.gz
    tar xvf redis-$redis_version.tar.gz
    cd redis-$redis_version
    make && make Install
    cp redis.conf /etc/redis/6379.conf
    cp $cwd/redis_init /etc/init.d/redis
}

case "$1" in
    1)
    set_unlimit
    upgrade
    disable_services
    ;;
    2)
    openresty
    ;;
    3)
    mariadb
    ;;
    4)
    redis
    ;;
    *)
    echo "Usage: `basename $0` {1|2|3|4}"
    echo "1 = set system unlimit, upgrade system and install dependency, disable some services"
    echo "2 = install openresty"
    echo "3 = install mariadb"
    echo "4 = install redis"
    exit 2
esac
