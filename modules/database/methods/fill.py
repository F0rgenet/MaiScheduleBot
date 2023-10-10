from modules.database import create_group
from modules.parser import parse_groups


async def fill_groups():
    for group in await parse_groups():
        await create_group(group)
