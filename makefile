test:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 pipenv run pytest

xtest:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 pipenv run pytest -v -k $(test)

install:
	LC_ALL=C.UTF-8 LANG=C.UTF-8  pipenv install $(lib)

remove:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 pipenv uninstall $(lib)

setup:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 PIPENV_IGNORE_VIRTUALENVS=1 pipenv install --dev

destroy:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 PIPENV_IGNORE_VIRTUALENVS=1 pipenv --rm --clear

where:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 E_VIRTUALENVS=1 PIPENV_IGNORE_VIRTUALENVS=-1 pipenv --where

freeze:
	LC_ALL=C.UTF-8 LANG=C.UTF-8 PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pip3.7 freeze > requirements.txt