.PHONY: docker-start docker-stop docker-ssh docker-db \
docker-account docker-init docker-lint docker-migrate docker-test docker-typecheck \
account init lint migrate test typecheck

# controlling docker

docker-start:
	docker-compose up -d --build

docker-stop:
	docker-compose stop

docker-ssh:
	docker-compose run -p 8000:8000 app bash

docker-db:
	docker-compose run database

# docker wrappers

docker-account: docker-start
	docker-compose run app bash ./scripts/wait-for database:5432 -- make account

docker-init: docker-start
	docker-compose run app bash ./scripts/wait-for database:5432 -- make init

docker-lint: docker-start
	docker-compose run app make lint

docker-migrate: docker-start
	docker-compose run app bash ./scripts/wait-for database:5432 -- make migrate

docker-test: docker-start
	docker-compose run app bash ./scripts/wait-for database:5432 -- make test

docker-typecheck: docker-start
	docker-compose run app make typecheck

# app commands

account:
	@echo '** If running locally make sure you do `make docker-db` in a separate terminal **'
	python manage.py createsuperuser

init: migrate account

lint:
	flake8 .

migrate:
	@echo '** If running locally make sure you do `make docker-db` in a separate terminal **'
	python manage.py migrate

test:
	@echo '** If running locally make sure you do `make docker-db` in a separate terminal **'
	python manage.py test

typecheck:
	mypy .

coverage:
	coverage run manage.py test && coverage html && coverage report
