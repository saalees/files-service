from pydantic import field_validator
from pydantic_settings import BaseSettings


class Env(BaseSettings):
	buckets_dir: str = ".buckets"
	database_user: str | None = None
	database_password: str | None = None
	database_host: str = "localhost"
	database_port: int = 5432
	database_name: str = ""

	model_config = {
		"env_file": ".env",
	}

	@field_validator("database_name")
	@classmethod
	def validate_database_name(cls, value: str) -> str:
		if value == "":
			raise ValueError("DATABASE_NAME environment variable is missing")

		return value


env = Env()
