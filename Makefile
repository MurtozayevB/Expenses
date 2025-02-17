mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

admin:
	python3 manage.py createsuperuser


udb:
	rm -rf db.sqlite3
	rm -rf apps/migrations/*
	touch apps/migrations/__init__.py
	python3 manage.py makemigrations
	python3 manage.py migrate

celery:
	celery -A root worker --loglevel=info


