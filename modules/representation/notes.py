from modules.parser import parse_schedule
from fpdf import FPDF


def get_telegram_message(group: str, week: int):
    week = parse_schedule(group, week)
    days = []
    for day in week.days:
        day_string = f"**{day.convert_weekday(day.weekday).title()}, {day.day} {day.month}:**\n"
        subjects = []
        for i, subject in enumerate(day.subjects):
            teacher_string = f" / {subject.teacher}" if subject.teacher else ""
            location_string = f" / {subject.location}" if subject.location else ""
            subjects.append(f"\t{i+1}) {subject.name} `({subject.category})`\n\t\t__{subject.time}{teacher_string}{location_string}__")
        day_string += "\n".join(subjects)
        days.append(day_string)
    return "\n\n".join(days)


print(get_telegram_message("М3О-121Б-23", 4))

