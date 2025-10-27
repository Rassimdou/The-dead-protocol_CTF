FROM python:3.10-slim
RUN apt-get update && apt-get install -y libcurl4-openssl-dev gcc && \
    pip install flask pycurl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
CMD ["python", "app.py"]