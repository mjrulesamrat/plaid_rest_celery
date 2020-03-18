# Plaid API with Django Rest & Celery

"Few crazy out there who are willing to change the world will change it"

## Local Installation Guideline:

- Clone repository

```
git clone git@github.com:mjrulesamrat/plaid_rest_celery.git
```

- go to project directory

```
cd plaid_rest_celery
```

- Create Virtual Environment and install dependencies with [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/install.html#installing-pipenv)

```
pipenv install
```

- Activate virtualenv

```
pipenv shell
```

- Setup settings file

```
cp plaid_rest_celery/settings/example-staging.py plaid_rest_celery/settings/staging.py
```

- Run migrations

```
python manage.py migrate
```

- Run project locally

```
python manage.py runserver
```

## Admin panel

```
localhost:8000/plaid-admin/
```

## API docs using [drf-yasg](https://drf-yasg.readthedocs.io/en/latest/readme.html)

- You'll need to login to admin panel first to access API docs
```
localhost:8000/api/v1/docs/
```

## Celery local setup

- start celery worker

```
celery -A plaid_rest_celery worker --loglevel=info
```
