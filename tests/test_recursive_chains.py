import asyncio

from asyncchain import ChainMeta


class Target(metaclass=ChainMeta):
    async def first(self):
        print("one")

    async def second(self):
        print("calling one")
        await self.first()
        print("called one")
        print("two")


async def main():
    my_target = Target()

    await my_target.first().second()


if __name__ == "__main__":
    asyncio.run(main())
