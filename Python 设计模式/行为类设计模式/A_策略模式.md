# 策略模式

在实验楼网站的问答模块中，一个问题可能有多种显示方式：

- 普通用户，显示问题内容
- 管理员用户，显示问题内容并显示编辑按钮

这样一个对象我们该怎么实现呢？看以下代码：

```python
class Question(object):
    """
    问题类，没有使用策略模式之前的写法
    """

    def __init__(self, admin=False):
        self._admin = admin

    def show(self):
        """
        根据是否是管理员显示不同的信息 
        """
        if self._admin:
            return "显示问题内容和编辑按钮"
        return "显示问题内容"


if __name__ == '__main__':
    q1 = Question()
    print(q1.show())
    q2 = Question(admin=True)
    print(q2.show())
```

创建问题类的实例时，需要提供一个参数以决定该问题的显示方式。

在上面的介绍中，问题的显示方式有两种：针对普通用户和针对管理员用户。如果在项目的后续需求中出现了「增加问题的显示方式」，就需要整体修改 Question 类了，随着代码量的增加，这会变得麻烦。

如何设计 Question 类，才能使得「增加问题的显示方式」这个需求变得容易实现？这就轮到「策略模式」发挥作用了。

代码修改如下：

```python
import abc


class AbsShow:
    """
    显示方式有很多种，把它们称作「管理员显示」、「用户显示」等等
    这些显示方式都设计成类，让类的实例调用自身的 show 方法来显示
    当前这个类就是这些显示方式类的抽象父类
    定义此类用到了抽象基类 ABCMeta 和抽象方法装饰器 @abstractmethod
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def show(self):
        pass


class AdminShow(AbsShow):
    """
    管理员显示类
    """

    def show(self):
        return "显示问题内容和编辑按钮"


class UserShow(AbsShow):
    """
    普通用户显示类
    """

    def show(self):
        return "显示问题内容"


class Question:
    """
    问题类，使用「策略模式」后
    """

    def __init__(self, show_obj):
        # 初始化问题类的实例时，给实例定义一个属性
        # 属性值就是某个显示类的实例
        self.show_obj = show_obj

    def show(self):
        # 调用问题类的实例的 show 方法，会调用显示类的实例的同名方法
        print(self.show_obj.show())



if __name__ == '__main__':
    user_show = UserShow()      # 用户显示类的实例
    admin_show = AdminShow()    # 管理员显示类的实例
    q = Question(user_show)     # 这个问题实例的显示方式是「用户显示」
    print('用户显示：', end=' ')
    q.show()
    q.show_obj = admin_show     # 修改问题的属性就可以修改显示方式啦
                                # 这叫做策略模式的「互换行为」
    print('管理员显示：', end=' ')
    q.show()
```

之前的做法是在创建 Question 实例时需要一个参数，在类的内部预先定义好这个参数指向什么结果。

使用策略模式后，每个显示方式自己有一个单独的类，这个类的实例有个方法提供显示功能。需要添加显示方式，就创建一个类，然后创建其实例。

Question 在实例化时，依然提供一个参数，这个参数就是显示方式类的实例，这个实例有个方法提供显示功能。

也就是说「策略模式」把提供功能的那部分代码放到 Question 类的外部了。想要增加什么显示方式，外部去实现，Question 在实例化的时候只管调用一个显示方式类的实例。

此外还有一个叫「互换行为」的东西，其实就是因为 Question 的实例使用一个属性指向显示方式类的实例，改变 Question 的实例的属性值就会改变显示方式。这个功能用不用「策略模式」都有。

