SHELL := /bin/bash

.PHONY: up down build logs migrate superuser collectstatic shell restart

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

superuser:
	docker compose exec web python manage.py createsuperuser

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

shell:
	docker compose exec web python manage.py shell

restart:
	docker compose down && docker compose up -d
