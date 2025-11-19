"""User model."""

from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    username: str | None
    full_name: str | None   # имя из Telegram

    fio: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    
