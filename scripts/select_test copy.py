import sqlite3

DB_PATH = "data/club_schedule.db"

def fix_base_schedule():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Проверяем текущее содержимое
    print("Текущее содержимое base_schedule_templates:")
    for row in cur.execute("SELECT id, weekday, start_time, duration_minutes, trainer_id, place, training_type, active FROM base_schedule_templates"):
        print(row)

   

    conn.close()

if __name__ == "__main__":
    fix_base_schedule()
