# scripts/populate_base_schedule.py
from datetime import time
import sqlite3
from core.models.schedule import BaseScheduleTemplate
from core.repositories.schedule_repo import BaseScheduleTemplateRepo

conn = sqlite3.connect("data/club.db")
repo = BaseScheduleTemplateRepo(conn)

# пример базового расписания
templates = [
    BaseScheduleTemplate(
        id=None,
        weekday=0,  # понедельник
        start_time=time(20,0),
        duration_minutes=90,
        trainer_id=101,
        place="Малый зал",
        training_type="Рапира",
    ),
    
    BaseScheduleTemplate(
        id=None,
        weekday=1,  # вторник
        start_time=time(20,0),
        duration_minutes=90,
        trainer_id=102,
        place="Малый зал",
        training_type="Сабля",
    ),
    BaseScheduleTemplate(
        id=None,
        weekday=3,  # чт
        start_time=time(20,0),
        duration_minutes=90,
        trainer_id=102,
        place="Малый зал",
        training_type="Сабля",
    ),
        BaseScheduleTemplate(
        id=None,
        weekday=4,  # пт
        start_time=time(20,0),
        duration_minutes=90,
        trainer_id=101,
        place="Малый зал",
        training_type="Рапира",
    ),
    BaseScheduleTemplate(
        id=None,
        weekday=6,  # вс
        start_time=time(14,0),
        duration_minutes=120,
        trainer_id=101,
        place="Малый зал",
        training_type="Самоподготовка",
    ),
]

for t in templates:
    repo.add(t)

print("Базовое расписание создано ✅")
conn.close()
