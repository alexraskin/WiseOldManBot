FROM python:3.10.8-alpine

WORKDIR /usr/src/app

RUN apk update \
&& apk --no-cache --update add libffi-dev gcc musl-dev linux-headers python3-dev git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "bot/bot.py"]
