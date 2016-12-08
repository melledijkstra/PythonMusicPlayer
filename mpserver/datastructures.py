class Stack:
    """
    Stack is a Last-In/First-Out(LIFO) data structure which represents a stack of objects.
    It enables users to pop to and push from the stack.
    """
    def __init__(self, limit=None):
        if isinstance(limit, int):
            self._limit = limit
        self._items = []

    def isEmpty(self) -> bool:
        return self._items == []

    def push(self, item):
        if self.size() < self._limit:
            self._items.append(item)

    def pop(self) -> object:
        return self._items.pop()

    def peek(self) -> object:
        return self._items[len(self._items) - 1]

    def size(self) -> int:
        return len(self._items)

    def limit(self) -> int:
        return self._limit