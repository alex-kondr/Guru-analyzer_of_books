from pathlib import Path

#--> email
EMAIL_MAX__LEN = 50
EMAIL_MIN_LEN = 5

#--> username
USERNAME_MIN_LEN = 5
USERNAME_MAX_LEN = 30

#--> password
PASSWORD_MIN_LEN = 6
PASSWORD_MAX_LEN = 10

#--> first_name
FIRST_NAME_MIN_LEN = 3
FIRST_NAME_MAX_LEN = 20

# format for loaders
FILE_CONTENT_TYPE_PDF = "application/pdf"
FILE_CONTENT_TYPE_TEXT = "text/plain"
FILE_CONTENT_TYPE_DOC = "application/msword"
FILE_CONTENT_TYPE_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
FILE_SUPPORTED_CONTENT_TYPE = [FILE_CONTENT_TYPE_PDF, FILE_CONTENT_TYPE_TEXT, FILE_CONTENT_TYPE_DOC,
                               FILE_CONTENT_TYPE_DOCX]

WORK_PATH = Path("src/model/files")
WORK_PATH.mkdir(exist_ok=True)


