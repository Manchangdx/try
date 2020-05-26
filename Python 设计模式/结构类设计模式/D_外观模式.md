## 外观模式

所谓外观模式，就是将各种子系统的复杂操作通过外观模式简化，让客户端使用起来更方便简洁。比如你夏天晚上出门时，要关闭电灯，关闭电视机，关闭空调。如果有了一个总开关，通过它可以关闭电灯，电视机和空调，你出门的时候关闭总开关就行了。在这个例子中，你就是客户端，总开关就是外观模式的化身。在实验楼中，外观模式应用在创建实验环境的接口上。让我们看看具体的代码吧。

#### 第 1 步

首先，创建三个类模拟用户、课程和实验：

```python
class User:
    """
    用户类
    """
    def is_login(self):
        return True

    def has_privilege(self, privilege):
        return True


class Course:
    """
    课程类
    """
    def can_be_learned(self):
        return True


class Lab:
    """
    实验类
    """
    def can_be_started(self):
        return True
```

#### 第 2 步

创建客户端类，该类的实例用来启动实验环境。启动实验环境之前，先要对用户、课程和实验进行判断，全部符合要求才会启动实验环境。

代码如下：

```python
class Client:
    """
    客户类，用于开始一个实验
    """
    def __init__(self, user, course, lab):
        self.user = user
        self.course = course
        self.lab = lab

    def start_lab(self):
        """
        开始实验，需要一系列的判断：
        用户是否登录，课程是否可以学习，实验是否可以开始。判断非常繁琐！
        """
        if (self.user.is_login() and self.course.can_be_learned() and
                self.lab.can_be_started()):
            print("Start lab")
        else:
            print("Can not start lab")
```

#### 第 3 步

客户端采用「外观模式」设计，其原理简单到不能再简单了，就是把原客户端里的 start_lab 方法里启动实验环境的代码拿出来，放到另一个类里面。

代码如下：

```python
class FacadeLab:
    """
    新的 Lab 类，应用了面向对象模式
    """

    def __init__(self, user, course, lab):
        self.user = user
        self.course = course
        self.lab = lab

    def can_be_started(self):
        if (self.user.is_login() and self.course.can_be_learned() and
                self.lab.can_be_started()):
            return True
        else:
            return False


class NewClient:
    """
    新的客户类，使用外观模式
    """
    def __init__(self, facade_lab):
        self.lab = facade_lab

    def start_lab(self):
        """
        开始实验，只需要判断 FacadeLab 是否可以开始
        """
        if self.lab.can_be_started:
            print("Start lab")
        else:
            print("Can not start lab")
```

#### 第 4 步

创建各个类的实例：

```python
if __name__ == '__main__':
    print('General Pattern:')
    user = User()
    course = Course()
    lab = Lab()
    client = Client(user, course, lab)
    client.start_lab()

    print("Facade Pattern:")
    facade_lab = FacadeLab(user, course, lab)
    facade_client = NewClient(facade_lab)
    facade_client.start_lab()
```

对于不同的客户端，其结果是一样的：

```bash
General Pattern:
Start lab
Facade Pattern:
Start lab
```

以上代码中，我们使用了在[实验楼](https://www.shiyanlou.com)中启动实验的案例实现了外观模式。正常情况下，我们开始一个实验，需要判断一系列前置条件：用户是否已经登录、课程是否满足学习的条件、实验是否满足可以启动等。如果我们直接将这些对象在客户端 Client 类中使用，无疑增加了客户端类和 `User`，`Course` 和 `Lab` 类的耦合度。另外如果我们要增加新的前置条件判断时，我们就要修改`Client`类。为了解决这些问题，我们引入了外观模式实现了`FacadeLab`类，在这个类中，我们通过对外提供接口`FacadeLab.can_be_started`来屏蔽客户端类对子系统的直接访问，使得新的客户端类`NewClient`的代变得简洁。

总的来说外观模式的主要目的在于降低系统的复杂程度，在面向对象软件系统中，类与类之间的关系越多，不能表示系统设计得越好，反而表示系统中类之间的耦合度太大，这样的系统在维护和修改时都缺乏灵活性，因为一个类的改动会导致多个类发生变化，而外观模式的引入在很大程度上降低了类与类之间的耦合关系。引入外观模式之后，增加新的子系统或者移除子系统都非常方便，客户类无须进行修改（或者极少的修改），只需要在外观类中增加或移除对子系统的引用即可。