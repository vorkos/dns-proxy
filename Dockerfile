FROM python:3.10-alpine

WORKDIR /usr/local/bin
COPY dns-proxy.py .
EXPOSE 53

ENTRYPOINT ["python","dns-proxy.py"]
