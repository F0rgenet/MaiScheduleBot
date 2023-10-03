from sqlalchemy.exc import NoResultFound

from loguru import logger

from ..models import Group, Subject
from .. import Database


async def get_group_info(name: str):
    # М3О-121Б-23
    data = name.split("-")
    area = {"М": "москва", "Т": "таганка", "С": "стрела", "Б": "байконур"}[data[0][0]]
    institute = data[0][1:-1]
    education_form = {"О": "очная", "З": "заочная"}[data[0][-1]]
    course = int(data[1][0])
    course_group = int(data[1][1:-1])
    education_level = {"Б": "бакалавриат", "С": "специалитет"}[data[1][-1]]
    graduation_year = int(f"20{data[2]}")
    return {"area": area, "institute": institute, "education_form": education_form,
            "course": course, "course_group": course_group, "education_level": education_level,
            "enter_year": graduation_year}


async def create_group(name: str):
    session = Database().session
    try:
        session.query(Group.id).filter(Group.name == name).one()
    except NoResultFound:
        logger.info(f"Создана группа {name}")
        session.add(Group(name=name, **await get_group_info(name)))
    session.commit()
