\"\"\"Schedule repository (JSON).\"\"\"

import json
from core.models.schedule import WorkoutSlot

class ScheduleRepository:
    def __init__(self, path):
        self.path = path
        self.slots = self._load()

    def _load(self):
        try:
            with open(self.path, \"r\", encoding=\"utf8\") as f:
                data = json.load(f)
            arr = data.get(\"training_schedule\", [])
            return [WorkoutSlot(**s) for s in arr]
        except:
            return []
