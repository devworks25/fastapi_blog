FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libpq-dev libpq5 \
	&& pip install --no-cache-dir fastapi["all"] "uvicorn[standard]" psycopg2 sqlalchemy \
	&& apt-get purge -y --auto-remove build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY app ./app

EXPOSE 8052

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8052"]
