---
title: K8s基础
date: 2026-06-17T14:57:57+08:00
lastmod: 2026-06-22T17:34:57+08:00
summary:
url: /posts/K8s基础/
categories:
  - 云安全
tags:
  - K8s
draft: false
---
# 什么是Kubernetes

Kubernetes又名k8s，是一个由Google开源，现由 CNCF（云原生计算基金会）维护的容器编排平台

Kubernetes（K8s） 集群是k8s的基本运行单元，由一个控制平面和一组用于运行容器化应用的工作机器组成， 这些工作机器称作节点（Node）。每个集群至少需要一个工作节点来运行 Pod。

K8S集群主要负责容器编排，本质上来说，K8S不仅能将单个容器运行起来，将其对外暴露出去提供服务。还提供了：路由网关、集群监控、灾难恢复，以及应用的水平扩展等能力。

# Kubernetes架构

![](image/Pasted%20image%2020260731112310.png)

从结构图不难看出，k8s主要是由Master节点（控制平面）以及工作器节点组成，Master节点参与对Node节点的管理控制
# Master节点

MasterNode主要包括四个部分：

- ApiServer：顾名思义就是提供API接口进行资源操作，并提供认证、授权、访问控制、API 注册和发现等机制
- Controller Manager：控制管理，负责维护集群的状态，监控各种资源状态的变化
- Scheduler：调度程序，负责资源的调度，其实就是根据策略将Pod调度到相应的机器上
- etcd：里面保存了整个集群的状态，用作 Kubernetes 所有集群数据的后台数据库。

# Worker节点

WorkerNode主要有以下部分：

- pod：k8s的最小的调度和运行单元，一个pod可以包含一个或多个容器，pod内所有容器都共用一个IP地址和网络命名空间，其实就类似于一台机器以及机器上的进程服务
- kubelet：每台节点上的代理，负责维护容器的生命周期
- Kube-proxy：通过为Service资源的ClusterIP生成iptable或ipvs规则，实现将K8S内部的服务暴露到集群外面去；处理节点上的网络规则，让 Pod 之间能互相通信

# k8s和docker，docker-compose的区别

最大的区别就是在于运行管理方面，doker和docker-compose更偏向于单机运行的管理，docker一次只能管理一个容器，虽然docker-compose能同时管理多个容器，但本质上还是只限制在一台机器中，而k8s是集群多机器编排，可以同时管理多台机器

除此之外，k8s还有以下特点：

- 弹性伸缩：容器数量的控制，流量高峰自动加副本，低谷自动缩减，节省成本
- 自我修复/高可用：对容器进行监测，如果某台机器宕机，Pod 自动迁移到其他机器，而出现问题的机器会自动抛弃或重启
- 自动部署和回滚：自动对容器的回滚更新且更新版本时无缝替换，用户无感知

# k8s工作流程

k8s工作的时候通常会使用kubectl，kubectl 是 k8s 的客户端工具，可以使用命令行管理集群

具体流程如下：

- kubectl向apiserver发送部署创建请求（例如使用 kubectl create -f deployment.yml）
- apiserver将请求写入etcd，随后收到etcd的回调事件
- apiserver将回调事件发送给ControllerManager，ControllerManager中的ReplicationController根据deployment的描述创建一个ReplicaSet并将ReplicaSet对象返回给apiserver并持久化回etcd
- Scheduler调度程序看到未调度的pod对象，根据调度规则选择一个可调度的节点，将节点名写入pod描述的nodeName字段中，并将pod对象返回给apiserver并写入etcd
- apiserver接收到etcd的回调后会将更新pod的事件发送给pod对应的node上的kubelet进程
- kubelet在看到有pod对象中nodeName字段属于本节点，将其从队列中拉出，通过容器运行时创建pod中描述的容器

# k8s安全基础

一方面是组件接口的安全风险：

## API server未授权访问

API server的默认服务接口是8080和6443，但是8080只提供http服务，并没有认证与授权机制，而6443两者兼并

默认情况下8080端口是不会启动的，但是如果使用者开启了该服务，就可能会造成API的未授权访问，从而控制整个k8s集群

使用kubectl获取集群信息

```bash
kubectl -s [ip]:[port] get nodes
```

## Kubelet未授权访问

Kubelet也是运行API服务的，默认服务端口是10250和10248，同样也容易存在未授权访问

## etcd信息泄露

etcd默认监听2379（用于客户端连接）和2380（用于多个etcd之间的通信）端口

默认情况下，etcd两个端口的访问都需要证书去进行认证，所以如果我们拿到了证书或者使用者给etcd设置了允许匿名访问，那么就可以读取etcd中的数据，导致信息泄露风险

- etcd v2：Kubernetes ≤ 1.5的版本默认使用etcd v2

```html
/v2/keys/?recursive=true
```

- etcd v3：k8s v1.6开始默认使用 etcd v3,一般使用etcdctl实现对etcd的访问

文档：https://github.com/etcd-io/etcd/tree/main/etcdctl

```bash
./etcdctl --endpoints=x.x.x.x:2379 get / --prefix --keys-only
```



另一方面是k8s常见的漏洞，包括未授权访问，权限提升，权限维持，凭证窃取等

这里放一张yuy0ung师傅的图

| **初始访问**            | **权限提升**             | **防御绕过**             | **凭证窃取**                    | **权限维持**         |
| ------------------- | -------------------- | -------------------- | --------------------------- | ---------------- |
| 版本信息探测              | 特权容器逃逸               | 容器及宿主机日志清理           | Kubernetes secret窃取         | 后门Pod            |
| insecure-port未授权访问  | rolebinding添加用户权限    | Kubernetes audit日志清理 | Kubernetes ServiceAccount泄露 | Shadow-apiserver |
| Api-server匿名访问      | 目录挂载逃逸               | 利用系统Pod伪装            | 应用层Api凭据泄露                  | cronjob持久化       |
| Kubeconfig泄露        | 操作系统内核漏洞逃逸           | 通过代理访问Api-server     | 利用Kubernetes准入控制器获取信息       | 后门镜像             |
| Kubelet未授权访问        | Docker漏洞逃逸           | 关闭安全产品平台容器           | Pod服务账户凭据窃取                 | 修改核心组件访问权限       |
| Docker daemon未授权访问  | Kubernetes漏洞提权       | 创建超长Annotations      |                             | 系统层后门            |
| 通过Nodeport访问Service | Docker.sock逃逸        | CVE-2019-1002101     |                             | DaemonSets后门     |
| Dashboard未授权访问      | Linux Capabilities逃逸 |                      |                             |                  |
| etcd未授权访问           | CVE-2018-1002105     |                      |                             |                  |

参考文章：

https://yuy0ung.github.io/blog/%E4%BA%91%E5%AE%89%E5%85%A8/k8s%E5%AE%89%E5%85%A8/k8s%E5%AE%89%E5%85%A8%E5%9F%BA%E7%A1%80/

https://www.cnblogs.com/ZhuChangwu/p/16441181.html

https://kubernetes.io/zh-cn/docs/concepts/architecture/

