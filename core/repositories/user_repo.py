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
                email TEXT
            )
            """
        )

        await conn.commit()
        return cls(db_path, conn)

    async def get(self, user_id: int) -> Optional[User]:
        cur = await self.conn.execute(
            """
            SELECT user_id, username, full_name,
                   fio, birth_date, gender, phone, email
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
        )

    async def upsert(self, user: User):
        """Обновляет ВСЕ поля. Используется для авто-регистрации и обновления профиля."""
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
                email=excluded.email
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

    async def update_extra(self, user_id: int, **fields):
        """Обновляет только дополнительные поля."""
        keys = []
        values = []

        for k, v in fields.items():
            if v is not None:
                keys.append(f"{k} = ?")
                values.append(v)

        if not keys:
            return

        sql = f"UPDATE users SET {', '.join(keys)} WHERE user_id = ?"
        values.append(user_id)

        await self.conn.execute(sql, values)
        await self.conn.commit()

    async def close(self):
        await self.conn.close()
