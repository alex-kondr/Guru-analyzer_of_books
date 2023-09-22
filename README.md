# Welcome to Guru-analyzer of books

### Application features:
1. accepts a document of these types: pdf, doc, docx, txt or downloads a text from a link and analyzes it
2. gives a summary of the document
3. can conduct a dialogue on downloaded documents
4. saves dialogue history
5. summarizes the conversation
6. conduct a dialogue on topics that are not included in the document

# Installing the application

### Method 1:

1. docker pull alexkondr/guru-analyzer_of_books
2. create docker-compose.yml:
    version: '3.9'
    services:
      app:
        image: alexkondr/guru-analyzer_of_books:latest
        ports:
          - "8000:8000"
        environment:
          SQLALCHEMY_DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
          SECRET_KEY: ${SECRET_KEY}
          ALGORITHM: ${ALGORITHM}
          HUGGINGFACEHUB_API_TOKEN: ${HUGGINGFACEHUB_API_TOKEN}
          OPENAI_API_KEY: ${OPENAI_API_KEY}

3. docker-compose up
4. open url http://127.0.0.1:8000

### Method 2:

1. gh repo clone alex-kondr/Guru-analyzer_of_books
2. create .env file a sample file .example.env
    POSTGRES_DB=
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_PORT=
    POSTGRES_HOST=

    SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

    SECRET_KEY=
    ALGORITHM=

    HUGGINGFACEHUB_API_TOKEN=
    OPENAI_API_KEY=

3. pip install -r requirements.txt
4. py main.py
5. open url http://127.0.0.1:8000
