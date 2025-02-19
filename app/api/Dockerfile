FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y libomp-dev

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.api.main:app", "--host", "localhost", "--port", "8001"]