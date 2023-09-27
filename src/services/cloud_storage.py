import aiohttp

import aiofiles

from src.conf import constants


URL = "https://fat-lory-alex-kondr.koyeb.app/"


async def backup_vector_db(document_id: int) -> None:
    file_faiss = constants.VECTOR_DB_PATH / f"{document_id}.faiss"
    file_pkl = constants.VECTOR_DB_PATH / f"{document_id}.pkl"

    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL, data={'file': open(file_faiss, "rb")}):
            pass

    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL, data={'file': open(file_pkl, "rb")}):
            pass


async def recovery_vector_db(document_id: int) -> None:
    file_faiss = constants.VECTOR_DB_PATH / f"{document_id}.faiss"
    file_pkl = constants.VECTOR_DB_PATH / f"{document_id}.pkl"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{URL}?file_name={document_id}.faiss") as resp:
            async with aiofiles.open(file_faiss, "wb") as file:
                await file.write(await resp.content.read())

    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{URL}?file_name={document_id}.pkl") as resp:
            async with aiofiles.open(file_pkl, "wb") as file:
                await file.write(await resp.content.read())
