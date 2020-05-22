# 命令模式

顾名思义，命令模式就是对命令的封装。所谓封装命令，就是将一系列操作封装到命令类中，并且命令类的实例只需要对外公开一个执行方法 `execute` ，调用此命令的对象（调用者）只需要执行命令的 `execute` 方法就可以完成所有的操作。

这样调用此命令的对象就和命令具体操作之间解耦了。

更进一步，通过命令模式我们可以抽象出调用者、接收（并执行）者和命令三个对象：

- 命令接收与执行者。该对象有一些方法用于执行某些特定操作。该对象会被命令对象调用自身的一些方法来执行特定操作。
- 命令对象。命令类在实例化时，会将命令接收与执行者作为参数，并将后者赋值给自身实例的某个属性。命令类的实例会提供一个 execute 方法用来调用命令接收者的某个方法以执行特定操作。

- 调用者。调用者在初始化时会将命令对象作为参数并赋值给自身的某个属性，然后再提供一个方法来调用命令对象的 execute 方法。链式发展，execute 方法会调用命令接收者的某个方法以执行特定操作。

命令调用者与命令接收者之间没有直接引用关系，命令调用者只需要知道如何发送命令，而不必知道如何执行命令。

示例代码如下：

```python
import abc


class VmReceiver:
    """
    命令接收与执行者类，该类的实例接收命令以执行自身的方法
    """

    def start(self):
        print("Virtual machine start")

    def stop(self):
        print("Virtual machine stop")


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


class ClientInvoker:
    """
    命令调用者类
    """

    def __init__(self, command):
        self.command = command

    def do(self):
        self.command.execute()


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

总地来说，命令模式的封装性很好，每个命令都被封装起来。对于客户端来说，需要什么功能就去调用相应的命令，而无需知道命令具体是怎么执行的。同时命令模式的扩展性很好，在命令模式中，在接收者类中一般会对操作进行最基本的封装，命令类则通过对这些基本的操作进行二次封装。当增加新命令的时候，对命令类的编写一般不是从零开始的，有大量的接收者类可供调用，也有大量的命令类可供调用，代码的复用性很好。

