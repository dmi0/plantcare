FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN apt-get update && apt-get install -y bluez && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY plantcare.py .
CMD [ "python3", "./plantcare.py" ]
