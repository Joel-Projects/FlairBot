FROM node:lts-alpine as build-stage

COPY ./FlairBotMgmt /FlairBotMgmt
WORKDIR /FlairBotMgmt/static

RUN npm install webpack && npm install extract-text-webpack-plugin && npm install && npm run build


FROM python:3.7-alpine

COPY ./praw.ini /FlairBotMgmt/praw.ini
COPY ./FlairBotMgmt /FlairBotMgmt
WORKDIR /FlairBotMgmt

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev nano bash && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY --from=build-stage /FlairBotMgmt/static/dist /static/dist

EXPOSE 5000

CMD ["flask", "run", "--debugger"]