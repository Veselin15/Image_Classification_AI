release: python manage.py migrate --skip-checks && python manage.py collectstatic --noinput
web: gunicorn Image_Classification_AI.wsgi --timeout 120 --log-file -