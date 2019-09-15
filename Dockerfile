FROM node:lts-alpine as build-stage

COPY ./FlairBotMgmt /FlairBotMgmt
WORKDIR /FlairBotMgmt/static

RUN npm install webpack && npm install extract-text-webpack-plugin && npm install && npm run build



FROM python:3.7-alpine3.7

COPY ./praw.ini /FlairBot/praw.ini
COPY ./FlairBotMgmt /FlairBot/FlairBotMgmt

WORKDIR /FlairBot/FlairBotMgmt

ENV TZ America/Chicago

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev&& \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY --from=build-stage /FlairBotMgmt/static/dist /static/dist

WORKDIR /FlairBot
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "FlairBotMgmt:app"]
