FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/temp

COPY . .

ENV PYTHONPATH=/app
ENV PORT=${PORT:-8000}
ENV HOST=${HOST:-::}

EXPOSE 8000

CMD uvicorn app.main:app --host ${HOST} --port ${PORT}