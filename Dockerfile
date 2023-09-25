FROM python:3.10.12

WORKDIR /app

COPY src /app/src
COPY static /app/static
COPY templates /app/templates
COPY main.py /app
COPY requirements.txt /app

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz
RUN tar -xzvf geckodriver-v0.32.0-linux64.tar.gz -C /app/bin/geckodriver
RUN chmod +x /app/bin/geckodriver
RUN export PATH=$PATH:/app/bin/geckodriver/
RUN geckodriver -V

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]