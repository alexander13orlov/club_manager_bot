# core/models/user.py
# User model
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def current_time_iso() -> str:
    """Возвращает текущее время в формате ISO."""
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")


@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None

    fio: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    created_at: str = field(default_factory=current_time_iso)
    updated_at: str = field(default_factory=current_time_iso)

    def touch(self):
        """Обновить updated_at."""
        self.updated_at = current_time_iso()

    def update_fields(self, **kwargs):
        """
        Обновляет только непустые поля.
        Автоматически обновляет updated_at, если что-то поменялось.
        """
        changed = False
        for k, v in kwargs.items():
            if hasattr(self, k) and v is not None and getattr(self, k) != v:
                setattr(self, k, v)
                changed = True
        if changed:
            self.touch()
        return changed

