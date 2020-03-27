# Plaid API with Django Rest & Celery

"Few crazy out there who are willing to change the world will change it"

## TLDR;

```
git clone git@github.com:mjrulesamrat/plaid_rest_celery.git

cd plaid_rest_celery

chmod +x app/entrypoint.sh

# most of default should work fine for quick demo except plaid keys & sentry
cp .env.example .env

cp plaid_rest_celery/settings/example-staging.py plaid_rest_celery/settings/staging.py

docker-compose up -d --build

docker-compose exec web python manage.py migrate --noinput

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --noinput

# Cleanup:
docker-compose down -v  # down and remove volumes
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

## Flower monitoring(Tested within docker)

- Basic auth creds, `admin/admin` or `foo/bar`
```
http://localhost:7775/
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
celery flower -A plaid_rest_celery --address=127.0.0.1 --port=7775
```

## Update requirements

Update requirements from Pipfile to `requirements.txt`. Everytime we do `pipenv install`, make sure to update `requirements.txt`

    pipenv lock -r > requirements.txt

## Logging

- Go to logs [README](logs/README.md)

# Testing guidelines (Tested with already created user, login to logout)

## 1. Login(Token authentication)

* Get access-token
```
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:7777/api/v1/auth/token/login/
```

* response (Use this token in further requests)

```
{"auth_token":"dddad1111Example_token8218132251b"}
```

## 2. Get public token of customer from plaid

* Get Public token by running sandbox mode [plaid-python-quickstart](https://github.com/plaid/quickstart/tree/master/python)

## 3. Create an Item

* Send public token to create new item (Add user's plaid account)

```
curl -X POST -H "Authorization: Token dddad1111Example_token8218132251b" -d '{"public_token": "token"}' http://localhost:7777/api/v1/plaid/create-item/
```

## 4. Let the magic happen!

* background celery tasks will fetch access_token and item_id

* Then, it'll fetch and save item metadata

* then, it'll fetch and save accounts for given item

* At last, it'll fetch last 30 days transactions data for given item

## 5. Get Accounts information

```
curl -X GET -H "Authorization: Token dddad1111Example_token8218132251b" http://localhost:7777/api/v1/plaid/accounts/
```


## 6. Get transactions

```
curl -X GET -H "Authorization: Token dddad1111Example_token8218132251b" http://localhost:7777/api/v1/plaid/transactions/
```

## 7. Logout
```
curl -X POST -H "Authorization: Token dddad1111Example_token8218132251b" http://localhost:7777/api/v1/auth/token/logout/
```
