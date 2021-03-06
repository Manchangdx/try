# 命令模式

顾名思义，命令模式就是对命令的封装。所谓封装命令，就是将一系列操作封装到命令类中，并且命令类的实例（命令对象）只需要对外公开一个执行方法 `execute` ，命令对象的调用者只需要执行命令的 `execute` 方法就可以完成所有的操作。

这样命令的调用者就和命令具体操作之间解耦了。我们可以创建任意命令对象，并将其作为参数来创建调用者或将其直接赋值给已存在的调用者的某个属性。

更进一步，通过命令模式我们可以抽象出调用者、命令对象、接收与执行者三部分：

- 命令接收与执行者，简称命令接收者。该对象有一些方法用于执行某些特定操作。
- 命令对象。命令类在实例化时，会将命令接收者作为参数，并将后者赋值给自身实例的某个属性。命令对象会提供一个 execute 方法用来调用命令接收者的某个方法以执行特定操作。
- 调用者。调用者在初始化时会将命令对象作为参数并赋值给自身的某个属性，然后再提供一个方法来调用命令对象的 execute 方法。

执行命令的整个流程如下：

- 命令调用者调用自身的方法 do
- 方法 do 内部调用命令对象的方法 execute
- 方法 execute 调用命令接收者的方法执行具体操作

这些方法的名字都是可以自定义的，建议使用大众化的名字以便阅读。

由上述可知，命令调用者与命令接收者之间没有直接引用关系，前者只需要知道如何发送命令，而不必知道如何执行命令。也就是说命令调用者只需要编写一个调用自身属性的方法即可，这个属性值就是某个命令对象，而且属性值是可以随时变更的；命令对象只需要提供一个执行接口即可，这个执行接口会调用命令接收者的方法；命令接收者只需要提供一个方法来执行任务。各司其职，互不干涉。

接下来举例说明。假设有这么一台虚拟机，它提供了启动和停止功能。

#### 第 1 步

我们先创建一个虚拟机类 VmReceiver ，它的实例就是虚拟机，可以执行启动和停止操作。在命令模式中，该实例就是命令的接收与执行者。

编写如下代码：

```python
class VmReceiver:
    """
    命令接收与执行者类，该类的实例接收命令以执行自身的方法
    """

    def start(self):
        print("Virtual machine start")

    def stop(self):
        print("Virtual machine stop")
```

#### 第 2 步

接下来创建命令类，命令类的实例就是命令对象。命令对象必须提供统一的接口 execute ，为了实现这个「必须」，首先要创建一个抽象基类：

```python
import abc


class Command:
    """
    命令抽象基类
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self):
        """
        命令对象对外只提供 execute 方法
        """
        pass
```

针对虚拟机的启动和停止功能，我们创建两个命令类：

```python
class StartVmCommand(Command):
    """
    命令类，开启虚拟机的命令类
    """

    def __init__(self, recevier):
        """
        使用一个命令接收者初始化
        """
        self.recevier = recevier

    def execute(self):
        """
        真正执行命令的时候命令接收者调用自身的方法开启虚拟机
        """
        self.recevier.start()


class StopVmCommand(Command):
    """
    命令类，停止虚拟机的命令类
    """

    def __init__(self, recevier):
        """
        使用一个命令接收者初始化
        """
        self.recevier = recevier

    def execute(self):
        """
        真正执行命令的时候命令接收者调用自身的方法关闭虚拟机
        """
        self.recevier.stop()
```

这两个类的实例就是命令对象，在实例化时，需要提供命令接收者作为参数。看得出来，命令接收者可以随意修改自身方法内部的代码而不影响命令对象本身的代码逻辑。

#### 第 3 步

命令调用者就是客户端了，也可以称之为虚拟机管理器。虚拟机管理器可以控制虚拟机的启动和停止。

创建调用类如下，该类的实例就是调用者，也就是虚拟机管理器：

```python
class ClientInvoker:
    """
    命令调用者类
    """

    def __init__(self, command):
        self.command = command

    def do(self):
        self.command.execute()
```

调用类在创建实例时，需要提供命令对象作为参数，实例在调用自身的 do 方法时，链式调用各种方法执行具体的某个操作。该实例的 command 属性值指向具体的命令对象，修改此属性值可以实现执行不同命令的效果。

#### 第 4 步

编写测试代码：

```python
if __name__ == '__main__':
    # 创建命令接收与执行者
    recevier = VmReceiver()
    # 创建两个命令对象，创建命令对象时传入命令接收与执行者作为参数
    start_command = StartVmCommand(recevier)
    stop_command = StopVmCommand(recevier)

    # 创建命令调用者，创建命令调用者的时候会传入命令对象作为参数
    # 命令调用者同时也是客户端，通过自身的方法执行固定的命令
    client = ClientInvoker(start_command)
    client.do()

    # 修改命令调用者的命令对象
    client.command = stop_command
    client.do()
```

将以上代码写入脚本，保存并执行：

```bash
Virtual machine start
Virtual machine stop
```

可以看出命令模式的封装性很好，每个命令都被封装起来。对于客户端来说，需要什么功能就去调用相应的命令，而无需知道命令具体是怎么执行的。同时命令模式的扩展性很好，在命令模式中，在接收者类一般会对操作进行最基本的封装，命令类则通过对这些基本的操作进行二次封装。当增加新命令的时候，对命令类的编写一般不是从零开始的，有大量的接收者类可供调用，也有大量的命令类可供调用，代码的复用性很好。

