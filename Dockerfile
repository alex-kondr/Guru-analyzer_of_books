FROM python:3.10.12

WORKDIR /app

COPY src /app/src
COPY static /app/static
COPY templates /app/templates
COPY driver /app/driver
COPY main.py /app
COPY requirements.txt /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]