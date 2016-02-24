 ### update/patch_versions

 #### 0. Backup

    su - git;cd $HOME/gitlab
    bundle exec rake gitlab:backup:create RAILS_ENV=production

#### 1. Stop server

    /etc/init.d/gitlab stop

#### 2. Get latest code for the stable branch

    git fetch --all
    git checkout -- Gemfile.lock db/schema.rb
    LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
    git checkout $LATEST_TAG -b $LATEST_TAG

#### 3. Update gitlab-shell to the corresponding version

    cd $HOME/gitlab-shell
    git fetch
    git checkout v`cat /home/git/gitlab/GITLAB_SHELL_VERSION` -b v`cat /home/git/gitlab/GITLAB_SHELL_VERSION`

#### 4. Install libs, migrations, etc.

    bundle install --without development test postgres --deployment
    bundle exec rake db:migrate RAILS_ENV=production
    bundle exec rake assets:clean RAILS_ENV=production
    bundle exec rake assets:precompile RAILS_ENV=production
    bundle exec rake cache:clear RAILS_ENV=production

#### 5. Start application

    /etc/init.d/gitlab start

#### 6. Check application status

    bundle exec rake gitlab:env:info RAILS_ENV=production
    bundle exec rake gitlab:check RAILS_ENV=production
