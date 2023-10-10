from todoist_api_python.api_async import TodoistAPIAsync, Section, Task
import asyncio
from asyncio import Task as AsyncTask
from loguru import logger


class TodoistApp(object):
    def __init__(self, api_token: str, project_id: int, project_name: str):
        self.api = TodoistAPIAsync(api_token)
        self.project_id = str(project_id)
        self.project_name = project_name


class TodoistTasks(TodoistApp):
    def __init__(self, api_token: str, project_id: int, project_name: str):
        super().__init__(api_token, project_id, project_name)


class TodoistSchedule(TodoistApp):
    def __init__(self, api_token: str, project_id: int, project_name: str):
        super().__init__(api_token, project_id, project_name)
        self.api = TodoistAPIAsync(api_token)
        self.project_id = str(project_id)
        self.default_priority = 2
        self.current_week_label = "[МАИ] Текущая неделя"
        self.preview_project_name = "Текущая неделя"

        # self.schedule_parser = ScheduleParser()

    async def get_projects(self):
        return {project.name: project.id for project in await self.api.get_projects()}

    async def get_sections(self):
        sections = []
        for section in await self.api.get_sections():
            if str(self.project_id) == section.project_id:
                sections.append(section)
        return sections

    async def get_tasks(self):
        tasks = []
        for task in await self.api.get_tasks():
            if str(self.project_id) == task.project_id:
                tasks.append(task)
        return tasks

    async def create_subject_task(self, day, subject, day_task: Task):
        content = f"{subject.name} ({subject.category})"
        description_data = [elem for elem in [subject.location, subject.teacher] if elem]
        description = ' / '.join(map(str, description_data))
        due = f"{day.day} {day.month} 2023 в {subject.time.split('–')[0].strip()}"
        # TODO: rename due, wrong context
        await self.api.add_task(content=content, description=description,
                                priority=self.default_priority, project_id=self.project_id, parent_id=day_task.id,
                                due_string=due, due_lang="ru", labels=[self.current_week_label])

    async def create_day_task(self, day, week_section: Section):
        weekday = day.convert_weekday(day.weekday).title()
        day_task = await self.api.add_task(content=f"* {weekday}", project_id=self.project_id,
                                           section_id=week_section.id)
        for subject in day.subjects:
            await self.create_subject_task(day, subject, day_task)

    async def create_week_section(self, group: str, week_number: int):
        week = self.schedule_parser.parse_schedule(group, week_number)
        week_section = await self.api.add_section(name=f"Неделя {week_number}", project_id=self.project_id)
        for day in week.days:
            await self.create_day_task(day, week_section)

    async def clear_schedule(self):
        for section in await self.get_sections():
            await self.api.delete_section(section.id)
        for task in await self.get_tasks():
            await self.api.delete_task(task.id)

    async def create_preview_project(self):
        await self.api.add_project(self.preview_project_name)

    async def create_homework_task(self, task: int, group_task: Task):
        await self.api.add_task(content=f"№{task}", project_id=self.project_id, parent_id=group_task.id,
                          priority=self.default_priority)
        logger.info(f"Добавлена задача: №{task}")

    # TODO: delete
    async def create_homework_tasks(self, target_task_id: int):
        tasks = {
            "Демидович": "15-21, 23-41, 46, 50, 51, 61, 68-70, 80, 89, 93, 94, 97, 107, 113-115, 117, 128, 129, 138-140, 142, 143, 156, 166-168, 170-179, 181-190, 191-198, 199-202, 203-215, 216-240, 253-263"}
        for group_name, tasks_string in tasks.items():
            group_task = await self.api.add_task(content=f"{group_name}", project_id=self.project_id,
                                                 parent_id=target_task_id, priority=self.default_priority+1)
            async_tasks: list[AsyncTask] = []
            for task in sorted(get_homework_tasks(tasks_string)):
                logger.info(f"Создана задача: №{task}")
                await self.create_homework_task(task, group_task)   


async def create_weeks_tasks(api):
    weeks_tasks = []
    week = 6
    task = asyncio.create_task(api.create_week_section("М3О-121Б-23", week), name=f"Week #{week}")
    weeks_tasks.append(task)
    return weeks_tasks


def get_homework_tasks(string):
    numbers = []
    for span in string.replace(" ", "").split(","):
        if "-" not in span:
            numbers.append(int(span))
        else:
            start, end = list(map(int, span.split("-")))
            numbers.extend(range(start, end+1))
    return numbers


async def test():
    api = TodoistSchedule("db895749923dac14d6407a59c1789f4ba76f7e40", 2320958651, "")
    await api.create_homework_tasks(7268809951)


asyncio.run(test())
