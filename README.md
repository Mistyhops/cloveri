# cloveri
В файле test_db.sql содержится скрипт, который необходимо запустить для создания таблицы в базе данных postgresql.

После создания таблицы, надо в файле settings.py добавить настройки базы в параметре DATABASES.

Затем необходимо выполнить команды python3 manage.py makemigrations и python3 manage.py migrate для создания миграций.
