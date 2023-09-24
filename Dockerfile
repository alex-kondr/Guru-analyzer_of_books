FROM python:3.9

WORKDIR /app

COPY src /app/src
COPY static /app/static
COPY templates /app/templates
COPY main.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]