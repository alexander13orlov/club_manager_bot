\"\"\"Workout schedule model.\"\"\"

from dataclasses import dataclass

@dataclass
class WorkoutSlot:
    day: str
    start: str
    workout_type: str
