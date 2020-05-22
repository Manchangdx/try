# 工厂模式

这块儿应该需要一个比较完整的背景环境，才能比较好地理解。

先写个例子吧，回头再补充。

```python
class Burger():

    name = ""
    price = 0.0

    def getPrice(self):
        return self.price

    def setPrice(self,price):
        self.price=price

    def getName(self):
        return self.name


class CheeseBurger(Burger):

    def __init__(self):
        self.name = '芝士汉堡'
        self.price = 10


class ChickenBurger(Burger):

    def __init__(self):
        self.name = '鸡肉汉堡'
        self.price = 15


class Snack():
    '''小食抽象类'''

    name = ""
    price = 0.0
    type = "SNACK"

    def getPrice(self):
        return self.price

    def setPrice(self, price):
        self.price = price

    def getName(self):
        return self.name


class Chips(Snack):

    def __init__(self):
        self.name = "薯条"
        self.price = 6


class ChickenWings(Snack):

    def __init__(self):
        self.name = "鸡翅"
        self.price = 12


class Beverage():
    '''饮料抽象类'''

    name = ""
    price = 0.0
    type = "BEVERAGE"

    def getPrice(self):
        return self.price

    def setPrice(self, price):
        self.price = price

    def getName(self):
        return self.name


class Coke(Beverage):

    def __init__(self):
        self.name = "可乐"
        self.price = 4


class Milk(Beverage):

    def __init__(self):
        self.name = "牛奶"
        self.price = 5


class FoodFactory():
    '''食物工厂抽象类'''

    type = ""

    def create_food(self, food_class):
        print(self.type, "factory produce a instance.")
        foodIns = food_class()
        return foodIns


class BurgerFactory(FoodFactory):
    '''主食工厂类'''

    def __init__(self):
        self.type = "BURGER"


class SnackFactory(FoodFactory):
    '''小食工厂类'''

    def __init__(self):
        self.type = "SNACK"


class BeverageFactory(FoodFactory):
    '''饮料工厂类'''

    def __init__(self):
        self.type = "BEVERAGE"


# 创建仨工厂类的实例，这仨实例都有 create_food 方法
# 这个方法把食物类作为参数，返回食物类的实例
burger_factory = BurgerFactory()        # 主食工厂实例
snack_factorry = SnackFactory()         # 小食工厂实例
beverage_factory = BeverageFactory()    # 饮料工厂实例


if  __name__ == "__main__":
    cheese_burger = burger_factory.create_food(CheeseBurger)
    print(cheese_burger.getName(), cheese_burger.getPrice())
    chicken_wings = snack_factorry.create_food(ChickenWings)
    print(chicken_wings.getName(), chicken_wings.getPrice())
    coke_drink = beverage_factory.create_food(Coke)
    print(coke_drink.getName(), coke_drink.getPrice())
```

