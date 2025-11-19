import sqlite3

conn = sqlite3.connect("data/club_schedule.db")  # создаёт файл, если его нет
cur = conn.cursor()

# создаём таблицы
cur.executescript("""
CREATE TABLE IF NOT EXISTS base_schedule_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekday INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    trainer_id INTEGER NOT NULL,
    place TEXT NOT NULL,
    training_type TEXT NOT NULL,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS training_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    trainer_id INTEGER NOT NULL,
    place TEXT NOT NULL,
    training_type TEXT NOT NULL,
    source_template_id INTEGER,
    status TEXT NOT NULL,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS schedule_change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_id INTEGER NOT NULL,
    admin_user_id INTEGER NOT NULL,
    change_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp TEXT NOT NULL
);
""")

conn.commit()
conn.close()
print("DB и таблицы созданы ✅")
