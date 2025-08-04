FROM python:3.12.11

EXPOSE 80

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "app.py"]