# Foodgram[https://github.com/elValeron/foodgram-project-react.git]
## Foodgram - Место где Ты можешь поделится своим любимым рецептом!

Бэкэнд стэк:
Django 3.2
Django-rest-framework 3.12
Djoser
Проект реализован с помощью сервиса контейниризации Docker.
В сервисе задействованы стандартные контейнеры Docker:
nginx 1.19.3
Postgres 3.10

1. ### Запуск сервиса в докер контейнерах:
    - На виртуальной машине, сервере или локально создайте директорию в которой будет хранится проект
        _ Перейдите в директорию infra, запуск сервиса в докер контейнерах необходимо выполнять из этой директории
        _ Создайте по шаблону env_example собственный файл (.env), с данными для подключения к бд
        _ Выполните команду sudo docker compose -f docker-compose.yml up -d 
        _ После запуска сервиса необходимо загрузить данные ингредиентов командой:
            - sudo docker compose -f docker-compose.yml exec backend python manage.py load_csv ingredients.csv
        ### Поздравляю! Можно приступить к работе с сервисом!





Перейти в домашний каталог:
cd ~/
Создание директории:
mkdir kittygram/
Отключиться от сервера:
exit
```
Для начала работы необходимо клонировать репозиторий на локальный компьютер
```
https://github.com/elValeron/kittygram_final.git
```
Перейти в папку /kittygram_final
```
cd kittygram_final/
```
Скопировать файл docker-compose.production.yml на виртуальный сервер командой:
```
sudo scp -i n\
 <путь до файла с ssh>/<файл с ssh> docker-compose.production.yml n\
 <user>@<ip-сервера>:~/kittygram/
```
Создать и открыть файл .env: 
```
touch .env
sudo nano .env
```
Добавить переменные:
```
POSTGRES_USER=Админ для контейнера с бд в Docker'e
POSTGRES_PASSWORD=пароль для пользователя в контейнере с бд в Docker'e
POSTGRES_DB=Название БД для контейнера Docker
DB_NAME=Имя БД к которой надо подключится 
DB_HOST=Имя контейнера в которой находится бд 
DB_PORT=Порт через который необходимо подключаться к бд
SECRET_KEY=Секретный ключ Django для файла settings.py
ALLOWED_HOSTS=список хостов для подключения.
```
Скопировать файл .env на сервер командой:
```
sudo scp -i 
 <путь до файла с ssh>/<файл с ssh> .env 
 <user>@<ip-сервера>:~/kittygram/
```
Подключиться к серверу и запустить файл docker-compose.production.yml:
```
cd ~/kittygram/
sudo docker compose -f docker-compose.production.yml up -d
```

Author @elValeron