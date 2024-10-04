from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, func
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
	__table_args__ = (
		UniqueConstraint("name", "bucket_id", name="files_name_bucket_id_uc"),
	)

	id: Mapped[UUID] = mapped_column(primary_key=True)
	name: Mapped[str]
	mime_type: Mapped[str | None]
	size: Mapped[int | None]
	checksum: Mapped[str]
	bucket_id: Mapped[str] = mapped_column(ForeignKey("buckets.id"), primary_key=True)
	created_at: Mapped[datetime] = mapped_column(server_default=func.now(), init=False)
	bucket: Mapped["Bucket"] = relationship(back_populates="files", init=False)
