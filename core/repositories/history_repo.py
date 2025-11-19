# core/repositories/history_repo.py

class ScheduleChangeLogRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, log: ScheduleChangeLog) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO schedule_change_log
            (training_id, admin_user_id, change_type, old_value, new_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            log.training_id,
            log.admin_user_id,
            log.change_type,
            json.dumps(log.old_value) if log.old_value else None,
            json.dumps(log.new_value) if log.new_value else None,
            log.timestamp.isoformat()
        ))
        self.conn.commit()
        return cur.lastrowid

    def get_for_training(self, training_id: int) -> List[ScheduleChangeLog]:
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT id, training_id, admin_user_id, change_type, old_value, new_value, timestamp
            FROM schedule_change_log
            WHERE training_id=?
            ORDER BY timestamp
        """, (training_id,)).fetchall()

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
