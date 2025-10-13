# 🎾 LiteTennis — Django Web Application

## 📖 Описание проекта
LiteTennis — это веб-платформа, созданная на *Django (Python 3.13)* для теннисного сообщества.  
Сайт позволяет пользователям создавать профили, просматривать достижения, участвовать в турнирах и общаться между собой.  
База данных — *SQLite*, сервер — **Hoster.kz (VDS Cloud 1-1-25)**,  
локация — **Астана**, домен — **litetennis.kz**, ОС — **Ubuntu 24.04 LTS**.

---

## ⚙ Параметры сервера

| Параметр | Значение |
|-----------|-----------|
| Сервер | cloud-001.h-145957.kz |
| IP-адрес | 89.35.124.44 |
| Локальный IP | 172.16.0.2 |
| ОС | Ubuntu 24.04 |
| CPU / RAM / Storage | 1 vCPU / 1 GB RAM / 25 GB SSD |
| Локация | Астана |

---

## 🚀 Локальный запуск (Windows)

### 1️⃣ Проверка Python
```bash
py -3.13 --version
Если не установлен — скачай с python.org/downloads.

2️⃣ Распаковка проекта
bash
Копировать код
C:\100 бальник\litetennis\
3️⃣ Создание виртуального окружения
bash
Копировать код
py -3.13 -m venv venv
venv\Scripts\activate
4️⃣ Установка зависимостей
bash
Копировать код
pip install -r requirements.txt
Если файла нет:

bash
Копировать код
pip install django pillow
5️⃣ Применение миграций
bash
Копировать код
py -3.13 manage.py makemigrations
py -3.13 manage.py migrate
6️⃣ Создание суперпользователя
bash
Копировать код
py -3.13 manage.py createsuperuser
7️⃣ Запуск локального сервера
bash
Копировать код
py -3.13 manage.py runserver
Теперь открой:
👉 http://127.0.0.1:8000/

☁ Развёртывание на сервере (Hoster.kz, Ubuntu 24.04)
1️⃣ Подключение к серверу
bash
Копировать код
ssh root@89.35.124.44
# или
ssh h-145957@89.35.124.44
2️⃣ Обновление и установка зависимостей
bash
Копировать код
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nginx git unzip -y
3️⃣ Загрузка проекта
bash
Копировать код
cd /var/www
git clone https://github.com/tipbandit52-stack/tennis_site.git litetennis
cd litetennis
4️⃣ Создание окружения и установка зависимостей
bash
Копировать код
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
5️⃣ Проверка запуска
bash
Копировать код
python3 manage.py runserver 0.0.0.0:8000
👉 http://89.35.124.44:8000

6️⃣ Настройка Gunicorn
bash
Копировать код
pip install gunicorn
gunicorn tennis_site.wsgi:application --bind 0.0.0.0:8000
7️⃣ Настройка Nginx для домена litetennis.kz
Создай файл:

bash
Копировать код
sudo nano /etc/nginx/sites-available/litetennis
Вставь:

nginx
Копировать код
server {
    listen 80;
    server_name litetennis.kz www.litetennis.kz;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /var/www/litetennis/tennis_site/staticfiles/;
    }
    location /media/ {
        alias /var/www/litetennis/tennis_site/media/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/litetennis/gunicorn.sock;
    }
}
Активируй конфиг:

bash
Копировать код
ln -s /etc/nginx/sites-available/litetennis /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
8️⃣ Настройка SSL (HTTPS)
bash
Копировать код
apt install certbot python3-certbot-nginx -y
certbot --nginx -d litetennis.kz -d www.litetennis.kz
После успешной установки сайт будет доступен по адресу:
👉 https://litetennis.kz

🧰 Команды для работы в PowerShell и на сервере
Назначение	Команда
Подключение к серверу	ssh root@89.35.124.44
Перейти в проект	cd /var/www/litetennis/tennis_site
Активировать окружение	source ../venv/bin/activate
Проверить статус gunicorn	sudo systemctl status gunicorn
Проверить статус nginx	sudo systemctl status nginx
Перезапустить сайт	sudo systemctl restart gunicorn nginx
Просмотреть ошибки gunicorn	sudo journalctl -u gunicorn -n 30
Просмотреть логи nginx	sudo journalctl -u nginx -n 30
Редактировать файл	sudo nano <имя_файла>
Резервная копия БД	cp db.sqlite3 db_backup_$(date +%F).sqlite3

🔐 Доступ к админ-панели Django
Адрес:
👉 https://litetennis.kz/admin/

Введи свои логин и пароль администратора вручную
(Не храни реальные пароли в GitHub или публичных файлах.)

🔑 API-доступ
LiteTennis предоставляет публичный REST API с возможностью просмотра списка игроков, турниров и матчей.
Для авторизации можно использовать универсальный API-ключ.

Пример запроса:

bash
Копировать код
https://litetennis.kz/api/players/?api_key=super-secret-key-123
Пример ответа:

json
Копировать код
[
  {
    "id": 1,
    "first_name": "Timur",
    "last_name": "Ibdiminov",
    "level": "4.0",
    "phone_number": "+7 777 015 2499"
  }
]
👤 Автор проекта
Ибдиминов Тимур
📱 +7 777 015 2499 (WhatsApp / Telegram)
🌍 https://litetennis.kz

© 2025 LiteTennis — Все права защищены.