import os
from contextlib import asynccontextmanager
from hashlib import file_digest
from shutil import copyfileobj
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select

from constants import HASHING_ALGORITHM
from database.schema import Bucket, File
from database.session import DatabaseSessionDependency
from env import env


@asynccontextmanager
async def lifespan(app: FastAPI):
	os.makedirs(env.buckets_dir, exist_ok=True)
	yield


app = FastAPI(lifespan=lifespan)


@app.post("/buckets")
def create_bucket(
	id: Annotated[str, Form(min_length=1)],
	session: DatabaseSessionDependency,
):
	bucket_path = os.path.join(env.buckets_dir, id)
	try:
		os.mkdir(bucket_path)
		bucket = Bucket(id=id)
		session.add(bucket)
		session.commit()
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Bucket already exists")
	except Exception as exception:
		try:
			os.rmdir(bucket_path)
		except FileNotFoundError:
			pass

		raise exception


@app.post("/buckets/{bucket_id}/files")
def upload_file(
	bucket_id: str,
	file: UploadFile,
	session: DatabaseSessionDependency,
):
	if file.filename is None:
		raise HTTPException(status_code=400, detail="File name could not be determined")

	file_path = os.path.join(env.buckets_dir, bucket_id, file.filename)
	try:
		with open(file_path, mode="xb+") as f:
			copyfileobj(file.file, f)

		with open(file_path, mode="rb") as f:
			checksum = file_digest(f, HASHING_ALGORITHM).hexdigest()

		database_file = File(
			id=file.filename,
			mime_type=file.content_type,
			size=file.size,
			checksum=checksum,
			bucket_id=bucket_id,
		)
		session.add(database_file)
		session.commit()
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Bucket not found")
	except FileExistsError:
		raise HTTPException(status_code=409, detail="File already exists")
	except Exception as exception:
		try:
			os.remove(file_path)
		except FileNotFoundError:
			pass

		raise exception


@app.get("/buckets/{bucket_id}/files/{file_id}")
def get_file(bucket_id: str, file_id: str, session: DatabaseSessionDependency):
	try:
		file_path = os.path.join(env.buckets_dir, bucket_id, file_id)
		with open(file_path, "rb") as f:
			checksum = file_digest(f, HASHING_ALGORITHM).hexdigest()
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")

	database_file = session.scalar(
		select(File).where(File.bucket_id == bucket_id, File.id == file_id)
	)

	if database_file is None:
		raise HTTPException(status_code=404, detail="File not found")

	if checksum != database_file.checksum:
		raise HTTPException(status_code=500)

	return FileResponse(
		path=file_path,
		media_type=database_file.mime_type,
		filename=database_file.id,
	)
