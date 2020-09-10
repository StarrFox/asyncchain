import asyncio
from typing import Callable


class AsyncChain:
    def __init__(self, instance, callback: Callable):
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(f"callback needs to be a coroutine function, not {type(callback)!r}")

        self.instance = instance
        self.callback = callback

        self.coros = []

    def __call__(self, *args, **kwargs):
        self.coros.append(self.callback(*args, **kwargs))
        return self

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            res = object.__getattribute__(self.instance, name)

        if isinstance(res, type(self)):
            res.coros.extend(self.coros)
            return res

        else:
            return res

    async def execute_coros(self):
        for coro in self.coros:
            await coro

    def __await__(self):
        return self.execute_coros().__await__()


class ChainMeta(type):
    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, *args, **kwargs)

        old_init = new_class.__init__

        def wrapped(*args, **kwargs):
            new_instance = args[0]
            old_init(*args, **kwargs)
            for attr in dir(new_instance):
                item = getattr(new_instance, attr)
                if asyncio.iscoroutinefunction(item):
                    setattr(new_instance, attr, AsyncChain(new_instance, item))

        new_class.__init__ = wrapped

        return new_class
