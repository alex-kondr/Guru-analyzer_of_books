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

FILE_TYPE_IS_NOT_SUPPORTED = "File type is not supported"
FILE_SAVED = "File saved"

STATIC = Path("static")
STATIC.mkdir(exist_ok=True)

VECTOR_DB_PATH = STATIC / "vector_db_path"
VECTOR_DB_PATH.mkdir(exist_ok=True)
