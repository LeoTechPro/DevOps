# Legacy Django Deployment Template (Docker Compose)

Этот контур показывает пример запуска legacy Django-сервиса через Docker Compose и reverse proxy.
Значения домена, путей, портов, email и имени сервиса ниже условные; перед реальным использованием замените их на свои.

## 1. Подготовка на сервере

```bash
sudo mkdir -p /opt/example-app
sudo chown -R $USER:$USER /opt/example-app
```

Скопируйте в `/opt/example-app` каталоги:
- `hecs` (из `archive/hecs`)
- `hecs-deploy` (из `archive/hecs-deploy`)

Ожидаемая структура:

```text
/opt/example-app/hecs
/opt/example-app/hecs-deploy
```

## 2. Runtime env

```bash
cd /opt/example-app/hecs-deploy
cp .env.example .env
```

Обязательно задайте уникальный `SECRET_KEY`.

## 3. Запуск контейнера

```bash
cd /opt/example-app/hecs-deploy
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
docker compose ps
```

## 4. Nginx

```bash
sudo cp /opt/example-app/hecs-deploy/nginx-hecs.conf /etc/nginx/sites-available/example-app.conf
sudo ln -sf /etc/nginx/sites-available/example-app.conf /etc/nginx/sites-enabled/example-app.conf
sudo nginx -t
sudo systemctl reload nginx
```

Создайте basic-auth файл для `/admin`:

```bash
sudo apt-get update && sudo apt-get install -y apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd-example-admin <admin_user>
sudo nginx -t && sudo systemctl reload nginx
```

## 5. TLS (certbot)

```bash
sudo certbot --nginx -d example.com --redirect -m admin@example.com --agree-tos --no-eff-email
```

Проверка автопродления:

```bash
systemctl status certbot.timer
```

## 6. Smoke checks

```bash
curl -I http://127.0.0.1:18080/healthz
curl -I https://example.com/healthz
docker compose logs --tail=100 web
```
