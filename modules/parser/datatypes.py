from datetime import datetime


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

    @staticmethod
    def get_current():
        months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
        current_month = datetime.now().month


    def __str__(self):
        return "\n".join(map(str, self.days))
