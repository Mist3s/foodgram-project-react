# ![Kittygram](https://kittygram-yandex.hopto.org/static/media/logo.018b6643f3dd14ed8a10432df1ab2a2b.svg) Kittygram

Данный проект служит интернет-площадкой для котоводов, где владельцы своих котиков могут выставлять их на показ включая имя, цвет, дату рождения и даже фото, а так же отмечать достижения кота. Благодаря данному ресурсу хозяева кошачих смогут создать реестр своих питомцев.



![example workflow](https://github.com/Mist3s/kittygram_final/actions/workflows/main.yml/badge.svg)

## Установка

Для развертывания проекта, используйте `docker-compose.production.yml`. Убедитесь, что у вас [установлен Docker](#установка-docker) и Docker Compose.

Запустите Docker Compose с этой конфигурацией на своём компьютере
```bash
docker-compose -f docker-compose.production.yml up -d
```
Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /static/static/:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
```bash
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /static/static/
```
## Установка Docker

<details>
<summary>Установка на Ubuntu</summary>

1. ```bash
    sudo apt-get update
   ```
2. ```bash
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
   ```
3. ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   ```
4. ```bash
    echo "deb [signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
5. ```bash
    sudo apt-get update
   ```
6. ```bash
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   ```
7. ```bash
    sudo usermod -aG docker $USER
   ```
8. ```bash
    sudo reboot
   ```
</details>

<details>
<summary>Установка на Windows</summary>

1. Скачайте установщик Docker Desktop с [официального сайта Docker](https://www.docker.com/products/docker-desktop) и выполните его установку.
2. Запустите Docker Desktop после установки.

</details>

<details>
<summary>Установка на macOS</summary>

1. Скачайте установщик Docker Desktop с [официального сайта Docker](https://www.docker.com/products/docker-desktop) и выполните его установку.
2. Запустите Docker Desktop после установки.

</details>

## Об авторе
Python-разработчик

[Андрей Иванов](https://github.com/Mist3s)

