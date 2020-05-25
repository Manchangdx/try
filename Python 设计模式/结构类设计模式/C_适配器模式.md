## 适配器模式

何为适配器？你买过水货电子产品吗？假如你是买的港行的电子产品，那么其电源插头是香港标准的，在大陆不能直接使用。一般情况下，商家会附赠一个转换插头。你把电子产品的电源插头插在转换插头上，然后转换插头插上电源，电子产品就能正常工作了。这就是适配器模式。下面让我们看看适配器模式在实验楼中使用吧。

有一些课程是很久以前写的，它们是 OldCourse 类的实例，这些实例有一个 S 方法展示属性。现在的新课使用的实例是由 NewCourse 来创建，这些实例展示属性时用的是 a 、b 和 c 方法。当我们把课程展示到页面的时候，页面只会调用实例的 S 方法，它不知道什么 a 、b 、c 方法。这时候，就需要对新课程的实例进行适配，使得它提供一个 S 方法。

#### 第 1 步

最开始，先要有 OldCourse 旧课类，以及将课程信息展示到页面的 Page 类：

```python
class OldCourse:
    """
    老的课程类
    """

    def show(self):
        """
        显示关于本课程的所有信息
        """
        print("Show description")
        print("Show teacher of course")
        print("Show labs")


class Page:
    """
    使用课程对象的客户端
    """

    def __init__(self, course):
        self.course = course

    def render(self):
        self.course.show()
```

旧的课程有一个 show 方法提供课程信息，Page 类的实例的 render 方法会调用课程的 show 方法。

#### 第 2 步

新的课程不再提供 show 方法，而是提供多个方法分别展示课程信息：

```python
class NewCourse:
    """
    新的课程类, 为了模块化显示课程信息，实现了新的课程类
    """

    def show_desc(self):
        """
        显示描述信息
        """
        print("Show description")

    def show_teacher(self):
        """
        显示老师信息
        """
        print("Show teacher of course")

    def show_labs(self):
        """
        显示实验
        """
        print("Show labs")
```

#### 第 3 步

新的课程不提供 show 方法，而 Page 的实例必须要用到这个方法，所以我们写一个适配器类，该类将新课程类的实例作为参数创建自身的实例，并提供一个 show 方法：

```python
class Adapter:
    """
    适配器, 尽管实现了新的课程类，但是在很多代码中还是需要使用 OldCourse.show() 方法
    """

    def __init__(self, course):
        self.course = course

    def show(self):
        """
        适配方法，调用真正的操作
        """
        self.course.show_desc()
        self.course.show_teacher()
        self.course.show_labs()
```

#### 第 4 步

创建实例，测试功能：

```python
if __name__ == '__main__':
    old_course = OldCourse()
    page = Page(old_course)
    page.render()
    print('--------------------------------------')
    new_course = NewCourse()
    # 新课程类的实例没有 show 方法，我们需要使用适配器进行适配
    adapter = Adapter(new_course)
    page = Page(adapter)
    page.render()
```

