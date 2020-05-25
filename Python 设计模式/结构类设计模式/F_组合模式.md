## 组合模式

什么是组合模式？按照定义来说，组合模式是将对象组合成树形结构表示，使得客户端对单个对象和组合对象的使用具有一致性。组合模式的使用通常会生成一颗对象树，对象树中的叶子结点代表单个对象，其他节点代表组合对象。调用某一组合对象的方法，其实会迭代调用所有其叶子对象的方法。

使用组合模式的经典例子是 Linux  系统内的树形菜单和文件系统。在树形菜单中，每一项菜单可能是一个组合对象，其包含了菜单项和子菜单，这样就形成了一棵对象树。在文件系统中，叶子对象就是文件，而文件夹就是组合对象，文件夹可以包含文件夹和文件，同样又形成了一棵对象树。同样的例子还有员工和领导之间的关系，下面就让我们实现下吧。

#### 第 1 步

在整个树形结构里，每个结点都是工作者，领导和员工都要工作。首先实现一个抽象基类 Worker ，领导类和员工类都要继承此类。

该类的所有子类都要实现 work 方法，代码如下：

```python
import abc


class Worker:
    """
    工作者抽象类
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def work(self):
        pass
```

#### 第 2 步

实现员工类和领导类，领导拥有额外的功能：添加和删除员工实例：

```python
class Employee(Worker):
    """
    员工类
    """

    def work(self):
        print("Employee: %s start to work " % self.name)


class Leader(Worker):
    """
    领导类
    """

    def __init__(self, name):
        super().__init__(name)
        self.members = []

    def add_member(self, employee):
        if employee not in self.members:
            self.members.append(employee)

    def remove_member(self, employee):
        if employee in self.members:
            self.members.remove(employee)

    def work(self):
        print("Leader: %s start to work" % self.name)
        for employee in self.members:
            employee.work()
```

#### 第 3 步

创建实例，测试功能：

```python
if __name__ == '__main__':
    employee_1 = Employee("employee_1")     # 创建 1 号员工
    employee_2 = Employee("employee_2")     # 创建 2 号员工
    leader_1 = Leader("leader_1")           # 创建 1 号领导
    leader_1.add_member(employee_1)         # 1 号领导添加 1 号员工
    leader_1.add_member(employee_2)         # 1 号领导添加 2 号员工

    employee_3 = Employee("employee_3")     # 创建 3 号员工
    leader_2 = Leader("leader_2")           # 创建 2 号领导
    leader_2.add_member(employee_3)         # 2 号领导添加 3 号员工
    leader_2.add_member(leader_1)           # 2 号领导添加 1 号领导

    leader_2.work()                         # 2 号领导调用 work 方法
```

运行结果如下：

```python
Leader: leader_2 start to work
Employee: employee_3 start to work
Leader: leader_1 start to work
Employee: employee_1 start to work
Employee: employee_2 start to work
```

在以上的代码中，雇员和领导都属于员工，都会实现`Worker.work()`方法，只要执行了该方法就代表这个员工开始工作了。我们也注意到一个领导名下，可能有多个次级领导和其他雇员，如果一个领导开始工作，那这些次级领导和雇员都需要开工。员工和领导组成了一个对象树，领导是组合对象，员工是叶子对象。还可以看到 `Leader`类通常会实现类似于`Leader.add_member`的方法来用于添加另一个组合对象或者是叶子对象，并且调用组合对象的`Leader.work`方法会遍历调用（通过迭代器）其子对象`work`方法。客户端使用组合模式实现的对象时，不必关心自己处理的是单个对象还是组合对象，降低了客户端的使用难度，降低了耦合性。

在最后的测试代码中，我们首先创建了2个雇员: `employe_1, employe_2` 和1个领导`leader_1`， 前2个雇员被后一个领导管理。接着我们又创建了第3个雇员`employe_3`，和第2个领导`leader_2`，其中 `leader_2`是大领导，他管理`employe_3`和`leader_1`。这些员工形成的对象树如下图所示：

![](https://doc.shiyanlou.com/document-uid5348labid1129timestamp1436418866901.png)

