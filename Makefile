test:
	pytest tests

run:
	python run.py

migrate:
# 	$env:FLASK_APP="app:create_app('default')"
	flask db migrate -m "Initial migrate"
	flask db upgrade

freeze:
	pip freeze > requirements.txt


remove-migration:
	Remove-Item -Recurse -Force migrations