from app.accounts.models import User


class AccountService:

    @staticmethod
    def update_profile(user_id: int, data: dict) -> User:
        allowed_fields = {"bio", "avatar"}
        clean = {k: v for k, v in data.items() if k in allowed_fields}
        User.objects.filter(id=user_id).update(**clean)
        return User.objects.get(id=user_id)

    @staticmethod
    def register(username: str, email: str, password: str) -> User:
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
    