# ![Foodgram](https://github.com/elValeron/foodgram-project-react.git)
## Foodgram - Место где Ты можешь поделится своим любимым рецептом!

Бэкэнд стэк:
Python 3.9
Django 3.14
Django-rest-framework 3.12
Djoser
Проект реализован с помощью сервиса контейниризации Docker.
В сервисе задействованы стандартные контейнеры Docker:
nginx 1.19.3
Postgres 3.10

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
        - Перейдите в директорию infra, запуск сервиса в докер контейнерах необходимо выполнять из этой директории
        - Создайте по шаблону env_example собственный файл (.env), с данными для подключения к бд
        - Выполните команду для запуска сервиса в контейнерах:
            ```
            - sudo docker compose -f docker-compose.yml up -d 
            ```
        - После запуска сервиса необходимо загрузить данные ингредиентов командой:
        ```
        - sudo docker compose -f docker-compose.yml exec backend python manage.py load_csv ingredients.csv
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
        - Измените в файле foodgram/foodgram/settings.py значение переменной DEBUG = True для подключение к БД SQLite
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
