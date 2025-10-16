class AppState:
    user_email = None
    user_role = None
    token = None

    @classmethod
    def set_user(cls, email, role, token=None):
        cls.user_email = email
        cls.user_role = role
        cls.token = token

    @classmethod
    def clear(cls):
        cls.user_email = None
        cls.user_role = None
        cls.token = None
