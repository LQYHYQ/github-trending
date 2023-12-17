# github-trending
每天获取并保存Github Trending热榜数据。

## 配置
修改 `config.ini` 文件。
```config.ini
[pushplus]
token = xxxxxxxxxxxxxxx

[mysql]
host = xxx.xxx.xxx.xxx
user = xxx
password = xxx
```
`pushplus.token`: pushplus推送服务配置  
`mysql.host`: mysql地址  
`mysql.user`: mysql账号  
`mysql.password`: mysql密码  

## 使用
1. 按上面配置 `config.ini` 文件。
2. 安装依赖，`pip install -r requirement.txt`。  
3. MySQL数据库生成表，在MySQL执行文件夹内的 `github_trending_daily.sql`脚本文件。  
4. 执行main.py文件。  
