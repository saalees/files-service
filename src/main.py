import os
from hashlib import file_digest
from shutil import copyfileobj
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select

from constants import HASHING_ALGORITHM
from database.schema import Bucket, File
from database.session import DatabaseSessionDependency
from env import env

app = FastAPI()


@app.post("/buckets")
def create_bucket(
	id: Annotated[str, Form(min_length=1)],
	session: DatabaseSessionDependency,
):
	try:
		bucket_path = os.path.join(env.buckets_dir, id)
		os.mkdir(bucket_path)
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Bucket already exists")

	try:
		bucket = Bucket(id=id)
		session.add(bucket)
		session.commit()
	except Exception as exception:
		os.rmdir(bucket_path)
		raise exception


@app.post("/buckets/{bucket_id}/files")
def upload_file(
	bucket_id: str,
	file: UploadFile,
	session: DatabaseSessionDependency,
):
	if file.filename is None:
		raise HTTPException(status_code=400, detail="File name could not be determined")

	bucket_path = os.path.join(env.buckets_dir, bucket_id)
	if not os.path.exists(bucket_path):
		raise HTTPException(status_code=404, detail="Bucket not found")

	file_id = uuid4()
	file_path = os.path.join(bucket_path, str(file_id))
	with open(file_path, mode="xb") as f:
		copyfileobj(file.file, f, length=env.file_chunk_size)

	try:
		with open(file_path, mode="rb") as f:
			checksum = file_digest(f, HASHING_ALGORITHM).hexdigest()

		database_file = File(
			id=file_id,
			name=file.filename,
			mime_type=file.content_type,
			size=file.size,
			checksum=checksum,
			bucket_id=bucket_id,
		)
		session.add(database_file)
		session.commit()
	except Exception as exception:
		os.remove(file_path)
		raise exception


@app.get("/buckets/{bucket_id}/files/{file_name}")
def get_file(bucket_id: str, file_name: str, session: DatabaseSessionDependency):
	database_file = session.scalar(
		select(File).where(File.bucket_id == bucket_id, File.name == file_name)
	)
	if database_file is None:
		raise HTTPException(status_code=404, detail="File not found")

	file_path = os.path.join(
		env.buckets_dir, database_file.bucket_id, str(database_file.id)
	)
	with open(file_path, "rb") as f:
		checksum = file_digest(f, HASHING_ALGORITHM).hexdigest()

	if checksum != database_file.checksum:
		raise HTTPException(status_code=500)

	return FileResponse(
		path=file_path,
		media_type=database_file.mime_type,
		filename=database_file.name,
	)
