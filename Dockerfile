FROM python:3.7-alpine
LABEL maintainer="xlcnd@outlook.com"
COPY *.txt /isbnsrv/
WORKDIR /isbnsrv
RUN apk add --update --no-cache \
        g++ \
        libffi-dev \
        curl \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del \
        g++ \
        gcc \
        libffi-dev
COPY isbnsrv /isbnsrv/isbnsrv
ENV SERVICE_NAME "isbnsrv"
ENV PORT 8080
EXPOSE 8080
HEALTHCHECK CMD curl -f http://localhost:8080/api/v1/7E2 || exit 1
ENTRYPOINT ["python3"]
CMD ["-c", "from isbnsrv.server import run; run()"]
