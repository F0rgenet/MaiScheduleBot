import re
from sqlalchemy.exc import NoResultFound
from xmltodict import parse as xml_parse
from loguru import logger

from pathlib import Path
from ..models import Group, Subject
from .. import Database


async def get_group_info(name: str):
    regex = r"([МТ])(\d{1,2}|[ИУС])([ОЗВ])-(\d)(\d{2})(Бки|БВ|Би|Бк|Б|Мки|Мк|М|Ак|А|СВки|СВк|Ск|СВ|С)-(\d\d)"
    match = re.match(regex, name)

    base_path = Path(__file__).resolve().parent.parent.parent.parent
    with open(f"{base_path}\\misc\\abbreviations.xml", encoding="UTF-8") as abbreviations_file:
        xml = abbreviations_file.read()
    abbreviations = xml_parse(xml)["abbreviations"]

    if not match:
        logger.warning(f"Группа {name} не соответствует заданному стандарту")
        return

    groups = match.groups()
    try:
        area = abbreviations["area"][groups[0]]
        if groups[1] not in abbreviations["department"].keys():
            department = f"Институт №{groups[1]}"
        else:
            department = abbreviations["department"][groups[1]]
        education_form = abbreviations["form"][groups[2]]
        course = int(groups[3])
        group_number = int(groups[4])
        education_level = abbreviations["level"][groups[5]]
        enter_year = int(groups[6])
        return {"area": area, "department": department, "education_form": education_form, "course": course,
                "group_number": group_number, "education_level": education_level, "enter_year": enter_year}
    except Exception as exception:
        logger.error(f"Ошибка получения данных группы {name}: {exception}")


async def create_group(name: str):
    session = Database().session
    try:
        session.query(Group.id).filter(Group.name == name).one()
        logger.info(f"Группа {name} уже внесена в БД")
    except NoResultFound:
        group_info = await get_group_info(name)
        if group_info:
            logger.info(f"Создана группа: {name}")
            session.add(Group(name=name, **group_info))
        else:
            logger.error(f"Не удалось создать группу: {name}")
    session.commit()
