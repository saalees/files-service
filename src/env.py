from os.path import isdir

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Env(BaseSettings):
	buckets_dir: str = ".buckets"
	database_user: str | None = None
	database_password: str | None = None
	database_host: str = "localhost"
	database_port: int = 5432
	database_name: str = ""
	file_chunk_size: int = 1024 * 8

	model_config = {
		"env_file": ".env",
	}

	@field_validator("buckets_dir")
	@classmethod
	def validate_buckets_dir(cls, value: str) -> str:
		if not isdir(value):
			raise ValueError(f"{value} is not a directory")

		return value

	@field_validator("database_name")
	@classmethod
	def validate_database_name(cls, value: str) -> str:
		if value == "":
			raise ValueError("DATABASE_NAME environment variable is missing")

		return value


env = Env()
