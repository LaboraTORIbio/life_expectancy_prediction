FROM python:3.12.3-slim

WORKDIR /app                                                                

COPY "requirements.txt" "./"

RUN pip install -r requirements.txt

COPY "/app" "./app"
COPY "api.py" "./"

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:9696", "api:app"]