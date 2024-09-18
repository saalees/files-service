from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .utils import get_database_url

database_url = get_database_url()
engine = create_engine(url=database_url)


def get_database_session() -> Generator[Session, None, None]:
	with Session(engine) as session:
		yield session


DatabaseSessionDependency = Annotated[Session, Depends(get_database_session)]
