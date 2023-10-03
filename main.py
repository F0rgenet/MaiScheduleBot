from modules.database import create_group, register_models
import asyncio


async def main():
    register_models()
    await create_group("М3О-121Б-23")


if __name__ == "__main__":
    asyncio.run(main())
