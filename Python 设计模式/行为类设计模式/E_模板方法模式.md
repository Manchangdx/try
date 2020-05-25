# 模板方法模式

提到模板，不难想到文档模板、简历模板等。其实模板方法模式中的模板就是这个意思，在模板方法模式中，我们先定义一个类模板，在这个类中，我们定义了各种操作的顺序（轮毂或者说是骨架），但是并不实现这些操作，这些操作由子类来操作。

举个例子，假如有一天我们想去去三岔湖钓鱼，那么需要怎么操作呢？第一步：准备鱼饵；第二步：到达三岔湖；第三步；选择钓点。这三步操作不能乱序，否则我们就钓不成鱼啦。但是在准备鱼饵的时候，可以通过淘宝购买，也可以在渔具店里购买，这些都是不确定。同时怎么去三岔湖也是不确定的，你可以开车去，也可以搭车去。在这种情况下，模板方法模式就非常有用了。在模板方法模式中我们先定义去三岔湖钓鱼的操作步骤，每一步的具体操作在不同的子类中可能都有不同的实现。下面让我们看看具体的代码吧。

#### 第 1 步

首先创建一个模板基类。在模板基类中定义一个流程方法，该方法规定任务步骤如何排列。此外还需要定义一些在子类中必须提供的方法，也就是各个步骤。

模板基类代码如下：

```python
import abc


class Fishing:
    """
    钓鱼模板基类
    """
    __metaclass__ = abc.ABCMeta

    def finishing(self):
        """
        钓鱼方法中，确定了要执行哪些操作才能钓鱼
        """
        self.prepare_bait()         # 准备鱼饵
        self.go_to_riverbank()      # 去河岸
        self.find_location()        # 找到合适的钓鱼位置
        print("Start fishing...")

    @abc.abstractmethod
    def prepare_bait(self):
        pass

    @abc.abstractmethod
    def go_to_riverbank(self):
        pass

    @abc.abstractmethod
    def find_location(self):
        pass
```

#### 第 2 步

假设 John 和 Simon 两位同学要去钓鱼，首先利用模板基类派生出两个子类，这两个子类创建的实例就可以执行任务了。

模板基类已经提供了 fishing 方法，子类只需提供具体每一个步骤的实现即可。

代码如下：

```python
class JohnFishing(Fishing):
    """
    John 也想去钓鱼，它必须实现钓鱼三步骤对应的三个方法
    """

    def prepare_bait(self):
        """
        从淘宝购买鱼饵
        """
        print("John: buy bait from Taobao")

    def go_to_riverbank(self):
        """
        开车去钓鱼
        """
        print("John: to river by driving")

    def find_location(self):
        """
        在岛上选择钓点
        """
        print("John: select location on the island")


class SimonFishing(Fishing):
    """
    Simon 也想去钓鱼，它也必须实现钓鱼三步骤
    """

    def prepare_bait(self):
        """
        从京东购买鱼饵
        """
        print("Simon: buy bait from JD")

    def go_to_riverbank(self):
        """
        骑自行车去钓鱼
        """
        print("Simon: to river by biking")

    def find_location(self):
        """
        在河边选择钓点
        """
        print("Simon: select location on the riverbank")
```

创建任意子类都只需要提供三个步骤对应的方法，其它的工作模板基类已经安排好了。

#### 第 3 步

创建两个子类的实例，执行 fishing 方法：

```python
if __name__ == '__main__':
    # John 去钓鱼
    f = JohnFishing()
    f.finishing()

    print('--------------------------------')

    # Simon 去钓鱼
    f = SimonFishing()
    f.finishing()
```

结果如下：

```bash
John: buy bait from Taobao
John: to river by driving
John: select location on the island
Start fishing...
--------------------------------
Simon: buy bait from JD
Simon: to river by biking
Simon: select location on the riverbank
Start fishing...
```

怎么样？模板方法模式是不是简单易懂呢？模板方法模式是结构最简单的行为型设计模式，在其结构中只存在父类与子类之间的继承关系。通过使用模板方法模式，可以将一些复杂流程的实现步骤封装在一系列基本方法中，在抽象父类中提供一个称之为模板方法的方法来定义这些基本方法的执行次序，而通过其子类来覆盖某些步骤，从而使得相同的算法框架可以有不同的执行结果。模板方法模式提供了一个模板方法来定义算法框架，而某些具体步骤的实现可以在其子类中完成。