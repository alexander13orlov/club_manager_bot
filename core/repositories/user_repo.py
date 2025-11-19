# core/repositories/user_repo.py
import aiosqlite
from pathlib import Path
from typing import Optional
from core.models.user import User


class UserRepository:
    """Асинхронный репозиторий пользователей на SQLite."""

    def __init__(self, db_path: str, conn: aiosqlite.Connection):
        self.db_path = db_path
        self.conn = conn

    @classmethod
    async def create(cls, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(db_path)

        # Обновленная структура таблицы
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,

                fio TEXT,
                birth_date TEXT,
                gender TEXT,
                phone TEXT,
                email TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await conn.commit()
        return cls(db_path, conn)

    # ----------------------- SELECT ALL -----------------------

    async def get_all_users(self):
        cursor = await self.conn.execute("""
            SELECT user_id, username, full_name,
                   fio, birth_date, gender, phone, email,
                   created_at, updated_at
            FROM users
            ORDER BY user_id ASC
        """)

        rows = await cursor.fetchall()
        await cursor.close()

        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                full_name=row[2],
                fio=row[3],
                birth_date=row[4],
                gender=row[5],
                phone=row[6],
                email=row[7],
                created_at=row[8],
                updated_at=row[9],
            ))

        return users

    # ----------------------- SELECT ONE -----------------------

    async def get(self, user_id: int) -> Optional[User]:
        cur = await self.conn.execute(
            """
            SELECT user_id, username, full_name,
                   fio, birth_date, gender, phone, email,
                   created_at, updated_at
            FROM users WHERE user_id = ?
            """,
            (user_id,)
        )
        row = await cur.fetchone()
        await cur.close()

        if not row:
            return None

        return User(
            user_id=row[0],
            username=row[1],
            full_name=row[2],
            fio=row[3],
            birth_date=row[4],
            gender=row[5],
            phone=row[6],
            email=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    # ----------------------- UPSERT -----------------------

    async def upsert(self, user: User):
        """
        Обновляет ВСЕ поля.
        created_at — трогать не нужно (ставится при INSERT).
        updated_at — обновляется при каждом UPDATE.
        """
        await self.conn.execute(
            """
            INSERT INTO users(
                user_id, username, full_name,
                fio, birth_date, gender, phone, email
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,

                fio=excluded.fio,
                birth_date=excluded.birth_date,
                gender=excluded.gender,
                phone=excluded.phone,
                email=excluded.email,

                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user.user_id,
                user.username,
                user.full_name,
                user.fio,
                user.birth_date,
                user.gender,
                user.phone,
                user.email,
            )
        )
        await self.conn.commit()

    # ----------------------- UPDATE EXTRA -----------------------

    async def update_extra(self, user_id: int, **fields):
        """
        Обновляет только дополнительные поля.
        updated_at всегда обновляется.
        """
        keys = []
        values = []

        for k, v in fields.items():
            if v is not None:
                keys.append(f"{k} = ?")
                values.append(v)

        if not keys:
            return

        # Добавляем обновление updated_at
        keys.append("updated_at = CURRENT_TIMESTAMP")

        sql = f"UPDATE users SET {', '.join(keys)} WHERE user_id = ?"
        values.append(user_id)

        await self.conn.execute(sql, values)
        await self.conn.commit()

    async def close(self):
        await self.conn.close()
