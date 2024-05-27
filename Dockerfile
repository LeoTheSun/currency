FROM python:3.9.19-alpine3.20

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

EXPOSE 8080

COPY /src /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]