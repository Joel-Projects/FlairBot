FROM python:3.7-alpine

COPY ./FlairBotMgmt /FlairBotMgmt
WORKDIR /FlairBotMgmt

RUN apk add --no-cache postgresql-libs && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev nano bash && pip install -r requirements.txt && apk --purge del .build-deps

EXPOSE 5000

CMD ["flask", "run", "--debugger"]