FROM python:3.12-alpine

ENV PYTHONUNBUFFERES=1

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -U pip && \
    pip3 install -r /app/requirements.txt

COPY . .
CMD ["python3", "main.py"]
