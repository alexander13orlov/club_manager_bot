from core.models.user import User

def test_user_model_creation():
    user = User(
        user_id=123,
        username="testuser",
        full_name="Test User"
    )

    assert user.user_id == 123
    assert user.username == "testuser"
    assert user.full_name == "Test User"
