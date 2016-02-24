
### Installation

	yum -y install expat expat-devel libtool

	mysql>INSTALL PLUGIN sphinx SONAME 'ha_sphinx.so';
	mysql>show engines;

	tar xvf coreseek-4.1-beta.tar.gz
	cd coreseek-4.1-beta/mmseg-3.2.14/
	./bootstrap
	./configure --prefix=/usr/local/mmseg
	make && make install

	cd ../csft-4.1
	sh buildconf.sh
	./configure --prefix=/usr/local/coreseek \
	--without-unixodbc --with-mmseg \
	--with-mmseg-includes=/usr/local/mmseg/include/mmseg/ \
	--with-mmseg-libs=/usr/local/mmseg/lib/ --with-mysql --with-python
	make && make install


#### Start searchd services

	/usr/local/coreseek/bin/searchd -c /data/wlwebdir/www/includes/sphinx/csft_mysql.conf

#### Stop searchd services

	/usr/local/coreseek/bin/searchd -c /data/wlwebdir/www/includes/sphinx/csft_mysql.conf --stop

#### update and reload coreseek

	/usr/local/coreseek/bin/indexer -c /data/wlwebdir/www/includes/sphinx/csft_mysql.conf --all --rotate
