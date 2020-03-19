###########
# BUILDER #
###########
# Note: app is plaid

# pull official base image
FROM python:3.6.10-alpine3.11 as builder
MAINTAINER Jay Modi <mjrulesamrat@gmail.com>
# set work directory
WORKDIR /usr/src/plaid

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update && apk add gcc python3-dev musl-dev

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/plaid/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.6.10-alpine3.11

# create directory for the app user
RUN mkdir -p /home/plaid

# create the app user
RUN addgroup -S plaid && adduser -S plaid -G plaid

# create the appropriate directories
ENV HOME=/home/plaid
ENV APP_HOME=/home/plaid/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/assets
WORKDIR $APP_HOME

# install dependencies
RUN apk update
COPY --from=builder /usr/src/plaid/wheels /wheels
COPY --from=builder /usr/src/plaid/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R plaid:plaid $APP_HOME

# change to the app(plaid) user
USER plaid

# run entrypoint.prod.sh
ENTRYPOINT ["/home/plaid/web/entrypoint.sh"]
