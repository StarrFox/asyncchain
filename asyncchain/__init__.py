import asyncio
import warnings
from typing import Callable


class AsyncChain:
    def __init__(
            self,
            instance,
            callback: Callable,
    ):
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(f"callback needs to be a coroutine function, not {type(callback)!r}")

        self.instance = instance
        self.callback = callback

        # self.coros: list[list[tuple[Callable, tuple[tuple, dict]]]] = []
        self.coros = []

    def __call__(self, *args, **kwargs):
        loop = asyncio.get_running_loop()

        def _task_factory(_loop, coro):
            if isinstance(coro, type(self)):
                return asyncio.Task(coro.execute_coros(), loop=_loop)

            else:
                return asyncio.Task(coro, loop=_loop)

        current_factory = loop.get_task_factory()
        if current_factory is None:
            loop.set_task_factory(_task_factory)

        # elif current_factory != _task_factory:
        #     warnings.warn("task_factory set elseware, chains will not be able to be create_tasked")

        self.coros.append((self.callback, (args, kwargs)))
        return self

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self.instance, name)

    async def execute_coros(self) -> list:
        res = []

        coro, args = self.coros.pop(0)

        res.append(await coro(*args[0], **args[1]))

        if len(res) == 1:
            return res[0]

        return res

    def __await__(self):
        return self.execute_coros().__await__()


class ChainMeta(type):
    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, *args, **kwargs)

        old_init = new_class.__init__

        def wrapped(*wrapped_args, **wrapped_kwargs):
            new_instance = wrapped_args[0]
            old_init(*wrapped_args, **wrapped_kwargs)
            for attr in dir(new_instance):
                item = getattr(new_instance, attr)
                if asyncio.iscoroutinefunction(item):
                    setattr(new_instance, attr, AsyncChain(new_instance, item))

        new_class.__init__ = wrapped

        return new_class
