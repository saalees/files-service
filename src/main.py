import os
from hashlib import sha256
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, UploadFile
from sqlalchemy import select

from database.schema import Bucket, File
from database.session import DatabaseSessionDependency
from env import env
from utils import generate_uuid, get_bucket_path, get_file_path

app = FastAPI()


@app.post("/buckets")
def create_bucket(
	name: Annotated[str, Form()],
	session: DatabaseSessionDependency,
):
	bucket_id = generate_uuid()
	bucket_path = get_bucket_path(bucket_id=bucket_id)
	os.mkdir(bucket_path)

	try:
		bucket = Bucket(id=bucket_id, name=name)
		session.add(bucket)
		session.commit()
	except Exception as exception:
		os.rmdir(bucket_path)
		raise exception


@app.post("/buckets/{bucket_name}")
def upload_file(
	bucket_name: str,
	file: UploadFile,
	session: DatabaseSessionDependency,
):
	if file.filename is None:
		raise HTTPException(status_code=400, detail="File name could not be determined")

	if file.size is None:
		raise HTTPException(status_code=400, detail="File size could not be determined")

	bucket_id = session.scalar(select(Bucket.id).where(Bucket.name == bucket_name))
	if bucket_id is None:
		raise HTTPException(status_code=404, detail="Bucket not found")

	file_id = generate_uuid()
	file_hash = sha256()
	file_path = get_file_path(bucket_id=bucket_id, file_id=file_id)
	with open(file_path, mode="xb") as output_file:
		while chunk := file.file.read(env.file_chunk_size):
			output_file.write(chunk)
			file_hash.update(chunk)

	try:
		database_file = File(
			id=file_id,
			name=file.filename,
			mime_type=file.content_type,
			size=file.size,
			checksum=file_hash.hexdigest(),
			bucket_id=bucket_id,
		)
		session.add(database_file)
		session.commit()
	except Exception as exception:
		os.remove(file_path)
		raise exception
