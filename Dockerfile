FROM python:latest

WORKDIR /usr/src/proxy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "-c", "gunicorn -w 1 --threads 2 -b 0.0.0.0:${LISTEN_PORT} --timeout 0 proxy:app"]
