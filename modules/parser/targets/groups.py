from modules.parser.utils import groups_request
from bs4 import BeautifulSoup, ResultSet
from loguru import logger


async def __parse_levels(level_soup: BeautifulSoup) -> list[str]:
    group_class = "btn btn-soft-secondary btn-xs mb-1 fw-medium btn-group"
    groups: list[BeautifulSoup] = level_soup.findAll("a", {"class": group_class})
    return [group.get_text(strip=True) for group in groups]


async def __parse_course(course_soup: BeautifulSoup) -> list[str]:
    levels: list[BeautifulSoup] = course_soup.findAll("div", {"role": "tabpanel"})
    groups = []
    for level_soup in levels:
        groups.extend(await __parse_levels(level_soup))
    return groups


async def __parse_department(department: str) -> list[str]:
    soup: BeautifulSoup = await groups_request(department=department, course="all")
    courses: list[BeautifulSoup] = soup.findAll("div", {"class": "tab-content mb-5 mb-sm-8"})
    groups = []
    for course_soup in courses:
        groups.extend(await __parse_course(course_soup))
    return groups


async def get_departments() -> list[str]:
    soup: BeautifulSoup = await groups_request()
    departments_soup: ResultSet = soup.find("select", {"id": "department"}).findChildren(recursive=False)[1:]
    departments = [elem.get_text(strip=True) for elem in departments_soup]
    return sorted(departments, key=lambda elem: int(elem.split("№")[1]))


async def parse_groups():
    groups = []
    for department in await get_departments():
        logger.info(f"Поиск групп для {department}")
        groups.extend(await __parse_department(department))
    return groups
