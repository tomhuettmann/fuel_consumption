FROM python:3.8-alpine

COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app/

ENTRYPOINT ["python3", "app.py"]

#docker run --name fuel_consumption -d -p 127.0.0.1:5001:5000 fuel_consumption
