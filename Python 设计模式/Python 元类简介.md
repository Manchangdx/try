# Python 元类

元类的英文名是 metaclass 。元类是对类的概念的一种抽象定义。

举个例子，'hello kitty' 是 str 类的实例，str 类可以看做是 type 的实例。type 是内置函数，它用于判断某个对象的类型，也可以用于创建新的类。type 就是新创建的类的默认元类。

```python
class Test1: 
    ...
    
class Test2(object, metaclass=type):
    ...
```

这两个类其实是一样的。Test1 的默认父类就是 object ，默认元类就是 type 。

创建类的时候，先调用元类的 `__new__` 方法，再调用元类的 `__init__` 方法。如果元类没有相应的方法，调用 type 的同名方法。

创建类的实例时，先调用类的 `__new__` 方法，再调用类的 `__init__` 方法。如果类没有相应的方法，调用 object 的同名方法。

所谓 “创建元类” 其实就是重写 type 中的各种方法的过程。

## 1、利用 `__new__` 方法增删改类的属性

#### 1.1 添加属性或方法

列表 list 的实例没有 add 方法，有 append 方法来增加一个元素到列表尾部。

现在我们创建一个类 List ，使得其实例有 add 方法，可以像 append 方法一样添加元素。

使用元类来实现，首先创建元类，然后使用元类创建类：

```python
class ListMeta(type):
    '''
    这就是一个元类，可以理解为“它的实例是类”
    '''

    # 参数 cls 指代元类自身
    # 参数「类名」是要创建的类的类名
    # 参数「父类的元组」就是新建的类需要继承的父类的元组
    # 参数「属性字典」为字典，它有一些 key ，例如 __module__ 、__doc__ 等
    # 此外类中的属性也会加进来，例如下面的 name 属性
    def __new__(cls, 类名, 父类的元组, 属性字典):
        print('cls:', cls)
        属性字典['add'] = lambda self, value: self.append(value)
        print('属性字典:', 属性字典)
        # return type.__new__(cls, 类名, 父类的元组, 属性字典)
        # 为了便于研究，上面的一行代码改写成了下面的 4 行代码
        a = type.__new__(cls, 类名, 父类的元组, 属性字典)
        print('-------a 就是 List 类:', a)
        print('-------List 类的属性:', dir(a))
        return a
      
      
# 下面这个就是我们要实现的类
class List(list, metaclass=ListMeta):
    '''
    创建 List 类时，会调用元类 ListMeta 的 __new__ 方法
    返回值是调用 type 的 __new__ 方法，该方法会将父类的“非私有属性”赋值给 List 类
    '''
    name = '哈喽World'
```

定义 List 类时，首先执行元类的 `__new__` 方法，在属性字典里加上 add ，再调用 type 的 `__new__` 方法生成 List 类。这样 List 类就有了属性字典中的全部属性以及父类的所有属性（双下划线的私有属性除外）。

最后还要调用元类的 `__init__` 方法，这里没有定义，那就直接调用 type 的 `__init__` 方法。此处没有用到。

**突然想到：在类内部定义的实例方法也可以被类直接调用，但需要传入 self 参数。**

举例如下：

```python
In [269]: s = set()

In [270]: class Test:
     ...:     def append(self, n):
     ...:         return self.add(n)
     ...:

In [271]: s
Out[271]: set()

In [272]: Test.append(s, 'adfs')

In [273]: s
Out[273]: {'adfs'}
```

#### 1.2 强制子类实现特定方法

假设你是一个库的作者，如下所示的代码中，Base.foo 方法要用到子类实现的方法 bar ：

```python
class Base(object):
    def foo(self):
        return self.bar()


class Derived(Base):
    def bar():
        ...
```

所以要求子类 Derived 必须提供 bar 方法，否则不予创建这个子类。

```python
class BaseMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        # 如果 name 不是基类的名字，那就是创建子类啦
        # 如果并且子类没有提供 bar 属性，那就不予创建这个子类
        if name != 'Base' and 'bar' not in namespace:
            raise TypeError('bad user class')
        return super().__new__(cls, name, bases, namespace, **kwargs)

class Base(object, metaclass=BaseMeta):
    def foo(self):
        return self.bar()
```

这会儿再将 Base 类作为父类创建子类时，子类就必须要提供 bar 属性了。

## 2、利用 `__init__` 方法增删改类的属性

有时我们会希望获取继承了某个类的子类。例如，实现了基类 List ，想知道都有哪些子类继承了它。用元类就能实现这个功能，也就是在初始化类的时候，在初始化方法 `__init__` 里做些手脚。

**注意：在元类中定义方法，参数 cls 通常指代元类本身，参数 self 指代利用元类定义的类。**

代码如下：

```python
class ListMeta(type):

    def __new__(cls, 类名, 父类的元组, 属性字典):
        '''创建类'''
        # 参数 cls 指代元类自身 ListMeta
        print('__new__ cls:', cls)
        属性字典['add'] = lambda self, value: self.append(value)
        return type.__new__(cls, 类名, 父类的元组, 属性字典)

    def __init__(self, name, bases, namespace, **kwargs):
        '''对类进行初始化'''
        # 参数 self 指创建的类 List
        print('__init__ self:', self)
        # 第一次使用 ListMeta 元类创建类 List 时
        # List 没有 sub_class_dict 这个属性，就定义一个空字典给它
        # 使用 List 作为父类创建子类 L1 和 L2 时
        # 子类会继承父类的 sub_class_dict 属性，这由 type.__new__ 完成
        # 继承关系的类们共享父类的属性，除非子类重新定义该属性
        if not hasattr(self, 'sub_class_dict'):
            self.sub_class_dict = {}
        else:
            self.sub_class_dict[name.lower()] = self
        print('初始化完成\n')
        
        
class List(list, metaclass=ListMeta):
    '''
    创建 List 类时，会调用元类 ListMeta 的 __new__ 方法
    返回值是调用 type 的 __new__ 方法，该方法会将父类的“非私有属性”赋值给 List 类
    type.__new__ 方法的返回值就是 List 类
    最后再调用 ListMeta.__init__ 方法初始化一下
    '''
    name = '哈喽World'


class L1(List): ...
class L2(List): ...
  
print(List.sub_class_dict)
print(L2.sub_class_dict)

l = List()
l.add('adsf')
print(l)
```

## 3、利用 `__call__` 方法设置类的调用规则

#### 3.1 禁用实例化功能

现需要创建一个类 NoInstance ，它不可以被调用，也就是不能创建实例，只能调用类的属性。实现这样的类是极为简单的，把它的 `__call__` 方法封死就行了，调用这个方法就抛异常即可。

我们知道控制实例调用自身的方法是定义在类中的 `__call__` 方法，那么控制类调用自身生成实例的 `__call__` 方法就定义在元类之中。所以定义个元类，写个 `__call__` 方法就行了：

```python
In [280]: class NoInstanceMeta(type):
     ...:     def __call__(self, *args, **kw):
     ...:         raise TypeError('这个类不能实例化')
     ...:

In [281]: class NoInstance(metaclass=NoInstanceMeta):
     ...:     name = 'Irving'
     ...:     # 这里可以写一些类方法和静态方法
     ...:     @classmethod
     ...:     def hello(cls, name):
     ...:         print('Hello,', name)
     ...:

In [282]: ni = NoInstance()
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-282-bd0e60b917f6> in <module>
----> 1 ni = NoInstance()

<ipython-input-280-f25f235eb8b1> in __call__(self, *args, **kw)
      1 class NoInstanceMeta(type):
      2     def __call__(self, *args, **kw):
----> 3         raise TypeError('这个类不能实例化')
      4

TypeError: 这个类不能实例化

In [283]: NoInstance.hello('Kitty')
Hello, Kitty

In [284]: NoInstance.name
Out[284]: 'Irving'
```

#### 3.2 实现单例模式

现在需要编写一个单例类 Singleton ，也就是说对该类进行实例化多次，得到的都是同一个实例。

我们可以创建一个这样的元类 SingletonMeta，在其中编写初始化方法，生成 Singleton 的一个属性，这个属性的值暂定为 None。

当类在进行实例化时，会调用元类的 `__call__` 方法，这个方法会根据 `Singleton.__instance` 的值来运行。结果就是 Singleton 类可以实例化多次，但返回值都是同一个。

代码如下：

```python
class SingletonMeta(type):
    '''单例类的元类'''
    
    def __init__(self, *args, **kwargs):
        print('【SingletonMeta.__init__】初始化类')
        print('【SingletonMeta.__init__】self:', self)
        print('【SingletonMeta.__init__】id(self):', id(self))
        # 定义一个私有属性
        self.__instance = None

    def __call__(self, *args, **kwargs):
        '''对 Singleton 类进行实例化时调用这个方法'''
        print('【SingletonMeta.__call__】创建 Singleton 的实例')
        if self.__instance is None:
            # 调用 SingletonMeta 的父类 type 的 __call__ 方法生成前者的实例
            # super 指的是 SingletonMeta 的父类 type
            #self.__instance = type.__call__(self, *args, **kwargs)
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


print('11111111111111111111111111111111111111111111111111111111111111')

class Singleton(metaclass=SingletonMeta):
    def __init__(self):
        # 对类进行实例化时，会打印这个，多次实例化操作只会打印一次
        # 因为只执行一次元类的 __call__ 方法，而 __init__ 方法是由前者内部调用的
        print('【Singleton.__init__】Creating Spam')


print('22222222222222222222222222222222222222222222222222222222222222')

# 在定义 Singleton 时，就调用了元类的初始化方法打印了类的 ID
# 此处再次打印类的 ID
print('类 Singleton 的 ID:', id(Singleton))
# 把类看作实例的话，元类相当于类的类
# 在类的外部获取实例的双下私有属性的格式是：_类名属性名
# 打印类的私有属性 __instance 的值
print('类 Singleton 的 __instance 属性值：',
        Singleton._SingletonMeta__instance)

print('33333333333333333333333333333333333333333333333333333333333333')

# 对类进行实例化，打印实例属性
s1 = Singleton()
print(id(s1))
s2 = Singleton()
print(id(s2))
```

## 4、抽象类

使用 abc 模块提供的 ABCMeta 元类可以很容易地创建抽象类：

```python
from abc import ABCMeta, abstractmethod


class Test(metaclass=ABCMeta):
    
    @abstractmethod
    def xxx():
        ...
```

抽象类一定会提供至少一个被 `@abstractmethod` 装饰的方法。抽象类的特点是不能被实例化。

一个应用的例子，调用 ABCMeta 元类创建抽象基类，使得抽象基类的子类必须提供某个属性或方法：

```python
from abc import abstractmethod, ABCMeta


# 接口类中定义了一些接口名：pay ，paying
# 且并未实现接口的功能，子类继承接口类，并且实现接口中的功能
class Payment(metaclass=ABCMeta):
    '''接口类，抽象基类'''

    # 利用抽象元类创建抽象类
    # 目的是把这个抽象类作为基类创建子类，并为子类提供一些特别的方法
    # 这些特别的方法在基类中创建，须使用 abstractmethod 抽象方法装饰器装饰
    # 此处抽象出来的方法是 pay ，也就是说子类在创建时，须定义同名方法
    # 且子类是真正干活的类，子类的 pay 方法是提供实际功能的方法
    @abstractmethod
    def pay(self, money):
        pass


class WeichatPay(Payment):
    '''子类'''

    def pay(self, money):
        print('微信支付了')


class AliPay(Payment):
    '''子类'''

    # 这里定义的方法名不是 pay ，在实例化的时候就会报错
    def paying(self, money):
        print('支付宝支付了')


# 用子类的实例作为参数进行支付操作
def pay(pay_obj, money):
    pay_obj.pay(money)

# WeichatPay 是可以正常使用的，因为它提供了 pay 方法
p = WeichatPay()
pay(p, 123)

# AliPay 类实例化的时候就会报错：
# TypeError: Can't instantiate abstract class Alipay with abstract methods pay
p = AliPay()
pay(p, 123)
```

