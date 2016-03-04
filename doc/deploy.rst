克隆代码; 安装常用库；安装python库，安转nginx，redis, supervisord
apt-get install supervisor

配置步骤：

修改debug为false.

it may be necessary to increase the number of open files per process (to avoid “Too many open files”-Error). To raise this limit (setting it to 50000 for example) you can use the ulimit command, modify /etc/security/limits.conf or setting minfds in your supervisord config.

修改步骤:
1.
sudo vi /etc/security/limits.conf
文件尾追加
* hard nofile 65535
* soft nofile 65535
2.
sudo vim /etc/pam.d/su
将 pam_limits.so 这一行注释去掉
重起系统
3.
vi /etc/profile
最后一行加上
ulimit -SHn 65535

vi /etc/nginx/nginx.conf
vi /etc/supervisor/supervisord.conf    # 加到最后
启动nginx:
sudo nginx
启动supervisord:
supervisord



另外应该用iptable屏蔽8000-8003端口。
1.允许本地所有端口：
-A INPUT -i lo -j ACCEPT
2.屏蔽外网访问8001～8002端口：
-A INPUT -p tcp  --dport 8001:8004 -j REJECT
