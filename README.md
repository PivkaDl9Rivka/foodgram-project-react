## FoodGram - Продуктовый помощник
![Результат выполнения workflows](https://github.com/PivkaDl9Rivka/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
### Описание:
В FoodGram пользователи могут создавать свои рецепты, подписываться на рецепты других пользователей, добавлять понравившиеся рецепты в Избранное, а также есть возможность скачать список необходимых продуктов для приготовления одного или нескольких желаемых блюд.
### Технологии :
* Python
* Django
* DjangoREST  
* Gunicorn
* PostgreSQL
* Nginx
* Docker
### Как запустить проект:
1. Склонировать репозиторий в командной строке:
```bash
https://github.com/PivkaDl9aRivka/foodgram-project-react.git
```
Затем перейдите в корневую директорию проекта:
```bash
cd  foodgram-project-react/
```
2. В директории infra/ необходимо создать файл .env, и заполните его по примеру:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<ваш_пароль>
DB_HOST=foodgram_db
DB_PORT=5432
SECRET_KEY=<секретный_ключ_проекта>
```
3. 
В директории infra/ необходимо запустить docker-compose, используя команду:

```bash
docker compose  up  -d
```
4. Создайть миграции командой:
```bash
docker-compose  exec  web  python  manage.py  migrate
```
5. Подгрузить статику:
```bash
docker-compose  exec  web  python  manage.py  collectstatic  --no-input
```
6. При необходимости создайте супер пользователя:
```bash
docker-compose  exec  web  python  manage.py  createsuperuser
```
7. Залейте базовые фикстуры (теги рецептов и ингредиенты к ним):
```bash
docker-compose  exec  web  python  manage.py  load_tags
docker-compose  exec  web  python  manage.py  load_ingredients
```

Рабочий проект развёрнут по адресу `http://foodgramforall.ddns.net/`:
- http://foodgramforall.ddns.net/admin/ - админка.

### Автор:
Паранин Максим
