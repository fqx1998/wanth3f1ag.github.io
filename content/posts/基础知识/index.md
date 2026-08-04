---
title: "基础知识"
date: 2024-12-13T15:16:45+08:00
summary: "放点基础知识"
url: "/posts/基础知识/"
categories:
  - "前置知识"
tags:
  - "基础知识"
draft: true
---

# 基础知识积累

## PHP九大全局变量

- $_POST [用于接收post提交的数据]
- $_GET [用于获取url地址栏的参数数据]
- $_FILES [用于文件就收的处理img 最常见]
- $_COOKIE [用于获取与setCookie()中的name 值]
- $_SESSION [用于存储session的值或获取session中的值]
- $_REQUEST [具有get,post的功能，但比较慢]
- SERVER[是预定义服务器变量的一种，所有SERVER[是预定义服务器变量的一种，所有_SERVER [是预定义服务器变量的一种，所有_SERVER开头的都
- $GLOBALS [一个包含了全部变量的全局组合数组]
- $_ENV [ 是一个包含服务器端环境变量的数组。它是PHP中一个超级全局变量，我们可以在PHP 程序的任何地方直接访问它]

## ASCII 设备控制字符

ASCII 控制字符（00-31，加上 127）最初被设计用来控制诸如打印机和磁带驱动器之类的硬件设备。

控制字符（除了水平制表符、换行、回车之外）在 HTML 文档中不起任何作用。

| 字符 | 编号 | 描述                                       |
| :--- | :--- | :----------------------------------------- |
| NUL  | 00   | 空字符（null character）                   |
| SOH  | 01   | 标题开始（start of header）                |
| STX  | 02   | 正文开始（start of text）                  |
| ETX  | 03   | 正文结束（end of text）                    |
| EOT  | 04   | 传输结束（end of transmission）            |
| ENQ  | 05   | 请求（enquiry）                            |
| ACK  | 06   | 收到通知/响应（acknowledge）               |
| BEL  | 07   | 响铃（bell）                               |
| BS   | 08   | 退格（backspace）                          |
| HT   | 09   | 水平制表符（horizontal tab）               |
| LF   | 10   | 换行（line feed）                          |
| VT   | 11   | 垂直制表符（vertical tab）                 |
| FF   | 12   | 换页（form feed）                          |
| CR   | 13   | 回车（carriage return）                    |
| SO   | 14   | 不用切换（shift out）                      |
| SI   | 15   | 启用切换（shift in）                       |
| DLE  | 16   | 数据链路转义（data link escape）           |
| DC1  | 17   | 设备控制 1（device control 1）             |
| DC2  | 18   | 设备控制 2（device control 2）             |
| DC3  | 19   | 设备控制 3（device control 3）             |
| DC4  | 20   | 设备控制 4（device control 4）             |
| NAK  | 21   | 拒绝接收/无响应（negative acknowledge）    |
| SYN  | 22   | 同步空闲（synchronize）                    |
| ETB  | 23   | 传输块结束（end transmission block）       |
| CAN  | 24   | 取消（cancel）                             |
| EM   | 25   | 已到介质末端/介质存储已满（end of medium） |
| SUB  | 26   | 替补/替换（substitute）                    |
| ESC  | 27   | 溢出/逃离/取消（escape）                   |
| FS   | 28   | 文件分隔符（file separator）               |
| GS   | 29   | 组分隔符（group separator）                |
| RS   | 30   | 记录分隔符（record separator）             |
| US   | 31   | 单元分隔符（unit separator）               |
|      |      |                                            |
| DEL  | 127  | 删除（delete）                             |

## ASCII 可打印的字符

| 字符 | 编号 | 描述                             |
| :--- | :--- | :------------------------------- |
|      | 32   | 空格（space）                    |
| !    | 33   | 感叹号（exclamation mark）       |
| "    | 34   | 引号（quotation mark）           |
| #    | 35   | 数字符号（number sign）          |
| $    | 36   | 美元符号（dollar sign）          |
| %    | 37   | 百分比符号（percent sign）       |
| &    | 38   | & 符号（ampersand）              |
| '    | 39   | 撇号（apostrophe）               |
| (    | 40   | 左括号（left parenthesis）       |
| )    | 41   | 右括号（right parenthesis）      |
| *    | 42   | 星号（asterisk）                 |
| +    | 43   | 加号（plus sign）                |
| ,    | 44   | 逗号（comma）                    |
| -    | 45   | 连字符（hyphen）                 |
| .    | 46   | 句号（period）                   |
| /    | 47   | 斜线（slash）                    |
| 0    | 48   | 数字 0                           |
| 1    | 49   | 数字 1                           |
| 2    | 50   | 数字 2                           |
| 3    | 51   | 数字 3                           |
| 4    | 52   | 数字 4                           |
| 5    | 53   | 数字 5                           |
| 6    | 54   | 数字 6                           |
| 7    | 55   | 数字 7                           |
| 8    | 56   | 数字 8                           |
| 9    | 57   | 数字 9                           |
| :    | 58   | 冒号（colon）                    |
| ;    | 59   | 分号（semicolon）                |
| <    | 60   | 小于号（less-than）              |
| =    | 61   | 等于号（equals-to）              |
| >    | 62   | 大于号（greater-than）           |
| ?    | 63   | 问号（question mark）            |
| @    | 64   | @ 符号（at sign）                |
| A    | 65   | 大写字母 A                       |
| B    | 66   | 大写字母 B                       |
| C    | 67   | 大写字母 C                       |
| D    | 68   | 大写字母 D                       |
| E    | 69   | 大写字母 E                       |
| F    | 70   | 大写字母 F                       |
| G    | 71   | 大写字母 G                       |
| H    | 72   | 大写字母 H                       |
| I    | 73   | 大写字母 I                       |
| J    | 74   | 大写字母 J                       |
| K    | 75   | 大写字母 K                       |
| L    | 76   | 大写字母 L                       |
| M    | 77   | 大写字母 M                       |
| N    | 78   | 大写字母 N                       |
| O    | 79   | 大写字母 O                       |
| P    | 80   | 大写字母 P                       |
| Q    | 81   | 大写字母 Q                       |
| R    | 82   | 大写字母 R                       |
| S    | 83   | 大写字母 S                       |
| T    | 84   | 大写字母 T                       |
| U    | 85   | 大写字母 U                       |
| V    | 86   | 大写字母 V                       |
| W    | 87   | 大写字母 W                       |
| X    | 88   | 大写字母 X                       |
| Y    | 89   | 大写字母 Y                       |
| Z    | 90   | 大写字母 Z                       |
| [    | 91   | 左方括号（left square bracket）  |
| \    | 92   | 反斜线（backslash）              |
| ]    | 93   | 右方括号（right square bracket） |
| ^    | 94   | 插入符号（caret）                |
| _    | 95   | 下划线（underscore）             |
| `    | 96   | 重音符（grave accent）           |
| a    | 97   | 小写字母 a                       |
| b    | 98   | 小写字母 b                       |
| c    | 99   | 小写字母 c                       |
| d    | 100  | 小写字母 d                       |
| e    | 101  | 小写字母 e                       |
| f    | 102  | 小写字母 f                       |
| g    | 103  | 小写字母 g                       |
| h    | 104  | 小写字母 h                       |
| i    | 105  | 小写字母 i                       |
| j    | 106  | 小写字母 j                       |
| k    | 107  | 小写字母 k                       |
| l    | 108  | 小写字母 l                       |
| m    | 109  | 小写字母 m                       |
| n    | 110  | 小写字母 n                       |
| o    | 111  | 小写字母 o                       |
| p    | 112  | 小写字母 p                       |
| q    | 113  | 小写字母 q                       |
| r    | 114  | 小写字母 r                       |
| s    | 115  | 小写字母 s                       |
| t    | 116  | 小写字母 t                       |
| u    | 117  | 小写字母 u                       |
| v    | 118  | 小写字母 v                       |
| w    | 119  | 小写字母 w                       |
| x    | 120  | 小写字母 x                       |
| y    | 121  | 小写字母 y                       |
| z    | 122  | 小写字母 z                       |
| {    | 123  | 左花括号（left curly brace）     |
| \|   | 124  | 竖线（vertical bar）             |
| }    | 125  | 右花括号（right curly brace）    |
| ~    | 126  | 波浪线（tilde）                  |

## HTTP协议

### HTTP协议分类

- HTTP1.0

对应服务器端口：80

**特点**：

1. 支持 GET、POST、HEAD 方法。
2. 引入了头部（Headers）、状态码（Status Codes）和内容类型（Content-Type）。
3. 每个请求需要建立一个新的 TCP 连接（无连接）。

- HTTP1.1

对应服务器端口：80

**特点**：

1. 支持持久连接（Keep-Alive），减少 TCP 连接的开销。
2. 引入了管道化（Pipelining），允许在同一个连接上发送多个请求。
3. 新增了 PUT、DELETE、OPTIONS、TRACE 等方法。
4. 支持分块传输编码（Chunked Transfer Encoding）。

但是对于HTTP协议来说，存在着安全隐患，HTTP是明文传输，数据容易被窃听或篡改。这时候另一种协议就会更安全

- HTTPS

对应服务器端口：443

**特点**：

1. 基于 TLS/SSL 加密传输，数据安全。

### HTTP请求方法

HTTP（超文本传输协议）是一种应用层协议，主要用于客户端和服务器之间的通信。HTTP定义了一些方法（又称为请求方法），用于指示客户端希望对服务器资源执行的操作。以下是一些常见的HTTP方法及其用途：

1. GET

- **用途**：请求指定资源的表示（通常是网页或文件）。
- 特点
  - 数据通过URL传递，适合获取数据。
  - 不会对服务器上的资源产生副作用，即是安全的（safe）和幂等的（idempotent）。

2. POST

- **用途**：向指定资源提交数据（例如表单数据），通常用于创建新的资源。
- 特点
  - 数据包含在请求体中。
  - 可能会对服务器上的资源产生副作用，不同的请求可能会产生不同的结果。

3. PUT

- **用途**：更新指定资源。如果资源不存在，则可以创建它。
- 特点
  - 数据包含在请求体中。
  - 是幂等的，即多次请求结果相同。

4. DELETE

- **用途**：删除指定资源。
- 特点
  - 请求体通常为空。
  - 是幂等的，重复请求同一资源的删除不会产生额外效果。

5. HEAD

- **用途**：获取指定资源的响应头，而不获取实际的资源内容。
- 特点
  - 常用于检查资源是否存在或获取资源的元信息。
  - 不会对服务器上的资源产生副作用。

6. OPTIONS

- **用途**：描述目标资源的通信选项，通常用于跨域请求。
- 特点
  - 返回允许的HTTP方法和其他相关信息。

7. PATCH

- **用途**：对指定资源进行部分更新。
- 特点
  - 数据包含在请求体中，可以只修改资源的部分属性。
  - 是非幂等的，具体结果取决于请求内容。

8. TRACE

- **用途**：用于诊断，回显服务器收到的请求信息。
- 特点
  - 主要用于调试目的。

9. CONNECT

- **用途**：建立一个到服务器的隧道，通常用于HTTPS请求。
- 特点
  - 通常在代理服务器中使用，允许客户端与目标服务器进行安全通信。

### URL统一资源定位符

组成结构

```
协议://主机名[:端口]/路径[?查询参数][#片段]
```

参数介绍

- 协议:指定访问资源所用的协议，常见的协议包括：

`http`：超文本传输协议（未加密）。

`https`：安全的超文本传输协议（加密）。

`ftp`：文件传输协议。

`mailto`：电子邮件地址。

`file`：本地文件。

- 主机名：指定资源所在的主机（服务器）的名称或 IP 地址。

- 端口：指定访问资源的端口号（可选）。如果未指定端口则默认http的80端口或者https的443端口

- 路径：指定资源在服务器上的路径
- 查询参数：用于向服务器传递的额外参数(可选)，以`?`开头，每个参数之间用`&`分隔
- 片段：用于指定资源中的某个部分（如页面中的锚点）（可选）。以`#`开头

一个完整的URL示例

```
http://www.example.com:8080/path/to/resource?key1=1&key2=2#section1
```

### url编码

**URL 编码的基本规则**

- **保留字符**：某些字符在 URL 中有特殊含义（如 `?`, `=`, `&`, `/`, `#` 等），称为保留字符。这些字符在特定位置不需要编码，但在其他位置需要编码。
- **非保留字符**：字母（`a-z`, `A-Z`）、数字（`0-9`）以及 `-`, `_`, `.`, `~` 等字符不需要编码。
- **其他字符**：所有其他字符（如空格、中文、特殊符号等）都需要编码。

**编码规则**

URL 编码使用 `%` 后跟两个十六进制数字表示字符的 ASCII 码。例如：

- 空格（ASCII 码为 32，十六进制为 20）编码为 `%20`。
- 中文字符 `中` 的 UTF-8 编码为 `E4 B8 AD`，因此 URL 编码为 `%E4%B8%AD`。

| **字符** | **描述** | **URL 编码** |
| ------ | ------ | ---------- |
| 空格     | 空格符    | `%20`      |
| !      | 感叹号    | `%21`      |
| "      | 双引号    | `%22`      |
| #      | 井号     | `%23`      |
| $      | 美元符号   | `%24`      |
| %      | 百分号    | `%25`      |
| &      | 与号     | `%26`      |
| '      | 单引号    | `%27`      |
| (      | 左括号    | `%28`      |
| )      | 右括号    | `%29`      |
| *      | 星号     | `%2A`      |
| +      | 加号     | `%2B`      |
| ,      | 逗号     | `%2C`      |
| /      | 斜杠     | `%2F`      |
| :      | 冒号     | `%3A`      |
| ;      | 分号     | `%3B`      |
| =      | 等号     | `%3D`      |
| ?      | 问号     | `%3F`      |
| @      | At 符号  | `%40`      |
| [      | 左方括号   | `%5B`      |
| ]      | 右方括号   | `%5D`      |

### 请求头介绍

**请求头（Request Headers）** 是 HTTP 请求的一部分，用于向服务器传递额外的信息。它们以键值对的形式存在，提供了关于客户端、请求内容、缓存策略等方面的详细信息。

请求头的存在有助于客户端与服务器之间的有效通信。通过请求头，客户端可以告诉服务器许多关于自己的信息，如浏览器类型、操作系统、所支持的内容格式等。这使得服务器能够根据这些信息，生成针对性的、优化的响应。

组成格式

一个标头包括它的名称（不区分大小写），一个冒号（`:`），可选且会被忽略的空格，最后是它的值（例如 `Allow: POST`）。

常用请求头大全

### **HTTP 请求头大全**

| **分类**     | **请求头**                     | **说明**                                       | **示例**                                                          |
| :--------- | :-------------------------- | :------------------------------------------- | :-------------------------------------------------------------- |
| **通用请求头**  | `Host`                      | 指定服务器的域名和端口号。                                | `Host: example.com`                                             |
|            | `User-Agent`                | 标识客户端（如浏览器、爬虫）的类型和版本。                        | `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)`         |
|            | `Accept`                    | 指定客户端希望接收的内容类型（MIME 类型）。                     | `Accept: text/html,application/xhtml+xml`                       |
|            | `Accept-Language`           | 指定客户端希望接收的语言。                                | `Accept-Language: en-US,en;q=0.9`                               |
|            | `Accept-Encoding`           | 指定客户端希望接收的内容编码（如压缩格式）。                       | `Accept-Encoding: gzip, deflate, br`                            |
|            | `Connection`                | 控制连接的行为，如是否保持连接。                             | `Connection: keep-alive`                                        |
|            | `Cache-Control`             | 指定缓存策略。                                      | `Cache-Control: no-cache`                                       |
|            | `Pragma`                    | 用于向后兼容 HTTP/1.0 的缓存控制。                       | `Pragma: no-cache`                                              |
|            | `Upgrade-Insecure-Requests` | 指示客户端希望将不安全的 HTTP 请求升级为 HTTPS。               | `Upgrade-Insecure-Requests: 1`                                  |
|            | **`Via`**                   | **用于记录请求或响应经过的代理服务器（正向代理/反向代理、网关、缓存等）路径信息**。 | `Via: ymzx.qq.com`                                              |
| **请求内容相关** | `Content-Type`              | 指定请求体的内容类型（MIME 类型）。                         | `Content-Type: application/json`                                |
|            | `Content-Length`            | 指定请求体的长度（字节数）。                               | `Content-Length: 348`                                           |
|            | `Content-Encoding`          | 指定请求体的编码方式（如压缩格式）。                           | `Content-Encoding: gzip`                                        |
|            | `Content-Language`          | 指定请求体的语言。                                    | `Content-Language: en-US`                                       |
|            | `Content-Location`          | 指定请求体的位置。                                    | `Content-Location: /path/to/resource`                           |
|            | `Content-Range`             | 指定请求体的范围（用于分块传输）。                            | `Content-Range: bytes 0-499/1234`                               |
| **身份验证相关** | `Authorization`             | 传递身份验证信息（如 Bearer Token、Basic Auth）。         | `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
|            | `Cookie`                    | 传递客户端的 Cookie 信息。                            | `Cookie: sessionId=abc123; username=john`                       |
|            | `Proxy-Authorization`       | 用于代理服务器的身份验证。                                | `Proxy-Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l`           |
| **条件请求相关** | `If-Modified-Since`         | 指定资源的最后修改时间，用于条件请求。                          | `If-Modified-Since: Mon, 10 Oct 2022 12:00:00 GMT`              |
|            | `If-None-Match`             | 指定资源的 ETag，用于条件请求。                           | `If-None-Match: "abc123"`                                       |
|            | `If-Unmodified-Since`       | 指定资源的最后修改时间，用于条件请求。                          | `If-Unmodified-Since: Mon, 10 Oct 2022 12:00:00 GMT`            |
|            | `If-Match`                  | 指定资源的 ETag，用于条件请求。                           | `If-Match: "abc123"`                                            |
|            | `If-Range`                  | 指定资源的 ETag 或最后修改时间，用于范围请求。                   | `If-Range: "abc123"`                                            |
| **其他请求头**  | `Referer`                   | 指定请求的来源页面。                                   | `Referer: https://example.com/page`                             |
|            | `Origin`                    | 指定请求的来源（用于跨域请求）。                             | `Origin: https://example.com`                                   |
|            | `X-Requested-With`          | 标识请求是通过 AJAX 发送的。                            | `X-Requested-With: XMLHttpRequest`                              |
|            | `DNT` (Do Not Track)        | 指示客户端是否启用“不跟踪”功能。                            | `DNT: 1`                                                        |
|            | `TE` (Transfer-Encoding)    | 指定客户端希望接收的传输编码。                              | `TE: trailers, deflate`                                         |
| **自定义请求头** | `X-Forwarded-For`           | 标识客户端的原始 IP 地址（用于代理服务器）。                     | `X-Forwarded-For: 192.168.1.1`                                  |
|            | `X-Forwarded-Proto`         | 标识客户端的原始协议（如 HTTP 或 HTTPS）。                  | `X-Forwarded-Proto: https`                                      |
|            | `X-Real-IP`                 | 标识客户端的真实 IP 地址。                              | `X-Real-IP: 192.168.1.1`                                        |
|            | `X-Custom-Header`           | 自定义请求头，用于传递额外的信息。                            | `X-Custom-Header: value`                                        |
|            | **`Client-IP`**             | 直接标明代理提取的真实客户端 IP                            | `Client-IP: 1.2.3.4`                                            |

### HTTP响应码大全

HTTP 响应码（HTTP Status Codes）是服务器对客户端请求的响应状态的三位数字代码。它们分为五类，分别表示不同的响应类型。

### **HTTP 响应码大全**

| **分类**         | **响应码** | **名称**                                   | **说明**                      |
| :------------- | :------ | :--------------------------------------- | :-------------------------- |
| **1xx: 信息响应**  | 100     | Continue（继续）                             | 客户端应继续发送请求的剩余部分。            |
|                | 101     | Switching Protocols（切换协议）                | 服务器已理解客户端的请求，并将切换到指定的协议。    |
|                | 102     | Processing（处理中）                          | 服务器已收到请求，但尚未完成处理。           |
|                | 103     | Early Hints（早期提示）                        | 服务器返回部分响应头，提示客户端提前加载资源。     |
| **2xx: 成功响应**  | 200     | OK（成功）                                   | 请求已成功处理。                    |
|                | 201     | Created（已创建）                             | 请求已成功处理，并创建了新资源。            |
|                | 202     | Accepted（已接受）                            | 请求已接受，但尚未处理完成。              |
|                | 203     | Non-Authoritative Information（非权威信息）     | 请求成功，但返回的元信息来自缓存或第三方。       |
|                | 204     | No Content（无内容）                          | 请求成功，但响应中没有内容。              |
|                | 205     | Reset Content（重置内容）                      | 请求成功，客户端应重置文档视图。            |
|                | 206     | Partial Content（部分内容）                    | 服务器成功处理了部分 GET 请求。          |
|                | 207     | Multi-Status（多状态）                        | 返回多个状态码，通常用于 WebDAV。        |
|                | 208     | Already Reported（已报告）                    | 资源的状态已在前面的响应中报告。            |
|                | 226     | IM Used（IM 已使用）                          | 服务器已完成对资源的操作，并返回结果。         |
| **3xx: 重定向响应** | 300     | Multiple Choices（多种选择）                   | 请求的资源有多个选择，客户端应选择其中一个。      |
|                | 301     | Moved Permanently（永久重定向）                 | 请求的资源已永久移动到新位置。             |
|                | 302     | Found（临时重定向）                             | 请求的资源临时移动到新位置。              |
|                | 303     | See Other（查看其他位置）                        | 客户端应使用 GET 方法访问新位置。         |
|                | 304     | Not Modified（未修改）                        | 资源未修改，客户端可使用缓存版本。           |
|                | 305     | Use Proxy（使用代理）                          | 请求的资源必须通过代理访问。              |
|                | 307     | Temporary Redirect（临时重定向）                | 请求的资源临时移动到新位置，客户端应保持原请求方法。  |
|                | 308     | Permanent Redirect（永久重定向）                | 请求的资源已永久移动到新位置，客户端应保持原请求方法。 |
| **4xx: 客户端错误** | 400     | Bad Request（错误请求）                        | 请求无效，服务器无法理解。               |
|                | 401     | Unauthorized（未授权）                        | 请求需要身份验证。                   |
|                | 402     | Payment Required（需要付款）                   | 保留状态码，通常用于支付系统。             |
|                | 403     | Forbidden（禁止访问）                          | 服务器拒绝请求。                    |
|                | 404     | Not Found（未找到）                           | 请求的资源不存在。                   |
|                | 405     | Method Not Allowed（方法不允许）                | 请求的方法不被允许。                  |
|                | 406     | Not Acceptable（不可接受）                     | 服务器无法生成客户端可接受的响应。           |
|                | 407     | Proxy Authentication Required（需要代理认证）    | 客户端需要通过代理进行身份验证。            |
|                | 408     | Request Timeout（请求超时）                    | 请求超时，服务器未收到完整请求。            |
|                | 409     | Conflict（冲突）                             | 请求与服务器的当前状态冲突。              |
|                | 410     | Gone（已删除）                                | 请求的资源已永久删除。                 |
|                | 411     | Length Required（需要长度）                    | 请求需要指定 `Content-Length` 头。  |
|                | 412     | Precondition Failed（前提条件失败）              | 请求的前提条件不满足。                 |
|                | 413     | Payload Too Large（负载过大）                  | 请求的负载超过服务器限制。               |
|                | 414     | URI Too Long（URI 过长）                     | 请求的 URI 过长，服务器无法处理。         |
|                | 415     | Unsupported Media Type（不支持的媒体类型）         | 请求的媒体类型不被支持。                |
|                | 416     | Range Not Satisfiable（范围无效）              | 请求的范围无效。                    |
|                | 417     | Expectation Failed（期望失败）                 | 请求的 `Expect` 头无法满足。         |
|                | 418     | I'm a teapot（我是茶壶）                       | 幽默响应码，表示服务器是茶壶。             |
|                | 421     | Misdirected Request（错误定向请求）              | 请求被错误定向到无法处理它的服务器。          |
|                | 422     | Unprocessable Entity（无法处理的实体）            | 请求格式正确，但语义错误。               |
|                | 423     | Locked（已锁定）                              | 请求的资源被锁定。                   |
|                | 424     | Failed Dependency（依赖失败）                  | 请求依赖于另一个请求，但该请求失败。          |
|                | 425     | Too Early（过早）                            | 服务器拒绝处理可能被重放的请求。            |
|                | 426     | Upgrade Required（需要升级）                   | 客户端需要升级协议。                  |
|                | 428     | Precondition Required（需要前提条件）            | 请求需要包含前提条件。                 |
|                | 429     | Too Many Requests（请求过多）                  | 客户端发送了过多请求。                 |
|                | 431     | Request Header Fields Too Large（请求头字段过大） | 请求头字段过大，服务器无法处理。            |
|                | 451     | Unavailable For Legal Reasons（因法律原因不可用）  | 请求的资源因法律原因不可用。              |
| **5xx: 服务器错误** | 500     | Internal Server Error（服务器内部错误）           | 服务器遇到意外错误，无法完成请求。           |
|                | 501     | Not Implemented（未实现）                     | 服务器不支持请求的功能。                |
|                | 502     | Bad Gateway（错误网关）                        | 服务器作为网关或代理时，从上游服务器收到无效响应。   |
|                | 503     | Service Unavailable（服务不可用）               | 服务器暂时无法处理请求（通常由于过载或维护）。     |
|                | 504     | Gateway Timeout（网关超时）                    | 服务器作为网关或代理时，未及时从上游服务器收到响应。  |
|                | 505     | HTTP Version Not Supported（HTTP 版本不支持）   | 服务器不支持请求的 HTTP 版本。          |
|                | 506     | Variant Also Negotiates（变体协商）            | 服务器内部配置错误。                  |
|                | 507     | Insufficient Storage（存储不足）               | 服务器无法存储完成请求所需的内容。           |
|                | 508     | Loop Detected（检测到循环）                     | 服务器检测到无限循环。                 |
|                | 510     | Not Extended（未扩展）                        | 请求需要进一步扩展。                  |
|                | 511     | Network Authentication Required（需要网络认证）  | 客户端需要通过网络进行身份验证。            |

### Python发送http请求

```py
#HTTP请求的学习
import requests

url = "https://www.baidu.com"
#GET请求
r = requests.get(url = url)#无参数GET请求
#r = requests.get(url = url,params = {'username':'admin','password':'admin123456'})#有参数GET请求

print("-----------分割线-------------")

#POST请求

r = requests.post(url = url)#无参数POST请求
data = {
    'username' : 'admin',
    'password' : 'admin123456'
}
r = requests.post(url = url , data = data)#有参数POST请求

print("-----------分割线-------------")

#自定义请求头

#headers请求头自定义

headers = {
    "User_Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
r = requests.post(url = url, headers = headers)#自定义请求头发送请求
```

### Python获取http信息

```py
import requests

#获取HTTP响应

url = "https://www.baidu.com"
r = requests.get(url=url)
#获取响应码
print(r.status_code)

#获取响应文本
print(r.text)#text文本，返回的是页面的字符串信息，r.text 会自动将响应内容解码为字符串。
print("-------------------------------------------------------")
print(r.content)#content文本，返回的是原始的字节数据

#将字节数据转化成指定编码

print(r.content.decode('utf-8'))#可以看到这里编码后就和r.text一样了

#获取响应头
print("-------------------------------------------------------")
print(r.headers)


#获取请求头
print("-------------------------------------------------------")
print(r.request.headers)


#获取请求url
print("-------------------------------------------------------")
print(r.url)


#获取cookie
print("-------------------------------------------------------")
print(r.cookies)
```

Python获取页面Cookie

```py
#获取网页的会话session
import requests

url = "https://www.baidu.com"

s = requests.Session()
r = s.get(url)
print(r.cookies)
print("----------------------------------------------------------------------------------------")
print(r.request.headers)
#第一次请求的时候返回对应的cookie值，后面的请求中则会自动携带cookie
r = s.get(url)
print("----------------------------------------------------------------------------------------")
print(r.request.headers)
#<RequestsCookieJar[<Cookie BDORZ=27315 for .baidu.com/>]>
#----------------------------------------------------------------------------------------
#{'User-Agent': 'python-requests/2.32.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': #'keep-alive'}
#----------------------------------------------------------------------------------------
#{'User-Agent': 'python-requests/2.32.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': #'keep-alive', 'Cookie': 'BDORZ=27315'}
```

## 常见文件头举例

| 文件类型    | 文件头（十六进制）                     | 说明                |
| ----------- | -------------------------------------- | ------------------- |
| JPEG (.jpg) | FF D8 FF                               | 标识 JPEG 图像      |
| PNG (.png)  | 89 50 4E 47 0D 0A 1A 0A                | PNG 图片文件        |
| GIF (.gif)  | 47 49 46 38 37 61 或 47 49 46 38 39 61 | GIF87a 或 GIF89a    |
| PDF (.pdf)  | 25 50 44 46 2D                         | "%PDF-" 开头        |
| ZIP (.zip)  | 50 4B 03 04                            | 压缩文件            |
| RAR (.rar)  | 52 61 72 21 1A 07 00                   | 压缩文件            |
| EXE (.exe)  | 4D 5A                                  | “MZ” 表示可执行文件 |
| MP3 (.mp3)  | FF FB 或 ID3                           | 音频文件            |

## IP地址

在互联网中，IP地址用于唯一标识一个网络接口

# Git 源码泄露的完整利用

## Git 是如何存储数据的？

Git 使用**对象数据库**存储所有内容，主要有 4 种对象：

1. **Blob 对象** - 存储文件内容
2. **Tree 对象** - 存储目录结构（文件名和对应的 blob）
3. **Commit 对象** - 存储提交信息（作者、时间、commit message、指向 tree）
4. **Tag 对象** - 存储标签信息

每个对象都有唯一的 SHA-1 哈希值作为标识。

一个完整的.git目录结构应该是这样的

```html
.git/
├── HEAD              # 当前分支指针
├── config            # 仓库配置
├── description       # 仓库描述
├── index             # 暂存区
├── refs/             # 引用（分支、标签）
│   ├── heads/        # 本地分支
│   └── tags/         # 标签
├── objects/          # 对象数据库（所有文件内容、提交记录）
│   ├── 5f/
│   │   └── ef682d... # 对象文件
│   └── pack/         # 打包的对象
└── logs/             # 操作日志
    ├── HEAD          # HEAD 变更记录（reflog）
    └── refs/
```

## 利用过程

### 1、获取 .git 目录

```bash
# 如果是网页泄露，使用工具下载
GitHack http://target.com/.git/
# 或
wget -r http://target.com/.git/
```

当然有时候访问备份文件也会有保存`.git`目录

### 2、进入目录并验证

```bash
cd /path/to/.git/..  # 进入 .git 的父目录
git status           # 检查 Git 仓库状态
```

### 3、查看历史提交commit

```bash
git log --all --oneline --graph
```

### 4、查看引用日志reflog

```bash
git reflog
```

### 5、列出所有对象

```bash
git rev-list --objects --all
```

需要注意的是，这里只显示**当前可达的**对象，已删除分支的对象不会显示。

### 6、查看特定提交的文件树

```bash
git ls-tree -r [提交哈希值前七位]
```

### 7、读取对象内容

```bash
# 方法1：使用 cat-file
git cat-file -p f3d34d7cb96b5bcdcda980a1413d2e35154e98de

# 方法2：使用 show（推荐）
git show 353b98f:config.php
```

Git命令

![image-20251013235023702](image/image-20251013235023702.png)

## 常见端口服务即攻击方法

| 端口号               | 端口服务/协议的简要说明                         | 常见攻击手法                             |
| -------------------- | ----------------------------------------------- | ---------------------------------------- |
| TCP/20、21           | FTP（默认的数据和命令传输端口，进行文件传输）   | 匿名访问、留后门、暴力破解、嗅探、提权等 |
| TCP/22               | SSH（Linux系统远程登录、文件上传、SSH加密传输） | 弱口令暴力破解获得Linux系统远程登录权限  |
| TCP/23               | Telnet（明文传输）                              | 弱口令暴力破解、明文嗅探                 |
| TCP/25               | SMTP（简单邮件传输协议）                        | 枚举邮箱用户、邮件伪造                   |
| UDP/53               | DNS（域名解析）                                 | DNS劫持、域传送漏洞                      |
| UDP/69               | TFTP（简单文件传输协议）                        | 文件下载                                 |
| TCP/80、443、8080等  | Web（常见Web服务端口）                          | Web服务                                  |
| TCP/110              | POP邮局协议                                     | 弱口令暴力破解、明文嗅探                 |
| TCP/137、139、445    | Samba（Windows系统和Linux系统间文件共享）       | MS08-067、MS17-010、弱口令暴力破解等     |
| TCP/143              | IMAP（可明文可密文）                            | 暴力破解                                 |
| UDP/161              | SNMP(明文)                                      | 暴力破解、弱密码                         |
| TCP/389              | LDAP（轻型目录访问协议）                        | Ldap注入、匿名访问、弱口令               |
| TCP/512、513、514    | Linux rexec                                     | 暴力破解、rlogin登录                     |
| TCP/873              | rsync备份服务                                   | 匿名访问、上传                           |
| TCP/1194             | Open VPN                                        | VPN账号暴力破解                          |
| TCP/1352             | Lotus Domino邮件服务                            | 弱口令、信息泄露、暴力破解               |
| TCP/1433             | MSSQL数据库                                     | 注入、弱口令、暴力破解                   |
| TCP/1500             | ISPManager主机控制面板                          | 弱口令                                   |
| TCP/1521             | Oracle数据库                                    | 暴力破解、注入                           |
| TCP/1025、111、2049  | NFS                                             | 权限配置不当                             |
| TCP/1723             | PPTP                                            | 暴力破解                                 |
| TCP/2082、2083       | cPanel主机管理面板登录                          | 弱口令                                   |
| TCP/2181             | ZooKeeper                                       | 未授权访问                               |
| TCP/2601、2604       | Zebra路由                                       | 弱口令                                   |
| TCP/3128             | Squid代理服务                                   | 弱口令                                   |
| TCP/3312、3311       | Kangle主机管理登录                              | 弱口令                                   |
| TCP/3306             | MySQL数据库                                     | 注入、暴力破解                           |
| TCP/3389             | Windows RDP远程桌面                             | Shift后门、暴力破解、ms12-020            |
| TCP/4848             | GlassFish控制台                                 | 弱口令                                   |
| TCP/4899             | Radmin远程桌面管理工具                          | 可获取其保存的密码                       |
| TCP/5000             | Sybase/DB2数据库                                | 暴力破解、弱口令                         |
| TCP/5432             | PostgreSQL数据库                                | 暴力破解、弱口令                         |
| TCP/5632             | PcAnywhere远程控制软件                          | 代码执行                                 |
| TCP/5900、5901、5902 | VNC远程桌面管理工具                             | 暴力破解                                 |
| TCP/5984             | CouchDB                                         | 未授权                                   |
| TCP/6379             | Redis存储系统                                   | 未授权访问、暴力破解                     |
| TCP/7001、7002       | WebLogic控制台                                  | Java反序列化、弱口令                     |
| TCP/7778             | Kloxo                                           | 面板登录                                 |
| TCP/8000             | Ajenti主机控制面板                              | 弱口令                                   |
| TCP/8443             | Plesk主机控制面板                               | 弱口令                                   |
| TCP/8069             | Zabbix                                          | 远程执行、SQL注入                        |
| TCP/8080~8089        | Jenkins，Jboss                                  | 反序列化、弱口令                         |
| TCP/9080、9081、9090 | WebSphere控制台                                 | Java反序列化、弱口令                     |
| TCP/9200、9300       | Elasticsearch                                   | 远程执行                                 |
| TCP/10000            | Webmin Linux系统管理工具                        | 弱口令                                   |
| TCP/11211            | Memcached高速缓存系统                           | 未授权访问                               |
| TCP/27017、27018     | MongoDB                                         | 暴力破解、未授权访问                     |
| TCP/3690             | SVN服务                                         | SVN泄露、未授权访问                      |
| TCP/50000            | SAP Management Console                          | 远程执行                                 |
| TCP/50070、50030     | Hadoop                                          | 未授权访问                               |
