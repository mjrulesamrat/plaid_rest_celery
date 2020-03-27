# Plaid API with Django Rest & Celery

"Few crazy out there who are willing to change the world will change it"

## TLDR;

```
git clone git@github.com:mjrulesamrat/plaid_rest_celery.git

cd plaid_rest_celery

chmod +x app/entrypoint.sh

# most of default should work fine for quick demo except plaid keys & sentry
cp .env.example .env

docker-compose up -d --build

docker-compose exec web python manage.py migrate --noinput

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --noinput
```

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

cp .env.example .env

# change user and password at .env.rabbitmq
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

- Start rabbitmq docker (Change user and password at .env.rabbitmq)

```
docker-compose -f docker-compose.rabbitmq.yml up -d

# If connection is refused despite right credenials. Troubleshoot with below commands.
docker exec -it container_id sh
rabbitmqctl list_users | grep user
rabbitmqctl change_password user password  # reset password
```

- start celery workers (Three workers with different queues)

```
celery -A plaid_rest_celery worker -Q flash -c 4 --loglevel=info
celery -A plaid_rest_celery worker -Q default -c 2 --loglevel=info
celery -A plaid_rest_celery worker -Q slow -c 2 --loglevel=info
```

## Update requirements

Update requirements from Pipfile to `requirements.txt`. Everytime we do `pipenv install`, make sure to update `requirements.txt`

    pipenv lock -r > requirements.txt

## Logging

- Go to logs [README](logs/README.md)

# Testing guidelines

## 1. Login(Token authentication)

* Get access-token
```
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:8000/api/v1/auth/token/login/
```

* response (Use this token in further requests)

```
{"auth_token":"036235d3eb26bab988a38e473db3f64cf113fc01"}
```

## 2. Get public token of customer from plaid

* Get Public token by running sandbox [plaid-python-quickstart](https://github.com/plaid/quickstart/tree/master/python)

## 3. Create an Item

* Send public token to create new item (Add user's plaid account)

```
curl -X POST -H "Authorization: Token dddad1111Example_token8218132251b" -d '{"public_token": "token"}' http://localhost:8000/api/v1/plaid/create-item/
```

## 4. Let the magic happen!

* background celery tasks will fetch access_token and item_id

* Then, it'll fetch and save item metadata

* then, it'll fetch and save accounts for given item

* At last, it'll fetch last 30 days transactions data for given item

## 5. Get transactions

```
curl -X POST -H "Authorization: Token dddad1111Example_token8218132251b" http://localhost:8000/api/v1/plaid/transactions/
```

## 6. Logout
```
curl -X POST -H "Authorization: Token dddad1111Example_token8218132251b" http://localhost:8000/api/v1/auth/token/logout/

```
