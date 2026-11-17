from django.db import connection
from django.http import JsonResponse


def health(request):
    """Легкий ендпоінт для keep-alive та моніторингу."""
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_ok = False

    return JsonResponse(
        {"status": "ok" if db_ok else "degraded", "db": db_ok},
        status=200 if db_ok else 503,
    )
