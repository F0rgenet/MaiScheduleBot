import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event


class Subject(object):
    def __init__(self, name: str, form: str = "", teacher: str = "", location: str = "", start_time: datetime = None,
                 end_time: datetime = None, week: int = 0):
        self.name = name
        self.form = form
        self.teacher = self.format_teacher_fullname(teacher)
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.week = week

    @staticmethod
    def format_teacher_fullname(full_name: str):
        if not full_name: return ""
        words = full_name.split()
        formatted_name = ' '.join(word.title() for word in words)
        return formatted_name

    def __repr__(self):
        formatted_time = f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        return f"{self.name} ({self.form}) {formatted_time} {self.teacher} {self.location}"


pattern = re.compile(
    r'((?P<week_day>Пн|Вт|Ср|Чт|Пт|Сб|Вс), (?P<day>\d\d) (?P<month>.+))|'
    r'(?P<subject>.+)(?P<subject_form>ПЗ|ЛК|ЛБ)|'
    r'((?P<start_time>\d\d:\d\d) – (?P<end_time>\d\d:\d\d))|'
    r'(?P<teacher>[А-Яа-я]+\s[А-Яа-я]+\s[А-Яа-я]+)|'
    r'(?P<location>--каф.|[0-Я]-\d+|ГУК|Орш.)'
)

abbreviations = {
    'Подготовка научных отчетов и презентаций': 'ПНОП',
    'Общие вопросы технологии в информационных системах': 'ОВТИС',
    'Теория вероятностей и математическая статистика': 'ТВИМС',
    'Программирование на языках высокого уровня': 'ПНЯВУ',
}

def parse_line(line: str) -> dict:
    months = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
              "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}
    matches = pattern.finditer(line)
    if not matches: raise ValueError(f"Invalid line: {line}")
    data = {}
    for match in matches:
        groups = match.groupdict()
        for key in groups.keys():
            if key not in data.keys() or not data[key]: data[key] = groups[key]
    if data['day']: data['day'] = int(data['day'])
    if data['month']: data['month'] = months[data['month']]
    return data


def parse_schedule(text: str):
    schedule = []
    current_date = None
    current_subject = None

    lines = text.split('\n')

    for i in range(len(lines)):
        line = lines[i].strip()
        if not line: continue
        data = parse_line(line)
        if data['subject']:
            if current_subject:
                schedule.append(current_subject)
            current_subject = Subject(data['subject'], data['subject_form'])
        elif data['week_day']:
            current_year = datetime.now().year
            current_date = datetime(day=int(data["day"]), month=data["month"], year=current_year)
        elif data['start_time']:
            start_hour, start_minute = map(int, data["start_time"].split(':'))
            current_subject.start_time = current_date.replace(hour=start_hour, minute=start_minute)
            end_hour, end_minute = map(int, data["end_time"].split(':'))
            current_subject.end_time = current_date.replace(hour=end_hour, minute=end_minute)
            if data['teacher']:
                current_subject.teacher = current_subject.format_teacher_fullname(data['teacher'])
            if data['location']:
                current_subject.location = data['location']
    schedule.append(current_subject)
    return schedule


def generate_ics(schedule: list[Subject]) -> bytes:
    cal = Calendar()
    weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
    for subject in schedule:
        event_ics = Event()
        if subject.name in abbreviations:
            subject_name = abbreviations[subject.name]
            subject_description = f"{subject.name}\n{subject.teacher}"
        else:
            subject_name = subject.name
            subject_description = subject.teacher
        event_ics.add('summary', f"{subject_name}({subject.form})")
        event_ics.add('description', subject_description)
        if subject.location != "--каф.":
            event_ics.add('location', subject.location)
        event_ics.add('dtstart', subject.start_time)
        event_ics.add('dtend', subject.end_time)
        week = subject.start_time.weekday()
        event_ics.add('rrule', {'freq': 'weekly', 'interval': 2, 'byday': weekdays[week]})
        cal.add_component(event_ics)

    return cal.to_ical()


with open("schedule.txt", "r", encoding="UTF-8") as file:
    text_schedule = file.read()

parsed_schedule = parse_schedule(text_schedule)
ics_data = generate_ics(parsed_schedule)

with open('schedule.ics', 'wb') as f:
    f.write(ics_data)
