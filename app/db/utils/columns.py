from functools import partial

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column

UTCDateTime = partial(
    mapped_column,
    DateTime(timezone=True),
)
