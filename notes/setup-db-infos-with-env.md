### setup fastcgi params($nginx/conf/fastcgi_params)

    fastcgi_param   DBUSER  dbuser;
    fastcgi_param   DBPASS  dbpass;
    fastcgi_param   DBHOST  localhost;
    fastcgi_param   DBPORT  3306;
    fastcgi_param   DBNAME  database_name;

### configure php.ini

    vim /usr/local/php/lib/php.ini
    variables_order = "EGPCS"

### reload nginx and php-fpm

### dblink configuration

    mysql://$_ENV['DBUSER']:$_ENV['DBPASS']@$_ENV['DBHOST']:$_ENV['DBPORT']/$_ENV['DBNAME']
