---
title: "ctfshow原谅杯"
date: 2025-08-14T16:58:29+08:00
summary: "ctfshow原谅杯"
url: "/posts/ctfshow原谅杯/"
categories:
  - "ctfshow"
tags:
  - "原谅杯"
draft: false
---

## 原谅4

```php
<?php isset($_GET['xbx'])?system($_GET['xbx']):highlight_file(__FILE__);
```

传入?xbx=ls，根目录看到一个flag，但是好像权限很低，读不出来

看到一个yuanliang_4_xxx.zip，访问之后把zip下下来

一个图片和一个txt文件，emmmm这个打比赛还有瓜吃

回头看命令好像很多都不能用，看一下bin文件下发现只有ls rm sh能用
