import asyncio

from asyncchain import ChainMeta


class Chainer(metaclass=ChainMeta):
    async def first(self):
        print("first")


if __name__ == "__main__":
    chainer = Chainer()

    async def caller():
        task = asyncio.create_task(chainer.first())
        await task

    asyncio.run(caller())
