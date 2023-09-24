from todoist_api_python.api import TodoistAPI


class TodoistSchedule(object):
    def __init__(self):
        self.api = TodoistAPI("db895749923dac14d6407a59c1789f4ba76f7e40")

    def load_schedule(self,  project_id: int, parent_id: int):
        pass
