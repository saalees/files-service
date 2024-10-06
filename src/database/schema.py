from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
	DeclarativeBase,
	Mapped,
	MappedAsDataclass,
	mapped_column,
	relationship,
)


class Base(DeclarativeBase):
	pass


class Bucket(MappedAsDataclass, Base):
	__tablename__ = "buckets"

	id: Mapped[str] = mapped_column(primary_key=True)
	created_at: Mapped[datetime] = mapped_column(server_default=func.now(), init=False)
	files: Mapped[list["File"]] = relationship(back_populates="bucket", init=False)


class File(MappedAsDataclass, Base):
	__tablename__ = "files"

	id: Mapped[str] = mapped_column(primary_key=True)
	mime_type: Mapped[str | None]
	size: Mapped[int | None]
	checksum: Mapped[str]
	bucket_id: Mapped[str] = mapped_column(ForeignKey("buckets.id"), primary_key=True)
	created_at: Mapped[datetime] = mapped_column(server_default=func.now(), init=False)
	bucket: Mapped["Bucket"] = relationship(back_populates="files", init=False)
