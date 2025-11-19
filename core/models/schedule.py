# core/models/schedule.py

from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional, Dict, Any


# ============================================================
#  БАЗОВОЕ ЗАНЯТИЕ НЕДЕЛЬНОГО РАСПИСАНИЯ
# ============================================================

@dataclass
class BaseScheduleTemplate:
    id: Optional[int]
    weekday: int                   # 0–6
    start_time: time
    duration_minutes: int
    trainer_id: int
    place: str
    training_type: str
    active: bool = True

    @staticmethod
    def table_name() -> str:
        return "base_schedule_templates"


# ============================================================
#  КОНКРЕТНОЕ ЗАНЯТИЕ ПО КАЛЕНДАРЮ
# ============================================================

@dataclass
class TrainingInstance:
    id: Optional[int]
    date: date
    start_time: time
    duration_minutes: int
    trainer_id: int
    place: str
    training_type: str
    source_template_id: Optional[int]   # null → создано вручную
    status: str                         # planned / canceled / moved / extra
    comment: Optional[str] = None

    @staticmethod
    def table_name() -> str:
        return "training_instances"

    @staticmethod
    def from_template(t: BaseScheduleTemplate, d: date) -> "TrainingInstance":
        """Создаёт instance из weekly-template."""
        return TrainingInstance(
            id=None,
            date=d,
            start_time=t.start_time,
            duration_minutes=t.duration_minutes,
            trainer_id=t.trainer_id,
            place=t.place,
            training_type=t.training_type,
            source_template_id=t.id,
            status="planned",
        )

    def moved_copy(
        self,
        new_time: time,
        new_duration: int,
        new_trainer: int,
        new_place: str
    ) -> "TrainingInstance":
        """Генерирует перемещённое занятие."""
        return TrainingInstance(
            id=None,
            date=self.date,
            start_time=new_time,
            duration_minutes=new_duration,
            trainer_id=new_trainer,
            place=new_place,
            training_type=self.training_type,
            source_template_id=None,      # moved — всегда one-time
            status="moved",
            comment=None
        )


# ============================================================
#  ЛОГ ИЗМЕНЕНИЙ РАСПИСАНИЯ
# ============================================================

@dataclass
class ScheduleChangeLog:
    id: Optional[int]
    training_id: int
    admin_user_id: int

    change_type: str            # added / canceled / time_changed / moved / trainer_changed
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]

    timestamp: Optional[datetime] = None

