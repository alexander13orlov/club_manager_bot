\"\"\"Attendance tracking service.\"\"\"

from core.models.attendance import AttendanceRecord
from datetime import datetime

class AttendanceService:
    def __init__(self, repo):
        self.repo = repo

    def mark_attendance(self, user_id, workout_type):
        record = AttendanceRecord(user_id=user_id, workout_type=workout_type, timestamp=datetime.now())
        self.repo.add(record)
