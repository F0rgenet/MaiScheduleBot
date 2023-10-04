import httpx
from bs4 import BeautifulSoup, ResultSet
from fake_useragent import UserAgent
from accessify import private
from loguru import logger
from modules.database import create_group


class GroupsParser(object):
    def __init__(self):
        self.__url = "https://mai.ru/education/studies/schedule/groups.php"

    @private
    async def request(self, **kwargs) -> BeautifulSoup:
        args = "&".join([f"{key}={value.replace(' ', '+')}" for key, value in kwargs.items()])
        link = f"{self.__url}?{args}"
        async with httpx.AsyncClient() as session:
            headers = {'user-agent': UserAgent().chrome}
            response = await session.get(link, headers=headers)
            if response.status_code != 200:
                raise ConnectionError(f"Невозможно установить подключение с {self.__url}")
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    @private
    async def parse_levels(self, level_soup: BeautifulSoup) -> list[str]:
        group_class = "btn btn-soft-secondary btn-xs mb-1 fw-medium btn-group"
        groups: list[BeautifulSoup] = level_soup.findAll("a", {"class": group_class})
        return [group.get_text(strip=True) for group in groups]

    @private
    async def parse_course(self, course_soup: BeautifulSoup) -> list[str]:
        levels: list[BeautifulSoup] = course_soup.findAll("div", {"role": "tabpanel"})
        groups = []
        for level_soup in levels:
            groups.extend(await self.parse_levels(level_soup))
        return groups

    @private
    async def parse_department(self, department: str) -> list[str]:
        soup: BeautifulSoup = await self.request(department=department, course="all")
        courses: list[BeautifulSoup] = soup.findAll("div", {"class": "tab-content mb-5 mb-sm-8"})
        groups = []
        for course_soup in courses:
            groups.extend(await self.parse_course(course_soup))
        return groups

    async def get_departments(self) -> list[str]:
        soup: BeautifulSoup = await self.request()
        departments_soup: ResultSet = soup.find("select", {"id": "department"}).findChildren(recursive=False)[1:]
        departments = [elem.get_text(strip=True) for elem in departments_soup]
        return sorted(departments, key=lambda elem: int(elem.split("№")[1]))

    async def parse_groups(self):
        for department in await self.get_departments():
            logger.info(f"Поиск групп для {department}")
            groups = await self.parse_department(department)
            for group in groups:
                await create_group(group)
