import random
from typing import List, Union

from mpserver.musicmodels import Song


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

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[len(self._items) - 1]

    def size(self) -> int:
        return len(self._items)

    def limit(self) -> int:
        return self._limit

class MusicQueue:
    """
    A music queue which acts like every other MusicQueue
    It keeps a pointer to the current song

    Attributes:
        _pointer    Points to the current index of the queue

    """
    def __init__(self, songs=None): # limit=None, songs=None):
        # if isinstance(limit, int):
        #     self._limit = limit
        self._pointer = 0
        if isinstance(songs, list) and len(songs) > 0:
            self._queue = songs # type: List[Song]
        else:
            self._queue = []

    def add(self, song):
        # if self.size() < self._limit:
            self._queue.append(song)

    def add_next(self, song):
        # TODO: use limit
        self._queue.insert(self._pointer + 1, song)

    def next(self) -> Union[Song, None]:
        if self._pointer + 1 < len(self._queue):
            self._pointer += 1
            return self.current()
        return None

    def previous(self) -> Union[Song, None]:
        if self._pointer - 1 >= 0:
            self._pointer -= 1
            return self.current()
        return None

    def current(self) -> Union[Song, None]:
        if len(self._queue) > 0:
            return self._queue[self._pointer]
        return None

    def size(self) -> int:
        return len(self._queue)

    def shuffle(self):
        # TODO: return random song which hasn't played before
        # When using random it is possible an earlier track gets returned
        self._pointer = random.randrange(0, len(self._queue))
        return self.current()

    def clear(self):
        self._queue.clear()
        self._pointer = 0

    def __repr__(self):
        return str(self._queue)

    def latest(self, song):
        self._queue.append(song)
        self._pointer = len(self._queue)-1
