---
title: "Java模板注入之Thymeleaf"
date: 2025-12-02T15:17:42+08:00
summary: "感觉还可以"
url: "/posts/Java模板注入之Thymeleaf/"
categories:
  - "javasec"
tags:
  - "javasec"
draft: true
---

# What's Thymeleaf

官方文档：https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html

和Python的Jinja2一样，Thymeleaf是SpringBoot中的一套模板引擎

Thymeleaf 是一个现代化的服务器端 Java 模板引擎，适用于 Web 和独立环境，能够处理 HTML、XML、JavaScript、CSS 甚至纯文本。

## Thymeleaf 的模板模式

Thymeleaf 的模板模式主要是六种：

- HTML
- XML
- TEXT
- JS
- CSS
- RAW

两种标记模板模式（HTML和XML），三种文本模板模式（TEXT、JAVASCRIPT和CSS），以及一种无操作模板模式（RAW）。

HTML模板模式允许输入任何类型的HTML代码包括HTML5，HTML4和XHTML

XML模板模式允许XML输入，并且解析器会进行格式的检验，发现格式错误会抛出异常

Thymeleaf可以通过表达式帮我们把动态的变量渲染到前端页面，非常的方便

# 模板表达式语法

- `${...}`：
