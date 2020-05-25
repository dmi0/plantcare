FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt *.py ./
RUN apk upgrade --update-cache --available && \
    apk add make pkgconfig glib-dev gcc libc-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del make pkgconfig gcc libc-dev py-pip && \
    rm -rf /var/cache/apk/* ~/.cache/pip

CMD [ "python3", "./plantcare.py" ]