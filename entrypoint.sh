# Start Migrations processes
echo Starting  Migrations
poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput

# Start Gunicorn processes
echo Starting Server
poetry run python manage.py runserver 0.0.0.0:8989
