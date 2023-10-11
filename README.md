![Foodgram](https://img.shields.io/badge/foodgram-passing-purple)
# [Продуктовый помошник](https://elfood.ddns.net/)

# Описание: 
    - Продуктовый помошник - сервис в котором пользователи могут делится своими рецептами.
    
    - Функционал сервиса позваляет подписываться на понравившихся автором, добавлять рецепты в избранное, и пожалуй одно из главных конкурентных преимуществ данного сервиса, возможность скачать список продуктов для рецепта в универсальном формате .txt.

# Стэк: 
Сервис реализован на языке программирования Python 3.9 и веб-фреймворках Django 3.14 и Django REST framework 3.12. Авторизация реализована с помощью пакета Djoser 2.1. 
Проект реализован с помощью сервиса контейниризации Docker.
Документация к сервису доступна по ссылке http://localhost/api/docs/

1. ### Запуск сервиса в докер контейнерах:
    - На виртуальной машине, сервере или локально создайте директорию в которой будет хранится проект
        
        - Перейдите в каталог, в котором хранится проект, командой:
            ```
            - cd <dir_name>/
            ```
        - Склонируйте репозиторий командой:
            ```
            - git clone https://github.com/elValeron/foodgram-project-react.git
            ```
        - Создайте по шаблону env_example собственный файл (.env), с данными для подключения к бд:
            ```
            - POSTGRES_USER=exampleuser* - имя пользователя контейнера с бд в Docker
            - POSTGRES_PASSWORD=E3x7a5m11p3l19e* - пароль для пользователя для подключения к БД
            - POSTGRES_DB=ExampleBD* - Название базы данных 
            - DB_HOST=example-db-1* - Имя контейнера с бд 
            - DB_PORT=1234* - Порт по которому бэкэнд будет обращатся к бд
            - SECRET_KEY=Секретный ключ Django приложения
            - ALLOWED_HOSTS=Разрешенные хосты с которыми сможет взаимодействовать Django
            ```
            *данные указаны для примера
        - Скачайте контейнеры с DockerHub'a командой:
            ```
            - sudo docker compose -f docker-compose.production.yml pull
            ```
        - Выполните команду для запуска сервиса в контейнерах:

            ```
            - sudo docker compose -f docker-compose.yml up -d 
            ```
        - Для корректного отображения информации необходимо скопировать папку collected_static командой:
        ```
        - sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
        ```
        ### Поздравляю! Можно приступить к работе с сервисом!
        
2. ### Запуск сервиса для отладки: 
    - На локальной машине создайте директорию в которой будет хранится проект
        - Перейдите в каталог, в котором хранится проект, командой:
            ```
            - cd <dir_name>/
            ```
        - Склонируйте репозиторий командой:
            ```
            - git clone https://github.com/elValeron/foodgram-project-react.git
            ```
        - Перейдите в директорию backend/ и установите виртуальное окружение командами:
            ```
            - cd backend/
            ```
            Виртуальное окружение для win:
            ```
            - python -m venv venv 
            ```
            Виртуальное окружение для Linux\Mac:
            ```
            - python3.9 -m venv venv
            ```
        - Активируйте виртуальное окружение и установите зависимости командами:
            Для Linux/Mac:
            ```
            - source venv/bin/activate
            - pip install -r requirements.txt
            ```
            Для win:
            ```
            - source venv/Script/activate
            - pip install -r requirements.txt
            ```
        - создать файл .env с переменными DEBUG=True и CHECKOUT=True для подключение к БД SQLite
        - Перейдите в директорию backend/foodgram и создайте и примените миграции командами:
            ```
            - python manage.py makemigrations
            - python manage.py migrate
            ```
        - Загрузите данные из файла ingredients.csv командой:
            ```
            - python manage.py load_csv ingredients.csv
            ```
        ### Поздравляю, проект готов к дебагу, удачи! :+1:

[Документация](https://elfood.ddns.net/api/docs/)
Автор [elValeron](https://github.com/elValeron/)