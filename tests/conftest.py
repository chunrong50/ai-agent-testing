import pytest



#用于模拟token计算的值
class FakeTokenCounter:
    def __init__(self, token_count):
        self.token_count = token_count

    def count(self, text):
        return self.token_count