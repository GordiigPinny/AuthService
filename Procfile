release: python manage.py migrate
web: python3 manage.py collectstatic --noinput; daphne AuthService.asgi:application