import requests
import shutil
from pathlib import Path

from src.conf import constants


async def upload_file(file_path: Path | str) -> None:
    with open(file_path, "rb") as file:
        requests.post(url="https://fat-lory-alex-kondr.koyeb.app/",
                      files={"file": file})


async def download_file(file_name: str) -> None:
    response = requests.get(url=f"https://fat-lory-alex-kondr.koyeb.app/?file_name={file_name}", stream=True)
    with open(constants.VECTOR_DB_PATH / file_name, "wb") as f:
        shutil.copyfileobj(response.raw, f)

# path = Path(constants.VECTOR_DB_PATH / "2.pdf")

# with open(path, "rb") as f:

#
# print(response)
# # print(response.content)
#
# requests.post(url="https://fat-lory-alex-kondr.koyeb.app/",
#               files={"file": open(path, "rb")})
