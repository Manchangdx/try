## 代理模式

代理模式在生活中比比皆是。比如你通过代理上网，比如你不会去华西牛奶生产地直接买牛奶，而是到超市这个代理购买牛奶，这些例子中都存在着代理模式。所谓代理模式就是给一个对象提供一个代理，并由代理对象控制对原对象的访问。通过代理，我们可以对访问做一些控制。在开发网站的过程中，针对一些频繁访问的资源，我们会使用缓存。在开发实验楼的过程中也是如此，我们通过缓存代理解决了一些热点资源的访问问题。下面让我们看看是怎么实现的吧。

下面的例子来模拟 Redis 缓存图片数据的过程。

#### 第 1 步

首先创建一个模拟 Redis 服务的类，并对其进行实例化，它可以实现缓存数据的功能：

```python
from time import sleep


class Redis:
    """
    用于模拟 redis 服务
    """

    def __init__(self):
        """
        使用字典存储数据
        """
        self.cache = dict()

    def get(self, key):
        """
        获取数据
        """
        return self.cache.get(key)

    def set(self, key, value):
        """
        设置数据
        """
        self.cache[key] = value
        
        
redis = Redis()
```

实例 redis 拥有一些方法可以实现数据缓存。这里我们使用一个字典对象来存储数据。

#### 第 2 步

接下来创建 Image 类和 Page 类。Image 类的实例就是图片本身，它有 name 和 url 两个属性。Page 类的实例可以获取图片的 url 属性并展示图片。

代码如下：

```python
class Image(object):
    """
    图片对象，图片存在七牛云存储中，我们只保存了一个地址
    """

    def __init__(self, name):
        self.name = name

    @property
    def url(self):
        sleep(2)
        return "https://dn-syl-static.qbox.me/img/logo-transparent.png"


class Page(object):
    """
    用于显示图片
    """

    def __init__(self, image):
        """
        需要图片进行初始化
        """
        self.image = image

    def render(self):
        """
        显示图片
        """
        print(self.image.url)
```

#### 第 3 步

定义图片代理类，该类的实例用于调用 redis 缓存图片数据。创建 Page 类的实例时，会将该类的实例作为参数。

代码如下：

```python
class ImageProxy:
    """
    图片代理，首次访问会从真正的图片对象中获取地址，以后都从 Redis 缓存中获取
    """

    def __init__(self, image):
        self.image = image

    @property
    def url(self):
        addr = redis.get(self.image.name)
        if not addr:
            addr = self.image.url
            print("Set url in redis cache!")
            redis.set(self.image.name, addr)
        else:
            print("Get url from redis cache!")
        return addr
```

#### 第 4 步

创建各个类的实例进行测试：

```python
if __name__ == '__main__':
    img = Image(name="logo")
    proxy = ImageProxy(img)
    page = Page(proxy)
    # 首次访问
    page.render()
    print("")
    # 第二次访问
    page.render()
```

结果如下：

```bash
Set url in redis cache!
https://dn-syl-static.qbox.me/img/logo-transparent.png

Get url from redis cache!
https://dn-syl-static.qbox.me/img/logo-transparent.png
```

在上面的代码中我们使用代理模式实现了对图片的缓存。在使用缓存之前，我们实现了`Redis`对象简单模拟了[Redis](http://baike.baidu.com/item/Redis)服务。可以看到访问`Image.url`属性是比较耗时的操作（我们使用`time.sleep`模拟了耗时操作），如果每次都是直接访问该属性，就会浪费大量的时间。通过实现`ImageProxy`缓存代理，我们将图片地址缓存到 `Redis` 中，提高了后续的访问速度。

从上面的代码可以看出，代理对象和真实的对象之间都实现了共同的接口，这使我们可以在不改变原接口情况下，使用真实对象的地方都可以使用代理对象。其次，代理对象在客户端和真实对象之间直接起到了中介作用，同时通过代理对象，我们可以在将客户请求传递给真实对象之前做一些必要的预处理。