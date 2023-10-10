from sqlalchemy.exc import NoResultFound
from loguru import logger

from datetime import datetime
from modules.database.utils import get_group_info

from ..models import Group, Subject
from .. import Database


# noinspection PyArgumentList
async def create_group(name: str):
    # noinspection PyArgumentList
    session = Database().session
    try:
        session.query(Group.id).filter(Group.name == name).one()
    except NoResultFound:
        group_info = await get_group_info(name)
        if group_info:
            logger.info(f"Создана группа: {name}")
            session.add(Group(name=name, **group_info))
        else:
            logger.error(f"Не удалось создать группу: {name}")
    session.commit()


# noinspection PyArgumentList
async def create_subject(group_name: str, name: str, category: str,
                         audience: str, professor: str, week: int, start_time: datetime, end_time: datetime):
    session = Database().session
    try:
        session.query(Subject.id).filter(Subject.start_time == start_time).one()
    except NoResultFound:
        session.add(Subject(group_name=group_name, name=name, category=category, audience=audience, professor=professor,
                            week=week, start_time=start_time, end_time=end_time))
        logger.info(f"Создан предмет {name} для недели {week}")
    session.commit()
