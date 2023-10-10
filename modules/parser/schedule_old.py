import requests
from bs4 import BeautifulSoup, PageElement
from fake_useragent import UserAgent
from datetime import datetime

url = "https://mai.ru/education/studies/schedule/index.php"


def __get_title(subject_soup: BeautifulSoup):
    data = subject_soup.findChild("p", {"class": "mb-2 fw-semi-bold text-dark"}).get_text(strip=True).split(" ")
    name = " ".join(data[:-1])
    category = data[-1]
    return name, category


def __parse_subject(subject_soup: BeautifulSoup) -> Subject:
    name, category = __get_title(subject_soup)

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


def __parse_day(day_soup: PageElement | BeautifulSoup) -> Day | None:
    subjects = []
    date = day_soup.find("span", {"class": "step-title ms-3 ms-sm-0 mt-2 mb-4 mb-sm-2 py-1 text-body"})
    if not date:
        date = day_soup.find("span",
                             {"class": "step-title ms-3 ms-sm-0 mt-2 mb-4 mb-sm-2 py-1 text-primary"})
    date = date.text.replace("\t", "").replace("\n", "").replace("\xa0", " ")
    weekday = date.split(",")[0].lower()
    date_data = date.strip().split(", ")[1].split(" ")
    day = date_data[0]
    month = date_data[1]
    for subject in day_soup.findChildren("div", {"class": "mb-4"}):
        subjects.append(__parse_subject(subject))
    weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    return Day(subjects, day, month, weekdays.index(weekday))


def parse_schedule(group: str, week: int) -> Week:
    user_agent = UserAgent().chrome
    link = f"{url}?group={group}&week={week}"
    data = requests.post(link, headers={"User-Agent": user_agent}, cookies={"schedule-group-cache": "2.0"})
    soup = BeautifulSoup(data.text, "html.parser")
    days = []
    days_soup = soup.find("ul", {"class": "step mb-5"})
    for day in days_soup.findChildren(recursive=False):
        if day:
            days.append(__parse_day(day))
    return Week(days)
