\"\"\"Schedule service.\"\"\"

class ScheduleService:
    def __init__(self, repo):
        self.repo = repo

    def get_slots_for_day(self, weekday):
        return [s for s in self.repo.slots if s.day == weekday]
