# 单例模式

单例模式有点意思，它有多种实现方法。

### 方法 1

```python
class Singleton:
    '''
    单例模式
    '''

    # 创建一个嵌套类，当前类 Singleton 的实例会
    class _A:
        def display(self):
            return id(self)

    _instance = None

    def __init__(self):
        __class__._instance = __class__._instance or __class__._A()

    def __getattr__(self, attr):
        return getattr(__class__._instance, attr)
```

- 这个单例模式在定义类的时候，在内部定义一个嵌套类 _A 。
- 在首次实例化 Singleton 时，会给 Singleton 本身添加一个属性 `_instance` ，该属性值就是嵌套类 _A 的实例。
- 后续实例化时，不再生成 _A 的实例。
- 每个 Singleton 的实例在获取属性时，都会调用 `__getattr__` 方法获取 Singleton._instance 的同名属性，也就是 _A 的实例的属性值。

所以这个方法实际上每次实例化 Singleton 时都会生成不同的实例，但这些实例在调用属性和方法时，结果都是相同的。

### 方法 2

```python
class Singleton:
    """
    单例类装饰器，可以用于想实现单例的任何类。注意，不能用于多线程环境。
    """

    def __init__(self, cls):
        print('装饰器初始化')
        self._cls = cls

    def instance(self):
        # 返回真正的实例
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
        return self._instance

    def __call__(self):
        return self.instance()

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class A:

    def display(self):
        return id(self)
```

首先创建一个类 Singleton ，该类的初始化方法将某个类作为参数，这样就实现了类装饰器，也就是在创建新的类时 Singleton 可以作为装饰器。凡是具有 `__call__` 方法的对象都可以作为装饰器，例如函数和类。

被 Singleton 装饰的类，在定义时就会调用 Singleton 类的初始化方法。当我们调用类 A 时，类 A 就是 Singleton 的实例。而原本定义的类 A 就被赋值给了 Singleton 的实例的 _cls 属性。

现在约定被装饰器装饰的类 A 为「类 A」，本来的类 A 为「原类 A」。

调用类 A 的代码是：

```python
A()
```

这看起来像是对原类 A 进行实例化，其实就是调用 Singleton 的实例的 `__call__` 方法，进一步调用 Singleton 内部的 instance 方法，返回原类 A 的实例。

简言之，就是调用类 A 会得到原类 A 的实例。而且 Singleton.instance 方法使得这个原类 A 只可能会被实例化一次。

总结一下：Singleton 每作为生成器定义一个新类，就会生成一个自身的实例。调用类 A 就是调用 Singleton 的实例本身的 `__call__` 方法。而原类 A 被赋值给类 A 的 _cls 属性。调用类 A 会得到原类 A 的实例，且该实例只有唯一的一个。

### 方法 3

在对类进行实例化时，需要先调用类的 `__new__` 方法创建实例，再调用实例的 `__init__` 方法初始化。所以要实现单例模式，可以在类的 `__new__` 方法中做文章。

代码如下：

```python
In [40]: class Singleton:
    ...:     def __new__(cls, *args, **kw):
    ...:         if not hasattr(cls, '_Singleton__instance'):
    ...:             cls.__instance = super().__new__(cls, *args, **kw)
    ...:         print(id(cls.__instance))
    ...:         return cls.__instance
    ...:

In [41]: s1 = Singleton()
4444858960

In [42]: s2 = Singleton()
4444858960

In [43]: s1 is s2
Out[43]: True
```

