FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

COPY src /app/src
COPY main.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN python3 -m spacy download en_core_web_sm

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]