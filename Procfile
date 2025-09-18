release: FLASK_APP=app.app flask db upgrade
web: gunicorn app.app:app --bind 0.0.0.0:$PORT