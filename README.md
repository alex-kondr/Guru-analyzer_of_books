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
2. create docker-compose.yml a sample file docker-compose.yml
3. docker-compose up
4. open url http://127.0.0.1:8000

### Method 2:

1. gh repo clone alex-kondr/Guru-analyzer_of_books
2. create .env file a sample file .example.env
3. pip install -r requirements.txt
4. py main.py
5. open url http://127.0.0.1:8000
