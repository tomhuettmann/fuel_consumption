FROM python:3.8-alpine

COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app/

ENTRYPOINT ["python3", "app.py"]
