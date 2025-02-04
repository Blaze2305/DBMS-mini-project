FROM python:alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn"  , "-w" , "2", "-b", "0.0.0.0:5000", "app:app"]