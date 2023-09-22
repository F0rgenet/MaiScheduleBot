from modules.parser import parse_schedule
from fpdf import FPDF


def generate_pdf(schedule):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', size=12)
    pdf.cell(w=1, h=1, txt="hello world")
    pdf.output("hello_world.pdf")


def get_samsung_notes(group: str, week: int):
    schedule = parse_schedule(group, week)



get_samsung_notes("М3О-121Б-23", 4)
