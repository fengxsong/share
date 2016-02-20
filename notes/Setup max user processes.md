## `limit.conf`之`*  soft(hard)   nproc  65535`的坑

某天修改过`php-fpm`的`max_children`数之后，使用ansible管理时竟然出现

    {"dark": {"web01": {"msg": "Failed to open session: SSH session not active", "failed": true}}, "contacted": {}}

之后`ssh web01`时出现`Write failed: Broken pipe`，使用其他系统sudo用户登录上去后检查`/var/log/secure`有以下日志

    fatal: setresuid 501: Resource temporarily unavailable

google了下原来是用户达到最大进程数不能再创建了，修改`/etc/security/limit.conf`，添加以下

    www    soft    nproc    32768
    www    hard    nproc    65535

**原来`*  soft(hard)    nproc   65535`**对`www`用户没有生效~！！！

设置rlimit的正确姿势应该设置用户名。。
