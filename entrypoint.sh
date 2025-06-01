# Start Migrations processes
echo run Pyarmor

# poetry run pyarmor gen --recursive \
#     --output ../dist/obfuscated_crm_src \
#     --exclude "*/migrations/*" \
#     --exclude "templates/*" \
#     --exclude "static/*" \
#     --exclude "venv/*" \
#     --exclude ".venv/*" \
#     --exclude "*.sqlite3" \
#     --exclude "/tests/*" \
#     --exclude "core/settings.py" \
#     --exclude "*.lock" \
#     --exclude "*.toml" \
#     --exclude "*.git" \
#     --exclude "**/__init__.py" \
#     --exclude "manage.py" \
#     app_accounting app_global app_productions app_users config 


echo Starting  Migrations
poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput

# Start Gunicorn processes
echo Starting Server
poetry run python manage.py runserver 0.0.0.0:8989
