### Git

	wget -O git.zip https://github.com/git/git/archive/master.zip
	unzip git.zip
	cd git-master
	autoconf
	./configure --prefix=/usr/local/
	make && make install
	ln -s /usr/local/bin/git /usr/bin/git
	git --version

### Ruby

	wget http://cache.ruby-lang.org/pub/ruby/2.1/ruby-2.1.6.tar.gz
	tar xvf ruby-2.1.6.tar.gz
	cd ruby-2.1.6
	./configure --disable-install-rdoc
    make
    sudo make install

Change source to `ruby.taobao.org`:

    gem sources --remove https://rubygems.org/
    gem sources -a https://ruby.taobao.org/
    gem sources -l
    *** CURRENT SOURCES ***

    https://ruby.taobao.org/

If RAILS project using Gemfile,change the source:

    source "https://ruby.taobao.org/"

Install the Bundler Gem:

    gem install bundler --no-ri --no-rdoc

### Create a `git` user for GitLab:

	useradd git

### Run as `git` user

	git clone https://gitlab.com/gitlab-org/gitlab-ce.git -b 7-5-stable gitlab
	cd gitlab
	cp config/gitlab.yml.example config/gitlab.yml
	# editor config/gitlab.yml

	chown -R git log/
    chown -R git tmp/
    chmod -R u+rwX,go-w log/
    chmod -R u+rwX tmp/

	mkdir /home/git/gitlab-satellites
	chmod u+rwx,g=rx,o-rwx /home/git/gitlab-satellites
	chmod -R u+rwX tmp/pids/
    chmod -R u+rwX tmp/sockets/

	chmod -R u+rwX  public/uploads
	# Copy the example Unicorn config
    cp config/unicorn.rb.example config/unicorn.rb

	git config --global user.name "GitLab"
    git config --global user.email "example@example.com"
    git config --global core.autocrlf input

	cp config/resque.yml.example config/resque.yml
	# editor config/resque.yml

	cp config/database.yml.mysql config/database.yml
	# editor config/database.yml

	yum -y install libicu-devel

	bundle install --deployment --without development test postgres aws

#### Install GitLab Shell

	bundle exec rake gitlab:shell:install[v2.2.0] REDIS_URL=unix:/tmp/redis.sock RAILS_ENV=production

#### Initialize Database and Activate Advanced Features

    bundle exec rake gitlab:setup RAILS_ENV=production

### Install Init Scripts

	cp /home/git/gitlab/lib/support/init.d/gitlab /etc/init.d/gitlab
	chmod 755 !$
	chown git. !$

### Check Application Status

    bundle exec rake gitlab:env:info RAILS_ENV=production

### Compile Assets

    bundle exec rake assets:precompile RAILS_ENV=production

### Start Your GitLab Instance(Run as `git` user)

    /etc/init.d/gitlab restart

### SETUP STMP(edit the smtp_settings)

    cp config/initializers/smtp_settings.rb.sample config/initializers/smtp_settings.rb
    sudo vim !$

### Web Login

	root
    5iveL!fe

### Nginx

    cp lib/support/nginx/gitlab /usr/local/tengine/conf/gitlab.conf
	# edit the gitlab.conf

### something else.

	mv /usr/bin/ruby /usr/bin/ruby.old
	ln -s /usr/local/bin/ruby /usr/bin/ruby

	cp /usr/lib64/libz.so /usr/local/lib/
	cp /usr/local/lib/libz.a /usr/lib64/

### run check

    /home/git/gitlab-shell/bin/check
