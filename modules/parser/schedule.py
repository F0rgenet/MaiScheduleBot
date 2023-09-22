import bs4
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def _get_cookies():
    return {"schedule-group-cache": "2.0"}


def _parse_subject(subject_soup: BeautifulSoup):
    title_data = subject_soup.findChild("p", {"class": "mb-2 fw-semi-bold text-dark"}).text
    title_data = [elem for elem in title_data.replace("\t", " ").replace("\n", " ").split(" ") if elem]
    subject_name = " ".join(title_data[:-1])
    subject_type = title_data[-1]

    other_data = [elem.text for elem in subject_soup.findChildren("li", {"class": "list-inline-item"})]
    result = {"name": subject_name, "type": subject_type, "time": other_data[0]}
    if len(other_data) == 3:
        if other_data[2] != "--каф.":
            result["place"] = other_data[2]
        result["teacher"] = other_data[1]
    if len(other_data) == 2:
        if other_data[1] != "--каф.":
            result["place"] = other_data[1]

    return result


def _parse_day(day_soup: BeautifulSoup):
    subjects = []
    date = day_soup.find("span", {"class": "step-title ms-3 ms-sm-0 mt-2 mb-4 mb-sm-2 py-1 text-body"})
    date = date.text.replace("\t", "").replace("\n", "").replace("\xa0", " ")
    weekday = date.split(",")[0]
    day = date.split(", "[1])
    for subject in day_soup.findChildren("div", {"class": "mb-4"}):
        subjects.append(_parse_subject(subject))
    return {"subjects": subjects, "weekday": weekday, "day": day}


def parse_schedule(group: str, week: int):
    user_agent = UserAgent().chrome
    link = f"https://mai.ru/education/studies/schedule/index.php?group={group}&week={week}"
    data = requests.post(link, headers={"User-Agent": user_agent}, cookies=_get_cookies())
    soup = BeautifulSoup(data.text, "html.parser")
    days = []
    days_soup = soup.find("ul", {"class": "step mb-5"})
    for day in days_soup.findChildren(recursive=False):
        days.append(_parse_day(day))
    return days
