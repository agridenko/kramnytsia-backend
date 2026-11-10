from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Обмежує частоту запитів на отримання JWT-токена (захист від брутфорсу)."""

    scope = "login"


class PaymentRateThrottle(UserRateThrottle):
    """Обмежує частоту запитів на створення платежу для авторизованих користувачів."""

    scope = "payment"
