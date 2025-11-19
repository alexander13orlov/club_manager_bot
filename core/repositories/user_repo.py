# core/repositories/user_repo.py
# core/repositories/user_repo.py
import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone

from core.models.user import User


def utc_now_iso() -> str:
    """Текущее время UTC в формате ISO 8601 с зоной +00:00."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
                email TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        await conn.commit()
        return cls(db_path, conn)

    async def get_all_users(self) -> List[User]:
        cursor = await self.conn.execute(
            """
            SELECT user_id, username, full_name,
                   fio, birth_date, gender, phone, email,
                   created_at, updated_at
            FROM users
            ORDER BY fio ASC, full_name ASC, username ASC
            """
        )
        rows = await cursor.fetchall()
        await cursor.close()

        users = [
            User(
                user_id=row[0],
                username=row[1],
                full_name=row[2],
                fio=row[3],
                birth_date=row[4],
                gender=row[5],
                phone=row[6],
                email=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
            for row in rows
        ]
        return users

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
            updated_at=row[9]
        )

    async def upsert(self, user: User):
        """
        Вставка или обновление пользователя.
        При вставке created_at = текущее UTC время.
        При обновлении updated_at = текущее UTC время.
        """
        now = utc_now_iso()
        if not user.created_at:
            user.created_at = now
        user.updated_at = now

        await self.conn.execute(
            """
            INSERT INTO users(
                user_id, username, full_name,
                fio, birth_date, gender, phone, email,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                fio=excluded.fio,
                birth_date=excluded.birth_date,
                gender=excluded.gender,
                phone=excluded.phone,
                email=excluded.email,
                updated_at=excluded.updated_at
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
                user.created_at,
                user.updated_at
            )
        )
        await self.conn.commit()

    async def update_extra(self, user_id: int, **fields):
        """Обновляет только дополнительные поля и updated_at."""
        keys = []
        values = []

        for k, v in fields.items():
            if v is not None:
                keys.append(f"{k} = ?")
                values.append(v)

        if not keys:
            return

        # Добавляем updated_at
        keys.append("updated_at = ?")
        values.append(utc_now_iso())

        sql = f"UPDATE users SET {', '.join(keys)} WHERE user_id = ?"
        values.append(user_id)

        await self.conn.execute(sql, values)
        await self.conn.commit()

    async def close(self):
        await self.conn.close()

