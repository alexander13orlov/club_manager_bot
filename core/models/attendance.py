\"\"\"Attendance record model.\"\"\"

from dataclasses import dataclass
from datetime import datetime

@dataclass
class AttendanceRecord:
    user_id: int
    workout_type: str
    timestamp: datetime
