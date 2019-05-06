---
show: step
version: 1.0
---

# Scrapy 爬取实验楼课程信息

## 介绍

`Scrapy`  是使用 Python 实现的一个开源爬虫框架。秉承着 “Don’t Repeat Yourself” 的原则，`Scrapy` 提供了一套编写爬虫的基础框架和编写过程中常见问题的一些解决方案。`Scrapy` 主要拥有下面这些功能和特点：

- 内置数据提取器（Selector），支持XPath 和 Scrapy 自己的 CSS Selector 语法，并且支持正则表达式，方便从网页提取信息。
- 交互式的命令行工具，方便测试 Selector 和 debugging 爬虫。
- 支持将数据导出为 JSON，CSV，XML 格式。
- 内置了很多拓展和中间件用于处理：
	- cookies 和 session
	- HTTP 的压缩，认证，缓存
	- robots.txt
	- 爬虫深度限制
- 可拓展性强，可运行自己编写的特定功能的插件

除了列出的这些，还有很多小功能，比如内置的文件、图片下载器等等。另外，Scrapy 基于 twisted 这个高性能的事件驱动网络引擎框架，也就是说，Scrapy 爬虫拥有很高的性能。

下面的内容我们来实现一个爬取实验楼所有课程信息的爬虫。

#### 本周脑图

Scrapy 是一个非常容易上手的成熟的爬虫框架，为了帮助大家梳理架构细节和常用命令，我们整理了一份脑图包含了 Scrapy 爬虫框架的基础知识。这份脑图大家可以在本周每个实验中都能去进行对照学习，让动手实践过程中学习到的知识点建立更加清晰的体系。

请点击以下链接进行访问：

* [Scrapy 爬虫基础知识点脑图](http://naotu.baidu.com/file/dd56a350fe7be1d871103ffea6d4ea54?token=dbdf171ff27dee77)

请注意实验只会包含常用的知识点，对于未涉及到的知识点，如果在脑图中看到可以查看 Scrapy 官方文档获得详细说明，也非常欢迎在讨论组里与同学和助教进行讨论，技术交流也是学习成长的必经之路。

Scrapy 爬虫基础知识点脑图制作过程中参考了以下文档：

* [Scrapy 官方文档](https://scrapy-chs.readthedocs.io/zh_CN/0.24/intro/tutorial.html)
* [ZOE 的 Scrapy 脑图](https://woaielf.github.io/2018/04/28/scrappy/)

#### 知识点

- scrapy 爬虫框架介绍
- scrapy 框架安装
- 数据提取器：CSS 和 XPATH
- scrapy shell
- 正则表达式数据提取
- start_urls

## 安装

为了方便管理 Python 版本和依赖包，首先在 `/home/shiyanlou/Code` 目录下创建一个 python3.5 的虚拟环境（实验环境已经安装了 virtualenv）：

```
virtualenv -p python3.5 venv
```

激活环境：

```
. venv/bin/activate
```

后面的 scrapy 爬虫实验都基于这个虚拟环境。

在虚拟环境中安装 `scrapy`:

```sh
pip install scrapy
```

注意，在虚拟环境中，pip 就是基于 Python3.5 的包管理工具，命令前面不要加 sudo 。

现在在命令行输入 `scrapy`，出现下面的内容说明已经安装成功了。

```
Scrapy 1.4.0 - no active project

Usage:
  scrapy <command> [options] [args]

Available commands:
  bench         Run quick benchmark test
  fetch         Fetch a URL using the Scrapy downloader
  genspider     Generate new spider using pre-defined templates
  runspider     Run a self-contained spider (without creating a project)
  settings      Get settings values
  shell         Interactive scraping console
  startproject  Create new project
  version       Print Scrapy version
  view          Open URL in browser, as seen by Scrapy

  [ more ]      More commands available when run from project directory

Use "scrapy <command> -h" to see more info about a command
```

从中我们也可以看到 `scrapy` 提供的命令行命令和它的功能简介。

Scrapy 安装操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-1-tvusb.mp4
@`

## 数据提取器

在开始编写爬虫前，我们先来学习一下 `scrapy` 的数据提取器（Selector），因为爬虫的本质就是为了获取数据，所以在编写爬虫的过程中需要编写很多数据提取的代码。

`scrapy` 内置两种数据提取语法： `CSS` 和 `XPath` 。下面通过例子来看看怎么使用，有这样一个 HTML 文件：

```html
<html>
 <head>
  <base href='http://example.com/' />
  <title>Example website</title>
 </head>
 <body>
  <div id='images'>
   <a href='image1.html'>Name: My image 1 <br /><img src='image1_thumb.jpg' /></a>
   <a href='image2.html'>Name: My image 2 <br /><img src='image2_thumb.jpg' /></a>
   <a href='image3.html'>Name: My image 3 <br /><img src='image3_thumb.jpg' /></a>
   <a href='image4.html'>Name: My image 4 <br /><img src='image4_thumb.jpg' /></a>
   <a href='image5.html'>Name: My image 5 <br /><img src='image5_thumb.jpg' /></a>
  </div>
 </body>
</html>
```

这是 `scrapy` 官方提供的一个网页，方便我们练习 `Selector`，它的地址是

``` 
http://labfile.oss.aliyuncs.com/courses/923/selectors-sample1.html
```

### scrapy shell

 `scrapy shell` 提供了一个交互式的 Python 环境方便我们测试和debug 爬虫，使用方法是

```sh
scrapy shell [url]
```

需要提供一个网页的 url，执行命令后，scrapy 会自动去下载这个 url 对应的网页，将结果封装为 `scrapy` 内部的一个 `response` 对象并注入到 python shell 中，在这个 `response` 对象上，可以直接使用 scrapy 内置的css 和 xpath 数据提取器。

运行下面的命令下载上面的网页并进入 `shell`：

```sh
scrapy shell http://labfile.oss.aliyuncs.com/courses/923/selectors-sample1.html
```

对于网页的源代码分析，推荐使用 Chrome 浏览器，在页面上的元素右键选择 `检查` 可以得到源代码，在源代码上可以拷贝出 xpath 路径。

### CSS Selector

顾名思义，css selector 就是 css 的语法来定位标签。例如要提取例子网页中 ID 为 `images` 的 div 下所有 a 标签的文本，使用 css 语法可以这样写：

```py
>>> response.css('div#images a::text').extract()
['Name: My image 1 ', 'Name: My image 2 ', 'Name: My image 3 ', 'Name: My image 4 ', 'Name: My image 5 ']
```

网页的 HTML 源码是由各种各样不同的标签组成，一个标签可以有很多属性，每个属性可以有很多属性值，属性值在源码中表现为由空格分隔的字符串，例如：`<a class="one two three" href="front.index">首页</a>` , 这是一个完整的标签，标签名为 a ，它有两个属性 class 和 href，其中 class 属性有三个属性值：one、two、three，class 又称为类属性，“首页” 二字就是标签的 text 值，也叫做标签文本。

在 CSS 提取器中，`div#images` 表示 id 属性的值为 images 的 div 标签，如果是类属性的值为 images，这里就写成 `div.images`。`div a` 表示 div 标签下所有的 a 标签，`::text` 表示提取文本，`extract` 方法执行提取操作，返回一个**列表**。如果只想要列表中第一个 a 标签下的文本，可以使用 `extract_first` 方法：

```py
>>> response.css('div#images a::text').extract_first()
'Name: My image 1 '
```

`extract_first()` 方法支持对没有匹配到的元素提供一个默认值：

```py
>>> response.css('div#images p::text').extract_first(default='默认值')
'默认值'
```

`div#images` 下面并没有 p 标签，所以会返回提供的默认值。如果不提供 default 值的话会返回 None。

如果要提取所有 a 标签的 href 链接，可以这样写：

```py
>>> response.css('div#images a::attr(href)').extract()
['image1.html', 'image2.html', 'image3.html', 'image4.html', 'image5.html']
```

不只是 `href`，任何标签的任意属性都可以用 `attr()` 提取。基于上面的知识，就能轻松写出提取所有图片的链接地址：

```py
>>> response.css('div#images a img::attr(src)').extract()
['image1_thumb.jpg', 'image2_thumb.jpg', 'image3_thumb.jpg', 'image4_thumb.jpg', 'image5_thumb.jpg']
```

如果 div 标签中的 class 属性有多个属性值，用 css 提取器可以写为 `div[class="r1 r2 r3"]` 或者 `div.r1.r2.r3` 

CSS Selector 操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-2-tvusb.mp4
@`

### XPath

XPath (XML Path Language) 是一门路径提取语言，最初被设计用来从 XML  文档中提取部分信息，现在它的这套提取方法也可以用于 HTML 文档上。

下面我们通过一个例子来看看这些规则的用法。

假设有下面这样一份 HTML 文档，它列出了一些世界知名的 IT 公司及其相关信息，将这份文档保存为 `example.html`。

```html
<!DOCTYPE html>
<html>
<head>
  <title>xpath</title>
</head>
<body>
  <div class="companies">
    <div class="company">
      <h2>阿里巴巴</h2>
      <a href="alibaba.com"><img src="alibaba.jpg"></a>
      <p class="location">杭州</p>
    </div>
    <div class="company">
      <h2>腾讯</h2>
      <a href="qq.com"><img src="qq.jpg"></a>
      <p class="location">深圳</p>
    </div>
    <div class="company">
      <h2>Facebook</h2>
      <a href="facebook.com"><img src="facebook.jpg"></a>
      <p class="location">硅谷</p>
    </div>
    <div class="company">
      <h2>微软</h2>
      <a href="microsoft.com"><img src="microsoft.jpg"></a>
      <p class="location">西雅图</p>
    </div>
  </div>
</body>
</html>
```

在使用 xpath 前，大家首先要把几个概念弄明白。首先，什么是 `节点(node)`，以上面的文档为例子，每个标签都是一个节点：

```html
<div class="company">
  <h2>腾讯</h2>
	<img src="tencent.jpg">
  <p class="location">深圳</p>
</div>
```

这里最外层的 div 是整个文档的一个子节点，里面包含的公司信息标签都是 div 的子节点，节点标签之间的内容称为这个节点的文本(text)，如 `腾讯` 是 `h2` 标签的文本。节点标签内部称为节点的属性(attribute)，如 `src` 是 `img` 标签的一个属性，每个标签都可以有 `class` 属性。每个属性都有一个或多个对应的值（class 属性可以有多个值）。那么爬虫的主要目的其实就是从一个文档中获取需要的文本或者属性的值。

可以使用实验环境右侧工具栏中的剪切板将上面的 HTML 文本复制粘贴到实验环境中，注意剪切板只支持二进制文本的复制，中文会变成问号，粘贴到文件里面之后需要自己手动修改一下。
进入 `scrapy shell` ，由于没有下载链接，我们将 `example.html` 文档手动构建成 `response` 对象，然后就可以在 `response` 对象上直接使用 `xpath` 方法了：

```py
>>> from scrapy.http import HtmlResponse
# body 的数据类型是字符串
>>> body = open('example.html').read()  
# HtmlResponse 接收两个参数，url 为自定义的网址
# body 参数的值应为字节码，所以需要使用字符串的 encode 方法进行编码
>>> response = HtmlResponse(url='http://example.com', body=body.encode('utf-8'))
```

节点选择的基本规则如下：

| 表达式 | 描述 |
| ---- | ---- |
| nodename | 选取此节点的所有子节点。|
| /	| 从根节点选取。|
| // | 从匹配选择的当前节点选择文档中的节点，而不考虑它们的位置。|
| .  | 选取当前节点。|
| .. | 选取当前节点的父节点。|

`/` 表示从根节点开始选取，比如，你想要选取 `title` 节点，就需要按标签的阶级关系来定位：

```py
>>> response.xpath('/html/head/title').extract()
['<title>xpath</title>']
```

而使用 `//` 就可以不必管标签在文档中的位置：

```py
>>> response.xpath('//title').extract()
['<title>xpath</title>']
>>> response.xpath('//h2').extract()
```

同 CSS 提取器的方法类似，extract 会返回一个列表，比如我们选取所有公司的名称所在的 `h2` 标签：

```py
>>> response.xpath("//h2").extract()
["<h2>阿里巴巴</h2>", "<h2>腾讯</h2>", "<h2>Facebook</h2>", "<h2>微软</h2>"]
```

可以在选择表达式后面加上 `text()` 来指定只返回文本：

```py
>>> response.xpath('//h2/text()').extract()
['阿里巴巴', '腾讯', 'Facebook', '微软']
```

而如果想要选取属性值，在属性名称前面加上 *@* 符号就可以了，比如我们选取所有 `img` 的 `src` 属性：

```py
>>> response.xpath('//img/@src').extract()
['alibaba.jpg', 'qq.jpg', 'facebook.jpg', 'microsoft.jpg']
```

我们同样可以用属性来定位节点，比如我们要选取所有 `class` 属性值为 `location` 的 `p`内的文本：

```py
>>> response.xpath('//p[@class="location"]/text()').extract()
['杭州', '深圳', '硅谷', '西雅图']
```

在节点名称后面加上 `[n]` ，n 是一个数字，这样可以获取到该节点下某个子节点的第 n 个，比如我们要获取 `div.companies` 下的第二个 `div` 子 节点，也就是腾讯所在的 `div` 节点，那么可以这样写：

```py
>>> response.xpath("//div[@class='companies']/div[2]")
[<Selector xpath="//div[@class='companies']/div[2]" data='<div class="company">\n      <h2>腾讯</h2>\n'>]
```

scrapy 中，对 xpath 方法选取到的对象可以进一步运用 xpath 方法，比如上一步中，我们获取到了腾讯所在的 div 标签，现在我们想在当前结果基础上进一步获取公司的网址，你可能会写出这样的代码：

```py
>>> response.xpath('//div[@class="companies"]/div[2]').xpath('//a/@href').extract()
['alibaba.com', 'qq.com', 'facebook.com', 'microsoft.com']
```

这时候你发现返回的其实是所有 `a` 标签的 `href`，这是因为 `//` 是基于整个文档来选择的，如果想要基于当前已经选择了的部分运用 xpath 方法，则要在 `//` 前面加上 `.` 号：
```py
>>> response.xpath('//div[@class="companies"]/div[3]').xpath('.//a/@href').extract()
['facebook.com']
```


前面我们说到过，一个标签的属性值可以存在多个，比如 `<div class=“name1 name2 name3”>hello</div>`，这种情况下进行定位的时候，把所有类名都写上就比较麻烦。这时候可以选取一个能唯一代表该 `div` 的类名，假设我们选了 name2，然后可以使用 `contains(@attr, "value")` 方法，该方法表示，只要标签的属性包含指定的值就可以：

```py
>>> response.xpath('//div[contains(@class, "name2")]/text()').extract() 
['hello']
```

XPATH 操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-3-tvusb.mp4
@`


```checker
- name: 检查是否创建 example.html 文件
  script: |
    #!/bin/bash
    ls -l /home/shiyanlou/example.html
  error:
    我们发现您还没有创建文件 /home/shiyanlou/example.html
```

### re 和 re_first 方法

除了 `extract()` 和 `extract_first()`方法， 还有 `re()` 和 `re_first()` 方法可以用于 `css()` 或者 `xpath()` 方法返回的对象。

使用 `extract()` 直接提取的内容可能并不符合格式要求，比如上面的 CSS 提取器例子中，获取的第一个 a 标签的 text 是这样的：`Name: My image 1 `，现在要求不要开头的 `Name:` 和结尾的空格，这时候就可以使用 `re()` 替代 `extract` 方法，使用正则表达式对提取的内容做进一步的处理：

```py
>>> response.css('div#images a::text').re('Name: (.+) ')
['My image 1', 'My image 2', 'My image 3', 'My image 4', 'My image 5']
```

`re()`  方法中定义的正则表达式会作用到每个提取到的文本中，只保留正则表达式中的子模式匹配到的内容，也就是 `()` 内的匹配内容。

`re_first()` 方法支持只作用于第一个文本：

```py
>>> response.css('div#images a::text').re_first('Name: (.+) ')
'My image 1'
```

re 及 re_first 操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-4-tvusb.mp4
@`

## 实战

下面我们使用 `scrapy` 写一个爬虫脚本，爬取实验楼课程页面前 3 页所有课程名称、简介、类型和学习人数信息，并保存为 `JSON` 文本。课程页面的地址是 `https://www.shiyanlou.com/courses/`。

在 `/home/shiyanlou/Code` 下新建 `shiyanlou_courses_spider.py` 文件，写入 `scrapy` 爬虫的基本结构：

```py
# -*- coding:utf-8 -*-
import scrapy

class ShiyanlouCoursesSpider(scrapy.Spider):
    """ 
    使用 scrapy 爬取页面数据需要编写一个爬虫类，该爬虫类要继承 scrapy.Spider 类。在爬虫类中定义要请求的网站和链接、如何从返回的网页提取数据等等。
    在 scrapy 项目中可能会有多个爬虫，name 属性用于标识每个爬虫，各个爬虫类的 name 值不能相同
    """
    name = 'shiyanlou-courses'

    # 注意此方法的方法名字是固定的，不可更改
    def start_requests(self):
        """ 
	    此方法需要返回一个可迭代对象，迭代的元素是 scrapy.Request 对象，可迭代对象可以是一个列表或者迭代器，这样 scrapy 就知道有哪些网页需要爬取了。scrapy.Request 接受一个 url 参数和一个 callback 参数：url 指明要爬取的网页；callback 是一个回调函数，用于处理返回的网页，它的值通常是一个提取数据的 parse 方法。
        """

    # 注意此方法的方法名字也是固定的，不可更改
    def parse(self, response):
        """ 
        这个方法作为 scrapy.Request 的 callback ，在里面编写提取数据的代码。scrapy 中的下载器会下载 start_reqeusts 中定义的每个 Request 并且将结果封装为一个 response 对象传入这个方法。
        """
	    pass 
```

分析实验楼的课程页面可以看出，每页有 4 x 5 行共 20 个课程卡片，我们需要从中提取 20 条数据，爬取前 3 页，共计 60 条数据，点击页面底部的「下一页」按钮进入下一页，将浏览器地址栏中的地址复制出来：

这样就可以写出 `start_requests` 方法：

```py
def start_requests(self):
    # 课程列表页面 URL ，注意此列表中的地址可能有变动，需手动打开页面复制最新地址
    url_list = ['https://www.shiyanlou.com/courses/',
                'https://www.shiyanlou.com/courses/?page_size=20&cursor=bz0yMA%3D%3D',
                'https://www.shiyanlou.com/courses/?page_size=20&cursor=bz00MA%3D%3D']
    # 返回一个生成器，生成 Request 对象，生成器是可迭代对象
    for url in url_list:
        yield scrapy.Request(url=url, callback=self.parse)
```

`scrapy` 内部的下载器会下载每个 `Request`，然后将结果封装为 `response` 对象传入 `parse` 方法，这个对象和前面 scrapy shell 练习中的对象是一样的，也就是说你可以用 `response.css()` 或者 `response.xpath()` 来提取数据了。

通过分析实验楼课程页面的文档结构，以《Linux 入门基础（新版）》课程为例，我们需要提取的数据主要包含在下面的 div 里面：

![图片描述](https://doc.shiyanlou.com/courses/uid310176-20190429-1556520901698)

根据这个 div 可以用提取器写出 parse 方法：

```py
def parse(self, response):
    # 遍历每个课程的 div.col-md-3
    for course in response.css('div.col-md-3'):
        # 使用 css 语法对每个 course 提取数据
        yield {
            # 课程名称，注意这里使用 strip 方法去掉字符串前后的空白字符
            # 所谓空白字符，指的是空格、换行符、制表符
            # 下面获取 name 的写法还可以省略 h6 的类属性，思考一下为什么可以省略
            'name': course.css('h6.course-name::text').extract_first().strip(),
            # 课程描述
            'description': course.css('div.course-description::text').extract_first().strip(),
            # 课程类型
            'type': course.css('span.course-type::text').extract_first().strip(),
            # 学生人数
            'students': course.css('span.students-count span::text').extract_first()
        }
```

```checker
- name: 检查是否创建 shiyanlou_courses_spider.py
  script: |
    #!/bin/bash
    ls -l /home/shiyanlou/Code/shiyanlou_courses_spider.py
  error: 
    我们发现您还没有创建文件 /home/shiyanlou/Code/shiyanlou_courses_spider.py
- name: 检查是否定义了 ShiyanlouCoursesSpider 类
  script: |
    #!/bin/bash
    grep ShiyanlouCoursesSpider /home/shiyanlou/Code/shiyanlou_courses_spider.py
  error: 
    shiyanlou_courses_spider.py 文件中没有定义 ShiyanlouCoursesSpider 类
```

## 运行

按照上一步中的格式写好 spider 后，就能使用 scrapy 的 `runspider` 命令来运行爬虫了。

```sh
scrapy runspider shiyanlou_courses_spider.py -o data.json
```

注意这里输出得到的 `data.json` 文件中的中文显示成 unicode 编码的形式，所以看到感觉像是乱码，其实是正常的。

`-o` 参数表示打开一个文件，scrapy 默认会将结果序列化为 JSON 格式写入其中。爬虫运行完后，在当前目录打开 `data.json` 文件就能看到爬取到的数据了。


实验楼课程爬虫开发视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-5-tvusb.mp4
@`

## start_urls

`scrapy.Spider` 类已经有了一个默认的 `start_requests` 方法，我们的爬虫代码其实可以进一步简化，只提供需要爬取的 `start_urls`，默认的 `start_requests` 方法会根据 `start_urls` 生成 `Request` 对象。所以，代码可以修改为：

```py
import scrapy


class ShiyanlouCoursesSpider(scrapy.Spider):

    name = 'shiyanlou-courses'

    @property
    def start_urls(self):
        """ start_urls  需要返回一个可迭代对象，所以，你可以把它写成一个列表、元组或者生成器，这里用的是列表
        """
        url_list = ['https://www.shiyanlou.com/courses/',
                    'https://www.shiyanlou.com/courses/?page_size=20&cursor=bz0yMA%3D%3D',
                    'https://www.shiyanlou.com/courses/?page_size=20&cursor=bz00MA%3D%3D']
        return url_list

    def parse(self, response):
        for course in response.css('div.col-md-3'):
            yield {
                'name': course.css('h6::text').extract_first().strip(),
                'description': course.css('div.course-description::text').extract_first().strip(),
                'type': course.css('span.course-type::text').extract_first().strip(),
                'students': course.css('span.students-count span::text').extract_first()
            }
```

start_urls 修改代码视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-1-6-tvusb.mp4
@`

## 总结

本节内容介绍了 scrapy 的主要功能，如何使用 scrapy 内置的 css 和 xpath 选择器提取数据，以及如何基于 scrapy 写一个简单的爬虫脚本，运行爬虫，将爬取结果保存为 JSON 数据。

本节实验中涉及到的是 Scrapy 爬虫入门的知识点：

- scrapy 爬虫框架介绍
- scrapy 框架安装
- 数据提取器：CSS 和 XPATH
- scrapy shell
- 正则表达式数据提取
- start_urls


