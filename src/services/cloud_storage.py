import requests
from pathlib import Path

from src.conf import constants


async def upload_file(file_path: Path | str) -> None:
    with open(file_path, "rb") as file:
        requests.post(url="https://fat-lory-alex-kondr.koyeb.app/",
                      files={"file": file})


async def download_file(file_name: str) -> None:
    response = requests.get(url=f"https://fat-lory-alex-kondr.koyeb.app/?file_name={file_name}")
    with open(constants.VECTOR_DB_PATH / file_name, "wb") as f:
        f.write(response.content)
