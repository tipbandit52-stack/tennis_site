# 🎾 LiteTennis — Django Web Application

## 📖 Описание проекта
LiteTennis — это веб-платформа, созданная на **Django (Python 3.13)** для теннисного сообщества.  
Сайт позволяет пользователям создавать профили, просматривать достижения, участвовать в турнирах и общаться между собой.  
База данных — **SQLite**, сервер — **Hoster.kz (VDS Cloud 1-1-25)**, локация — **Астана**, домен — **litetennis.kz**, ОС — **Ubuntu 24.04 LTS**.

---

## ⚙️ Параметры сервера

| Параметр | Значение |
|-----------|-----------|
| Сервер | `cloud-001.h-145957.kz` |
| IP-адрес | `89.35.124.44` |
| Локальный IP | `172.16.0.2` |
| ОС | Ubuntu 24.04 |
| CPU / RAM / Storage | 1 vCPU / 1 GB RAM / 25 GB SSD |
| Локация | Астана |

---

## 🚀 Локальный запуск (Windows)

### 1️⃣ Проверка Python
```bash
py -3.13 --version


Если не установлен — скачай с python.org/downloads

2️⃣ Распаковка проекта

Распакуй архив проекта, например:

C:\100 бальник\litetennis\

3️⃣ Создание виртуального окружения
py -3.13 -m venv venv
venv\Scripts\activate

4️⃣ Установка зависимостей
pip install -r requirements.txt


Если файла нет:

pip install django pillow

5️⃣ Применение миграций
py -3.13 manage.py makemigrations
py -3.13 manage.py migrate

6️⃣ Создание суперпользователя
py -3.13 manage.py createsuperuser

7️⃣ Запуск локального сервера
py -3.13 manage.py runserver


Теперь открой:
👉 http://127.0.0.1:8000/

☁️ Развёртывание на сервере (Hoster.kz, Ubuntu 24.04)
1️⃣ Подключение к серверу

Подключись по SSH:

ssh root@89.35.124.44

2️⃣ Обновление и установка зависимостей
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nginx git unzip -y

3️⃣ Загрузка проекта

Загрузи архив или клонируй с GitHub:

cd /root/
unzip litetennis.zip -d litetennis/
cd litetennis/

4️⃣ Создание окружения и установка зависимостей
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput

5️⃣ Проверка запуска
python3 manage.py runserver 0.0.0.0:8000


Открой в браузере:
👉 http://89.35.124.44:8000

6️⃣ Настройка Gunicorn
pip install gunicorn
gunicorn litetennis.wsgi:application --bind 0.0.0.0:8000

7️⃣ Настройка Nginx для домена litetennis.kz

Создай файл:

nano /etc/nginx/sites-available/litetennis


Вставь:

server {
    server_name litetennis.kz www.litetennis.kz;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /root/litetennis;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}


Активируй конфиг:

ln -s /etc/nginx/sites-available/litetennis /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

8️⃣ Настройка SSL (HTTPS)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d litetennis.kz -d www.litetennis.kz


После успешной установки сайт будет доступен по:
👉 https://litetennis.kz

🧰 Полезные команды
Назначение	Команда
Проверить версию Django	py -3.13 -m django --version
Применить миграции	py -3.13 manage.py migrate
Создать суперпользователя	py -3.13 manage.py createsuperuser
Собрать статику	py -3.13 manage.py collectstatic
Запустить сервер разработки	py -3.13 manage.py runserver
Запустить Gunicorn вручную	gunicorn litetennis.wsgi:application --bind 0.0.0.0:8000
Проверить логи Nginx	journalctl -u nginx
👤 Автор проекта

Ибдиминов Тимур
📱 +7 777 015 2499 (WhatsApp / Telegram)
🌍 https://litetennis.kz

© 2025 LiteTennis — Все права защищены.
