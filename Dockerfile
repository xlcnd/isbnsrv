FROM python:3.7-alpine
RUN apk add --update --no-cache \
    g++ \
    gcc \
    libffi-dev \
    && rm -rf /var/cache/apk/*
WORKDIR /isbnsrv
COPY isbnsrv /isbnsrv
COPY requirements.txt /isbnsrv
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del \
    g++ \
    gcc \
    libffi-dev
ENV SERVICE_NAME "isbnsrv"
EXPOSE 8080
ENTRYPOINT ["python3", "/isbnsrv/aiohttp_server.py"]
