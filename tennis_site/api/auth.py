from django.http import JsonResponse

# 🔑 Универсальный API-ключ (замени на свой)
UNIVERSAL_API_KEY = "super-secret-key-123"

def api_key_required(view_func):
    """
    Декоратор: даёт доступ к API если:
    1) Пользователь залогинен, или
    2) Передан правильный X-API-Key в заголовке запроса
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        api_key = request.headers.get("X-API-Key")
        if api_key == UNIVERSAL_API_KEY:
            return view_func(request, *args, **kwargs)

        return JsonResponse({"error": "Доступ запрещён: требуется API ключ"}, status=401)

    return wrapper
