#  FOODGRAM 

Дипломный проект 17 спринта факультета бэкенд-разработки 

### Технологии
- Python 3.7
- Django
- API
- Docker
- Nginx

# Описание проекта Foodgram.

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

# Исходники

- В репозитории есть папки frontend, backend, infra, data и docs.

- В папке frontend находятся файлы, необходимые для сборки фронтенда приложения.

- В папке infra — заготовка инфраструктуры проекта: конфигурационный файл nginx и docker-compose.yml.

- В папке backend описан бэкенд проекта

- В папке data подготовлен список ингредиентов с единицами измерения. Список сохранён в форматах JSON и CSV: данные из списка будет необходимо загрузить в базу.

- В папке docs — файлы спецификации API.

# Запуск проекта

Проект запускается при помощи Docker-контейнеров.

Параметры запуска описаны в файлах docker-compose.yml и nginx.conf которые находятся в директории infra/.

- Создайте в этой же директории .env файл со следующим описанием:

  ```
  DB_ENGINE=django.db.backends.postgresql
  DB_NAME=postgres
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres
  DB_HOST=db
  DB_PORT=5432
  ```

- Команда для создания контейнеров:
     - nginx
     - frondend
     - backend
     - db

    ```
    docker-compose up -d --build
    ```
    
 - После создания контейнров необходимо выполнить миграции следующей командой:
    ```
    sudo docker-compose exec backend python manage.py migrate
    ```
    
  - Также необходимо создать суперпользователя, собрать статику и наполнить базу данных заготовленными ингредиентами:

    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    sudo docker-compose exec backend python manage.py fill_db
    ```
