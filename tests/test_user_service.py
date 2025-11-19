from core.services.user_service import UserService
from core.repositories.user_repo_json import UserRepository
from core.models.user import User


class FakeTgUser:
    def __init__(self, id, username, full_name):
        self.id = id
        self.username = username
        self.full_name = full_name


def test_user_service_register(tmp_path):
    file = tmp_path / "users.json"
    repo = UserRepository(file)
    service = UserService(repo)

    tg_user = FakeTgUser(100, "tester", "Tester User")

    # Первый вызов — регистрация
    new_user = service.register_if_needed(tg_user)
    assert isinstance(new_user, User)
    assert new_user.user_id == 100

    # Второй вызов — не создаёт нового пользователя
    same_user = service.register_if_needed(tg_user)
    assert same_user is new_user
