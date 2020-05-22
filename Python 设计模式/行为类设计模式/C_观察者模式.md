# 观察者模式

所谓观察者模式，就是说当一个被观察对象（的某个属性）发生变化时会主动发出通知，观察者能及时得到通知并执行某些操作。

#### 第 1 步

被观察者就是被观察类的实例。为了便于批量创建被观察类，可以先写个被观察类的基类。被观察类的基类需要实现被观察类的基本必要属性或方法。

首先是注册和注销功能，被观察者需要提供这两个功能来控制观察者都有谁。我们可以把观察者放到一个列表里。然后就是发出通知的方法。

定义被观察类的基类如下：

```python
class Subject:
    """
    被观察类的基类，用来创建被观察类
    """

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """
        注册一个观察者
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """
        注销一个观察者
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self):
        """
        当被观察者的属性变动时，被观察者调用此方法通知所有观察者执行相应的方法
        """
        for observer in self._observers:
            # 观察者收到被观察者的通知后，调用自身的 update 方法，方法名是自定义的
            observer.update(self)
```

#### 第 2 步

创建一个课程类 Course 作为被观察类，被观察者就是课程啦。当课程有变动时，会主动通知观察者。我们将这个变动设置在课程的 _message 属性上。当这个属性被赋值时，通知观察者。

Course 类的代码如下：

```python
class Course(Subject):
    """
    课程类，被观察类，该类的实例就是被观察的对象
    """

    def __init__(self):
        super(Course, self).__init__()
        self._message = None

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, msg):
        self._message = msg
        # 当 _message 属性被修改，调用实例的 notify 方法通知观察者
        self.notify()
```

#### 第 3 步

创建两个观察类，它们的实例就是观察者。观察者必须有 update 方法，这是被观察类决定的。

为了实现这个「必须」，先写个抽象基类：

```python
import abc


class Observer:
    """
    观察者抽象基类
    """

    __metaclass__ = abc.ABCMeta

    # 当被观察者有变动时，被观察者会告知观察者调用自身的 update 属性
    @abc.abstractmethod
    def update(self, subject):
        pass
```

现在创建两个观察类，称他们为用户观察类和组织观察类吧：

```python
class UserObserver(Observer):
    """
    用户观察者
    """

    def update(self, subject):
        print("User observer: %s" % subject.message)


class OrgObserver(Observer):
    """
    组织观察者
    """

    def update(self, subject):
        print("Organization observer: %s" % subject.message)
```

#### 第 4 步

现在可以创建实例来测试功能了。

首先创建一位被观察者和两位观察者，然后把这俩观察者注册到被观察者的属性里：

```python
if __name__ == '__main__':
    # 创建一个课程类的实例，这个实例就是被观察者
    course = Course()
    
    # 初始化一个用户观察者
    user = UserObserver()
    # 初始化一个机构观察者
    org = OrgObserver()

    # 被观察者注册两个观察者
    course.attach(user)
    course.attach(org)
```

准备就绪，最后写上测试代码：

```python
   # 设置观察者的 message 属性，这时两个观察者会收到通知
    course.message = "第 1 次变更"

    # 被观察者注销一个观察者
    course.detach(user)
    # 再次设置观察者的 message 属性，只有一个观察者会收到通知
    course.message = "第 2 次变更"
```

将以上代码写入文件中执行，结果如下：

```bash
User observer: 第 1 次变更
Organization observer: 第 1 次变更
Organization observer: 第 2 次变更
```

这样就实现了被观察者每次发生时都会触发观察者的操作。

并且观察者和被观察者之间没有耦合，可以随意修改或新建被观察类和观察类并对其进行实例化。