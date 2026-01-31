class Item:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


def other(x):
    item = Item(x)
    return item.get_value()


def inside(x, y):
    a = other(y)
    return x + y + a


def function(x):
    return inside(x, x)


class A:
    def method(self, y):
        return function(y)


class B:
    def __init__(self, z):
        self.z = z

        class Internal:
            def internal_method(s, w):
                return s.z + w

        self.internal = Internal()

    def internal_method(self, w):
        return self.internal.internal_method(w)

    @staticmethod
    def call(x, y):
        return inside(x, y)


def main():
    a = A()
    result = a.method(10)
    print("Result:", result)


if __name__ == "__main__":
    main()
