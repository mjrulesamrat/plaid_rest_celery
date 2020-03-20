from __future__ import absolute_import, unicode_literals

from plaid.errors import APIError, RateLimitExceededError

from plaid_rest_celery.celery import app


# BTW bind=True is helpful to restart this task in case it is failed
@app.task(
    bind=True,
    default_retry_delay=60*2,
    max_retries=5
)
def token_exchange(self):
    try:
        # plaid API call here
        pass
    except APIError as exc:
        # Retry in 5 minutes.
        raise self.retry(exc=exc)


@app.task(bind=True)
def fetch_accounts_data(self):
    try:
        # plaid API call here
        pass
    except RateLimitExceededError as exc:
        # Retry in 5 minutes.
        raise self.retry(countdown=60 * 5, exc=exc)
