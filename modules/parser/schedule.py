import bs4
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Subject(object):
    def __init__(self, name: str, category: str, time: str, teacher: str = None, location: str = None):
        self.name = name
        self.category = category
        self.time = time
        self.teacher = teacher
        self.location = location

    def __str__(self):
        teacher_string = f" / {self.teacher}" if self.teacher else ""
        location_string = f" / {self.location}" if self.location else ""
        return f"{self.name} ({self.category})\n\t{self.time}{teacher_string}{location_string}"


class Day(object):
    def __init__(self, subjects: list[Subject], day: str, month: str, weekday: int):
        self.subjects = subjects
        self.day = day
        self.month = month
        self.weekday = weekday

    @staticmethod
    def convert_weekday(weekday: int):
        weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресение"]
        return weekdays[weekday]

    def __str__(self):
        text = f"{self.convert_weekday(self.weekday).title()}, {self.day} {self.month}\n"
        subjects = []
        for i, subject in enumerate(self.subjects):
            subjects.append(f"\t{i+1}) {subject}")
        return text + "\n".join(subjects)


class Week(object):
    def __init__(self, days: list[Day]):
        self.days = days

    def __str__(self):
        return "\n".join(map(str, self.days))


def _parse_subject(subject_soup: BeautifulSoup) -> Subject:
    title_data = subject_soup.findChild("p", {"class": "mb-2 fw-semi-bold text-dark"}).text
    title_data = [elem for elem in title_data.replace("\t", " ").replace("\n", " ").split(" ") if elem]
    name = " ".join(title_data[:-1])
    category = title_data[-1]

    other_data = [elem.text for elem in subject_soup.findChildren("li", {"class": "list-inline-item"})]
    time = other_data[0]
    subject = Subject(name, category, time)

    if len(other_data) == 3:
        if other_data[2] != "--каф.":
            subject.location = other_data[2]
        subject.teacher = other_data[1]
    if len(other_data) == 2:
        if other_data[1] != "--каф.":
            subject.location = other_data[1]

    return subject


def _parse_day(day_soup: BeautifulSoup) -> Day | None:
    subjects = []
    date = day_soup.find("span", {"class": "step-title ms-3 ms-sm-0 mt-2 mb-4 mb-sm-2 py-1 text-body"})
    if not date: date = day_soup.find("span", {"class": "step-title ms-3 ms-sm-0 mt-2 mb-4 mb-sm-2 py-1 text-primary"})
    date = date.text.replace("\t", "").replace("\n", "").replace("\xa0", " ")
    weekday = date.split(",")[0].lower()
    date_data = date.strip().split(", ")[1].split(" ")
    day = date_data[0]
    month = date_data[1]
    for subject in day_soup.findChildren("div", {"class": "mb-4"}):
        subjects.append(_parse_subject(subject))
    weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    return Day(subjects, day, month, weekdays.index(weekday))


def parse_schedule(group: str, week: int) -> Week:
    user_agent = UserAgent().chrome
    link = f"https://mai.ru/education/studies/schedule/index.php?group={group}&week={week}"
    data = requests.post(link, headers={"User-Agent": user_agent}, cookies={"schedule-group-cache": "2.0"})
    soup = BeautifulSoup(data.text, "html.parser")
    days = []
    days_soup = soup.find("ul", {"class": "step mb-5"})
    for day in days_soup.findChildren(recursive=False):
        if day:
            days.append(_parse_day(day))
    return Week(days)

