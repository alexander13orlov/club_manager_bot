import json
from pathlib import Path
from core.repositories.user_repo_json import UserRepository
from core.models.user import User


def test_user_repo_basic(tmp_path: Path):
    file = tmp_path / "users.json"

    repo = UserRepository(file)

    # Пустое хранилище
    assert repo.get(1) is None

    # Добавляем пользователя
    user = User(user_id=1, username="user", full_name="User Name")
    repo.upsert(user)

    # Проверяем, что он сохранился
    loaded = repo.get(1)
    assert loaded is not None
    assert loaded.user_id == 1
    assert loaded.username == "user"
    assert loaded.full_name == "User Name"

    # Проверяем файл
    with open(file, "r", encoding="utf8") as f:
        data = json.load(f)

    assert "1" in data
    assert data["1"]["username"] == "user"
