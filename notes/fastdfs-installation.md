### set up hostname

    10.0.0.93   tracker01
    10.0.0.94   storage01
    10.0.0.95   storage02   tracker02

### Synchronizing network time
### add system user `useradd www -s /sbin/nologin`
### mount device

    mkdir /u01
    fdisk /dev/sdb
    mkfs.xfs -i size=512 /dev/sdb1
    echo "/dev/sdb1 /u01 xfs defaults 1 2" >> /etc/fstab
    mount -a && mount

### install libfastcommon

    git clone https://github.com/happyfish100/libfastcommon.git
    cd libfastcommon && ./make.sh && ./make.sh install

### install fastdfs

    git clone https://github.com/happyfish100/fastdfs.git
    cd fastdfs && ./make.sh && ./make.sh install
    cp conf/{http.conf,mime.types} /etc/fdfs/

#### configure tracker01,tracker02

    cp /etc/fdfs/tracker.conf.sample /etc/fdfs/tracker.conf
    mkdir -p /u01/fastdfs/tracker
    chown -R www. /u01/fastdfs/tracker
    # Modify the configuration file `/etc/fdfs/storage.conf`
    base_path=/u01/fastdfs/tracker
    max_connections=1024
    run_by_group=www
    run_by_user=www

    http.server_port=80

    /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start
    # If there is an error, the error log will be recorded in the /u01/fastdfs/tracker/logs/trackerd.log

#### configure storage01,storage02(set up multiple tracker servers)

    cp /etc/fdfs/storage.conf.sample /etc/fdfs/storage.conf
    mkdir -p /u01/fastdfs/storage
    chown -R www. /u01/fastdfs/storage
    # Modify the configuration file `/etc/fdfs/storage.conf`
    bind_addr=10.0.0.94 #**Must be declared**
    base_path=/u01/fastdfs/storage
    max_connections=1024
    store_path_count=1
    store_path0=/u01/fastdfs/storage
    #store_path1=/home/yuqing/fastdfs2
    tracker_server=tracker01:22122
    tracker_server=tracker02:22122
    run_by_group=www
    run_by_user=www
    http.server_port=80

    /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start
    # If there is an error, the error log will be recorded in the /u01/fastdfs/storage/logs/storaged.log

#### ***monitor***

    /usr/bin/fdfs_monitor /etc/fdfs/storage.conf

#### test

    cp /etc/fdfs/client.conf.sample /etc/fdfs/client.conf
    ###
    base_path=/tmp/fdfs
    tracker_server=tracker01:22122
    tracker_server=tracker02:22122
    ###

    /usr/bin/fdfs_test /etc/fdfs/client.conf upload make.sh

### install nginx on storage01/02,nginx version [stable]

    git clone https://github.com/happyfish100/fastdfs-nginx-module.git
    # yum install pcre pcre-devel openssl openssl-devel gd gd-devel
    ./configure --prefix=/usr/local/nginx --with-http_ssl_module --with-http_realip_module --with-http_image_filter_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_stub_status_module --with-pcre --add-module=/root/ngx_cache_purge-2.3 --add-module=/root/fastdfs-nginx-module/src/
    make; make install

    #nginx.conf
    location /M00 {
        root /u01/fastdfs/storage/data;
        ngx_fastdfs_module;
    }

    ln -s /u01/fastdfs/storage/data /u01/fastdfs/storage/data/M00
    #Modify the configuration file /etc/fdfs/mod_fastdfs.conf

### nginx.conf on tracker01(or on webfrontend)

    log_format  proxy  '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent $request_time "$http_referer" '
                  '"$http_user_agent" "$http_x_forwarded_for"'
          '"$upstream_addr" "$upstream_status" "$upstream_response_time"';

    proxy_temp_path /tmp/proxy_temp;
    proxy_cache_path /tmp/proxy_cache levels=1:2 keys_zone=nginxcache:200m inactive=12h max_size=2g;
    upstream fdfs {
        server   10.0.0.94:80;
        server   10.0.0.95:80;
    }

    server {
        listen       80;
        server_name  api01.wlimg.com;

        access_log  logs/fastdfs.access.log  proxy;

        location /M00 {
            proxy_cache nginxcache;
        	proxy_cache_key $uri$is_args$args;
        	add_header	Nginx-Cache $upstream_cache_status;
        	include	proxy.conf;
        	proxy_cache_valid 200 304 301 302 8h;
        	expires	1d;
            proxy_pass http://fdfs;
        }
        location ~ /purge(/.*) {
            proxy_cache_purge  nginxcache $1$is_args$args;
        }
    }

if you wanna save file to the original file name,for example `a tar.gz` file,when you insert the record into database,url record which should be similar to  `'M00/00/00/wKgB9FY8vV2AOJefABDBhzgVUw4494.tar.gz?filename=real_file_name.tar.gz'`

[stable]: http://nginx.org/download/nginx-1.8.0.tar.gz
