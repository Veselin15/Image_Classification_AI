release: python manage.py migrate --skip-checks
web: gunicorn Image_Classification_AI.wsgi --timeout 120 --log-file -