from sqlalchemy import URL

from env import env


def get_database_url() -> URL:
	return URL.create(
		drivername="postgresql+psycopg",
		username=env.database_user,
		password=env.database_password,
		host=env.database_host,
		port=env.database_port,
		database=env.database_name,
	)
