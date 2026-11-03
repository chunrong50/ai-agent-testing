
# 关于@dataclass需要注意的点
 ## 普通类：

```
class A:
    x = []          # 类属性，可变 → 所有实例共享
    y = "running"   # 类属性，不可变 → 名义上共享，但无法原地修改，安全
```
可变类属性（list/dict/set）：共享，有坑。

不可变类属性（str/int/None/tuple）：名义上也是类属性、所有实例通过类查找拿到同一个对象，但因为不可变，没人能原地改它，所以实际安全。

 ## @dataclass：

``` 
@dataclass
class A:
    x: list = []                      # 直接报错 ValueError
    x: list = field(default_factory=list)   # 正确，每实例独立
    y: str = "running"                # 正确，每实例独立（默认值不可变）
```
可变默认值写 = []：dataclass 在定义类时就抛 ValueError，根本不让你运行，所以不存在"共享"这回事——它被拦住了。

用 field(default_factory=list)：每个实例创建时调用一次 list()，各自独立。

不可变默认值 = "running"：dataclass 生成 __init__ 默认参数，每个实例拿到自己的属性，独立。

**一句话记忆**
普通类：可变类属性 → 共享（坑）；正确做法是写进 __init__。
dataclass：可变默认值 → 直接报错；必须用 default_factory，结果是每实例独立，没有共享问题。
所以"共享"是普通类里可变类属性的问题，不是 dataclass 的字段特性。dataclass 用报错 + default_factory 把这个问题从源头堵住了。