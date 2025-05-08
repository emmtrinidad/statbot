FROM python:3.11

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --default-timeout=100 -r requirements.txt

COPY app/ .

CMD ["python3", "bot.py"]
