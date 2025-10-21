# your_project/middleware/registration_rate_limit.py
import time
from django.conf import settings
from django.core.cache import caches
from django.http import JsonResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin

# Используем кэш по имени (по умолчанию "default")
cache = caches[ getattr(settings, "REG_RATE_CACHE_ALIAS", "default") ]

class RegistrationRateLimitMiddleware(MiddlewareMixin):
    """
    Ограничивает количество регистраций с одного IP за окно времени.
    Настройки в settings.py:
      REG_RATE_LIMIT = 6             # макс. попыток за окно
      REG_RATE_WINDOW = 600          # окно в секундах (по умолчанию 1 час)
      REG_BLOCK_STATUS = 429         # HTTP статус при блокировке
      REG_RATE_CHECK_PATHS = ["/accounts/register/", "/api/register/"]
      REG_TRUSTED_PROXY_HEADER = "HTTP_X_FORWARDED_FOR" # заголовок для IP из proxy
      REG_RATE_CACHE_ALIAS = "default"  # кэш alias
    """

    def _get_remote_ip(self, request):
        # Если сайт за прокси/LoadBalancer, то возьми X-Forwarded-For (последний ненулевой)
        header = getattr(settings, "REG_TRUSTED_PROXY_HEADER", "HTTP_X_FORWARDED_FOR")
        xff = request.META.get(header)
        if xff:
            # X-Forwarded-For может быть "client, proxy1, proxy2"
            parts = [p.strip() for p in xff.split(",") if p.strip()]
            if parts:
                # берём первый элемент — реальный клиент (или последний в зависимости от конфигурации proxy)
                return parts[0]
        # fallback
        return request.META.get("REMOTE_ADDR", "")

    def process_request(self, request):
        # Проверяем пути, которые будем отслеживать
        paths = getattr(settings, "REG_RATE_CHECK_PATHS", ["/accounts/register/"])
        # если путь не совпадает ни с одним шаблоном — пропускаем
        path = request.path
        if not any(path.startswith(p) for p in paths):
            return None

        # Только реагируем на POST-запросы (регистрация — обычно POST)
        if request.method.upper() != "POST":
            return None

        ip = self._get_remote_ip(request) or "unknown"
        window = getattr(settings, "REG_RATE_WINDOW", 600)
        limit = getattr(settings, "REG_RATE_LIMIT", 6)
        cache_key = f"reg_rl:{ip}"

        # Стратегия: храним (count, first_ts)
        entry = cache.get(cache_key)
        now = int(time.time())
        if entry is None:
            entry = {"count": 1, "first": now}
            cache.set(cache_key, entry, timeout=window)
        else:
            # если окно истек — сбрасываем
            if now - entry["first"] > window:
                entry = {"count": 1, "first": now}
                cache.set(cache_key, entry, timeout=window)
            else:
                entry["count"] += 1
                # обновляем TTL — не обязательно, но полезно
                cache.set(cache_key, entry, timeout=window - (now - entry["first"]))

        if entry["count"] > limit:
            # можно вернуть JSON с info или Text
            status = getattr(settings, "REG_BLOCK_STATUS", 429)
            retry_after = entry["first"] + window - now
            data = {
                "detail": "Too many registration attempts from your IP. Try later.",
                "retry_after_seconds": max(retry_after, 0)
            }
            # Добавим заголовок Retry-After
            response = JsonResponse(data, status=status)
            try:
                response["Retry-After"] = str(max(retry_after, 0))
            except Exception:
                pass
            return response

        return None
