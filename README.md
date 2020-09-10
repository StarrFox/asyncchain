# asyncchain
Small python library to allow "async chaining"


## Usage
```py
import asyncio

from asyncchain import ChainMeta


class Target(metaclass=ChainMeta):
    async def first(self):
        print("first")

    async def second(self):
        print("second")


async def main():
    my_target = Target()

    await my_target.first().second()


if __name__ == "__main__":
    asyncio.run(main())
```
