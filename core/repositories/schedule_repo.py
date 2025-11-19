# core/repositories/schedule_repo.py

import json
import sqlite3
from datetime import datetime, date, time
from typing import Optional, List

from core.models.schedule import (
    BaseScheduleTemplate,
    TrainingInstance,
    ScheduleChangeLog
)


def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


# ---------------------------------------------------------
# BaseScheduleTemplateRepo
# ---------------------------------------------------------

class BaseScheduleTemplateRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, template: BaseScheduleTemplate) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO base_schedule_templates
            (weekday, start_time, duration_minutes, trainer_id, place, training_type, active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            template.weekday,
            template.start_time.strftime("%H:%M"),
            template.duration_minutes,
            template.trainer_id,
            template.place,
            template.training_type,
            1 if template.active else 0
        ))
        self.conn.commit()
        return cur.lastrowid

    def get_all(self) -> List[BaseScheduleTemplate]:
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT id, weekday, start_time, duration_minutes, trainer_id, place, training_type, active
            FROM base_schedule_templates
        """).fetchall()

        return [
            BaseScheduleTemplate(
                id=row[0],
                weekday=row[1],
                start_time=parse_time(row[2]),
                duration_minutes=row[3],
                trainer_id=row[4],
                place=row[5],
                training_type=row[6],
                active=bool(row[7]),
            )
            for row in rows
        ]

    def get_active(self) -> List[BaseScheduleTemplate]:
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT id, weekday, start_time, duration_minutes, trainer_id, place, training_type, active
            FROM base_schedule_templates
            WHERE active=1
        """).fetchall()

        return [
            BaseScheduleTemplate(
                id=row[0],
                weekday=row[1],
                start_time=parse_time(row[2]),
                duration_minutes=row[3],
                trainer_id=row[4],
                place=row[5],
                training_type=row[6],
                active=bool(row[7]),
            )
            for row in rows
        ]



class TrainingInstanceRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, inst: TrainingInstance) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO training_instances
            (date, start_time, duration_minutes, trainer_id, place, training_type, 
             source_template_id, status, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inst.date.isoformat(),
            inst.start_time.strftime("%H:%M"),
            inst.duration_minutes,
            inst.trainer_id,
            inst.place,
            inst.training_type,
            inst.source_template_id,
            inst.status,
            inst.comment
        ))
        self.conn.commit()
        return cur.lastrowid

    def get_by_date(self, d: date) -> List[TrainingInstance]:
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT id, date, start_time, duration_minutes, trainer_id, place, training_type,
                   source_template_id, status, comment
            FROM training_instances
            WHERE date=?
            ORDER BY start_time
        """, (d.isoformat(),)).fetchall()

        return [
            TrainingInstance(
                id=row[0],
                date=parse_date(row[1]),
                start_time=parse_time(row[2]),
                duration_minutes=row[3],
                trainer_id=row[4],
                place=row[5],
                training_type=row[6],
                source_template_id=row[7],
                status=row[8],
                comment=row[9],
            )
            for row in rows
        ]

    def update(self, inst: TrainingInstance):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE training_instances
            SET date=?, start_time=?, duration_minutes=?, trainer_id=?, place=?,
                training_type=?, source_template_id=?, status=?, comment=?
            WHERE id=?
        """, (
            inst.date.isoformat(),
            inst.start_time.strftime("%H:%M"),
            inst.duration_minutes,
            inst.trainer_id,
            inst.place,
            inst.training_type,
            inst.source_template_id,
            inst.status,
            inst.comment,
            inst.id
        ))
        self.conn.commit()


class ScheduleChangeLogRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, log: ScheduleChangeLog) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO schedule_change_log
            (training_id, admin_user_id, change_type, old_value, new_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                log.training_id,
                log.admin_user_id,
                log.change_type,
                json.dumps(log.old_value) if log.old_value else None,
                json.dumps(log.new_value) if log.new_value else None,
                log.timestamp.isoformat(),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_by_training(self, training_id: int) -> List[ScheduleChangeLog]:
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT id, training_id, admin_user_id, change_type,
                   old_value, new_value, timestamp
            FROM schedule_change_log
            WHERE training_id=?
            ORDER BY timestamp DESC
            """,
            (training_id,),
        ).fetchall()

        result = []
        for row in rows:
            result.append(
                ScheduleChangeLog(
                    id=row[0],
                    training_id=row[1],
                    admin_user_id=row[2],
                    change_type=row[3],
                    old_value=json.loads(row[4]) if row[4] else None,
                    new_value=json.loads(row[5]) if row[5] else None,
                    timestamp=datetime.fromisoformat(row[6]),
                )
            )
        return result

    def get_all(self, limit: int = 100) -> List[ScheduleChangeLog]:
        cur = self.conn.cursor()
        rows = cur.execute(
            f"""
            SELECT id, training_id, admin_user_id, change_type,
                   old_value, new_value, timestamp
            FROM schedule_change_log
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            ScheduleChangeLog(
                id=row[0],
                training_id=row[1],
                admin_user_id=row[2],
                change_type=row[3],
                old_value=json.loads(row[4]) if row[4] else None,
                new_value=json.loads(row[5]) if row[5] else None,
                timestamp=datetime.fromisoformat(row[6]),
            )
            for row in rows
        ]
