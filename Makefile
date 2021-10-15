.PHONY: requirements.txt

setup-and-run:	setup migrate run

venv:
	 python -m venv .venv

run:
	python manage.py runserver 0.0.0.0:8000

migrate:
	python manage.py migrate

dev:
	docker-compose run --service-ports django //bin/bash

install-frac:
	pip install -e /django/bash-shell.net --no-binary :all:

shell:
	docker compose exec django bash

# requirements.txt:
# 	# See https://stackoverflow.com/questions/58843905/what-is-the-proper-way-to-decide-whether-to-allow-unsafe-package-versions-in-pip
# 	# about allow-unsafe. In this case, to pin setuptools.
# 	pip-compile requirements.in --generate-hashes --upgrade --allow-unsafe
