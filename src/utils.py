from os import path
from uuid import UUID, uuid4

from env import env


def generate_uuid() -> UUID:
	return uuid4()


def get_bucket_path(bucket_id: UUID) -> str:
	return path.join(env.buckets_dir, str(bucket_id))


def get_file_path(bucket_id: UUID, file_id: UUID) -> str:
	return path.join(env.buckets_dir, str(bucket_id), str(file_id))
