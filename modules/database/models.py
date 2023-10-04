from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .main import Database


class Group(Database.BASE):
	__tablename__ = "groups"
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, nullable=False)
	department = Column(Integer, nullable=False)
	course = Column(Integer, nullable=False)
	group_number = Column(Integer, nullable=False)
	education_level = Column(String, nullable=False)
	education_form = Column(String, nullable=False)
	enter_year = Column(Integer, nullable=False)
	area = Column(String, nullable=False)


class Subject(Database.BASE):
	__tablename__ = "subjects"
	id = Column(Integer, primary_key=True, autoincrement=True)
	group_id = Column(Integer, nullable=False)
	name = Column(String, nullable=False)
	category = Column(String, nullable=False)
	audience = Column(String, nullable=False)
	professor = Column(String, nullable=True)
	week = Column(Integer, nullable=False)
	start_time = Column(DateTime(timezone=True), nullable=False)
	end_time = Column(DateTime(timezone=True), nullable=False)


def register_models():
	Database.BASE.metadata.create_all(Database().engine)
