# Django Structlog

- Complete reference [here](https://github.com/jrobichaud/django-structlog)
```
>>> import structlog
>>> logger = structlog.get_logger("plaid")
>>> logger.info("public-token exchange success", plaid_request_id="idhere")
```

- Results into

```
timestamp='2020-03-21T12:52:20.826595Z' level='info' event='public-token exchange success' logger='plaid' request_id='bcf4c34b-fa6f-4da0-932b-54dfc454f010' user_id=None ip='127.0.0.1' plaid_request_id='idhere'
```

- Find successful plaid token-exchange


```
$ cat logs/flat_line.log | grep "token_exchange='success'"
```
