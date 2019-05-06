---
show: step
version: 1.0
---

# Scrapy 爬取实验楼用户数据

## 简介

本节内容运用前两节学到的知识，爬取实验楼的用户数据，主要是为了练习、巩固前面学习到的知识。

#### 知识点

- Scrapy 项目框架
- 分析网页元素字段
- SQLAlchemy 定义数据模型
- 创建 Item
- 解析数据

## 要爬取的内容

下面是一个用户主页的截图，箭头指的是我们要爬取的内容：

![此处输入图片的描述](https://doc.shiyanlou.com/document-uid1labid3981timestamp1511830192301.png/wm)


要爬取的内容和字段名称定义：

- 用户名 (name)
- 类型：普通用户／会员用户 (is_vip)
- 加入实验楼的时间 (join_date)
- 楼层数 (level)
- 状态：在职／学生 (status)
- 学校/职位 (school_job)
- 学习记录 (study_record)


## 定义数据模型

**注意：本节实验的操作需要使用上一节 scrapy 创建的 shiyanlou 项目的代码，代码目录为 /home/shiyanlou/Code/shiyanlou**

决定好了要爬取的内容，就可以使用 SQLAlchemy 定义数据模型了，在上一节实验中创建的 `/home/shiyanlou/Code/shiyanlou/shiyanlou/models.py` 中的 `Course` 后面定义 `User` 模型：

```py
# User 表用到新类型要引入
from sqlalchemy import Date, Boolean

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    # 用户类型有普通用户和会员用户两种，我们用布尔值字段来存储
    # 如果是会员用户，该字段的值为 True ，否则为 False
    # 这里需要设置字段的默认值为 False 
    is_vip = Column(Boolean, default=False)
    status = Column(String(64), index=True)
    school_job = Column(String(64))
    level = Column(Integer, index=True)
    join_date = Column(Date)
    learn_courses_num = Column(Integer)
```

现在可以运行脚本在数据库中创建 `users` 表了： 

```
python3 models.py
```

`SQLAlchemy` 默认不会重新创建已经存在的表，所以不用担心 `create_all` 会重新创建 `course` 表造成数据丢失。

定义数据模型操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-3-1-tvusb.mp4
@`

```checker
- name: 检查 models.py 文件中是否定义了 User 类
  script: |
    #!/bin/bash
    grep User /home/shiyanlou/Code/shiyanlou/shiyanlou/models.py
  error:
    我们发现您还没有在 /home/shiyanlou/Code/shiyanlou/shiyanlou/models.py 文件中定义 User 类
```

## 创建 Item

在 `/home/shiyanlou/Code/shiyanlou/shiyanlou/items.py` 中添加 `UserItem`，为每个要爬取的字段声明一个 `Field`:

```py
class UserItem(scrapy.Item):
    name = scrapy.Field()
    is_vip = scrapy.Field()
    status = scrapy.Field()
    school_job = scrapy.Field()
    level = scrapy.Field()
    join_date = scrapy.Field()
    learn_courses_num = scrapy.Field()
```

```checker
- name: 检查在 items.py 文件中是否定义了 UserItem 类
  script: |
    #!/bin/bash
    grep UserItem /home/shiyanlou/Code/shiyanlou/shiyanlou/items.py
  error:
    我们发现您还没有在 /home/shiyanlou/Code/shiyanlou/shiyanlou/items.py 中定义 UserItem 类
```

## 创建爬虫

使用 `genspider` 命令创建 `users` 爬虫：

```
cd /home/shiyanlou/Code/shiyanlou/shiyanlou/
scrapy genspider users shiyanlou.com
```

scrapy 为我们在 `spiders` 下面创建 `users.py` 爬虫，将它修改如下：

```py
import scrapy

class UsersSpider(scrapy.Spider):
    name = 'users'

    @property
    def start_urls(self):
        """ 
        实验楼注册的用户数目前大约六十几万，为了爬虫的效率，
        取 id 在 524,800~525,000 之间的新用户，
        每间隔 10 取一个，最后大概爬取 20 个用户的数据
        """
        url_tmp = 'https://www.shiyanlou.com/users/{}/'
        return (url_tmp.format(i) for i in range(525000, 524800, -10))

```

爬虫及 Item 实现视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-3-2-tvusb.mp4
@`

```checker
- name: 检查是否创建了 users.py 文件
  script: |
    #!/bin/bash
    ls -l /home/shiyanlou/Code/shiyanlou/shiyanlou/spiders | grep users.py
  error:
    我们发现您还没有使用 scrapy 创建 /home/shiyanlou/Code/shiyanlou/shiyanlou/spiders/users.py 文件
```

## 解析数据

解析数据主要是编写 `parse` 函数。在实际编写前，最好是用 `scrapy shell` 对某一个用户进行测试，将正确的提取代码复制到 parse 函数中。

下面的几个例子是 “需要提取的某用户数据在页面源码中的结构” 和对应的提取器（提取器有很多种写法，可以用自己的方式去写）


```html
# 以下为用户页面部分源码

<div class="user-meta" data-v-22a7bf90>
  <span data-v-22a7bf90>
        幺幺哒
  </span> 
  <span data-v-22a7bf90>
        L2282
  </span> 
  <!----> 
  <!---->
</div> 
<div data-v-1b7bcd86 data-v-22a7bf90>
  <div class="user-status" data-v-1b7bcd86>
    <span data-v-1b7bcd86>
      学生
    </span> 
    <span data-v-1b7bcd86>
      格瑞魔法学校
    </span>
  </div>
</div> 
<span class="user-join-date" data-v-22a7bf90>
      2016-11-10 加入实验楼
</span>
```

```python
# name
# 提取结果为字符串，strip 方法去掉前后的空白字符
# 空白字符包括空格和换行符
response.css('div.user-meta span::text').extract()[0].strip()

# level
# 注意提取结果的第一个字符是 L
response.css('div.user-meta span::text').extract()[1].strip()

# status
# 该字段为用户个人信息，如果用户未设置，提取不到数据
# 这种情况将其设为“无”
response.css('div.user-status span::text').extract_first(default='无').strip()

# school_job
# 该字段同上，这里需要使用 xpath 提取器
response.xpath('//div[@class="user-status"]/span[2]/text()').extract_first(default='无').strip()

# learn_courses_num 
# 使用正则表达式来提取数字部分
# \D+ 匹配多个非数字字符，\d+ 匹配多个数字字符
# 大家可以尝试使用同样的方法修改 level 提取器的写法
response.css('span.tab-item::text').re_first('\D+(\d+)\D+')
```

如下图所示，会员用户头像右下角有一个会员标志，它是一张图片。在 div 标签下，非会员用户只有一个 img 标签在 a 标签内部，会员用户有两个 img 标签，我们可以根据 img 的数量来判断用户类型：

![图片描述](https://doc.shiyanlou.com/courses/uid310176-20190502-1556777018758)

```py
if len(response.css('div.user-avatar img').extract()) == 2:
    item['is_vip'] = True
```

依次在 scrapy shell 中测试每个要爬取的数据，最后将代码整合进 `users.py` 中如下：

```py
import scrapy
from ..items import UserItem


class UsersSpider(scrapy.Spider):
    name = 'users'
    allowed_domains = ['shiyanlou.com']

    @property
    def start_urls(self):
        url_temp = 'https://www.shiyanlou.com/users/{}'
        return (url_temp.format(i) for i in range(310176, 310000, -10))

    def parse(self, response):
        item = UserItem(
            name = response.css('div.user-meta span::text').extract()[0].strip(),
            level = response.css('div.user-meta span::text').extract()[1].strip(),
            status = response.css('div.user-status span::text').extract_first(default='无').strip(),
            school_job = response.xpath('//div[@class="user-status"]/span[2]/text()').extract_first(default='无').strip(),
            join_date = response.css('span.user-join-date::text').extract_first().strip(),
            learn_courses_num = response.css('span.tab-item::text').re_first('\D+(\d+)\D+')
        )
        if len(response.css('div.user-avatar img').extract()) == 2:
            item['is_vip'] = True

        yield item
```

数据解析操作视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-3-3-tvusb.mp4
@`

```checker
- name: 检查 users.py 文件中是否定义了 parse 函数
  script: |
    #!/bin/bash
    grep parse /home/shiyanlou/Code/shiyanlou/shiyanlou/spiders/users.py
  error:
    我们发现您还没有在 users.py 中定义 parse 函数 
```

## pipeline

因为 pipeline 会作用在每个 item 上，当和课程爬虫共存时候，需要根据 item 类型使用不同的处理函数。

最终代码文件 `/home/shiyanlou/Code/shiyanlou/shiyanlou/pipelines.py`：

```py
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from shiyanlou.models import Course, User, engine
from shiyanlou.items import CourseItem, UserItem


class ShiyanlouPipeline(object):

    def process_item(self, item, spider):
        """ 对不同的 item 使用不同的处理函数
        """
        if isinstance(item, CourseItem):
            self._process_course_item(item)
        else:
            self._process_user_item(item)
        return item

    def _process_course_item(self, item):
        item['students'] = int(item['students'])
        self.session.add(Course(**item))

    def _process_user_item(self, item):
        # 抓取到的数据类似 'L100'，需要去掉 'L' 然后转化为 int
        item['level'] = int(item['level'][1:])
        # 抓取到的数据类似 '2017-01-01 加入实验楼'，把其中的日期字符串转换为 date 对象
        item['join_date'] = datetime.strptime(item['join_date'].split()[0], '%Y-%m-%d')
        # 学习课程数目转化为 int
        item['learn_courses_num'] = int(item['learn_courses_num'])
        # 添加到 session
        self.session.add(User(**item))

    def open_spider(self, spider):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()

```

pipeline 实现视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-3-4-tvusb.mp4
@`


```checker
- name: 检查 pipelines.py 中是否定义了 open_spider 函数
  script: |
    #!/bin/bash
    grep open_spider /home/shiyanlou/Code/shiyanlou/shiyanlou/pipelines.py
  error:
    我们发现您还没有在 pipelines.py 中定义 open_spider 函数
- name: 检查 pipelines.py 中是否定义了 close_spider 函数
  script: |
    #!/bin/bash
    grep close_spider /home/shiyanlou/Code/shiyanlou/shiyanlou/pipelines.py
  error:
    我们发现您还没有在 pipelines.py 中定义 close_spider 函数
```


## 运行

使用 `crawl` 命令启动爬虫：

```
cd /home/shiyanlou/Code/shiyanlou/shiyanlou/
scrapy crawl users
```

爬虫运行及结果查看视频：

`@
https://labfile.oss.aliyuncs.com/courses/923/week3/3-3-5-tvusb.mp4
@`

## 总结

实验设计了一个新的实例，爬取实验楼的用户页面，在这个页面中首先需要分析页面中的各种元素，从而设计爬虫中数据提取的方式。然后把需要的数据内容通过 Scrapy 项目中的代码获取得到并解析出来，存储到数据库中。

本节实验包含以下的知识点：

- Scrapy 项目框架
- 分析网页元素字段
- SQLAlchemy 定义数据模型
- 创建 Item
- 解析数据

