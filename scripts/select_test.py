import sqlite3

DB_PATH = "data/club_schedule.db"

def fix_base_schedule():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Проверяем текущее содержимое
    print("Текущее содержимое base_schedule_templates:")
    for row in cur.execute("SELECT id, weekday, start_time, duration_minutes, trainer_id, place, training_type, active FROM base_schedule_templates"):
        print(row)

    # Исправляем weekday, если он 1-7 (понедельник=0)
    cur.execute("""
        UPDATE base_schedule_templates
        SET weekday = weekday - 1
        WHERE weekday BETWEEN 1 AND 7
    """)
    conn.commit()

    # Делаем все шаблоны активными
    cur.execute("""
        UPDATE base_schedule_templates
        SET active = 1
    """)
    conn.commit()

    print("\nПосле исправления:")
    for row in cur.execute("SELECT id, weekday, start_time, duration_minutes, trainer_id, place, training_type, active FROM base_schedule_templates"):
        print(row)

    conn.close()

if __name__ == "__main__":
    fix_base_schedule()
