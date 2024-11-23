from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy.types import String, TypeDecorator

Column = mapped_column

metadata_obj = MetaData()

BaseModel = declarative_base(metadata=metadata_obj)


class StrEnum(TypeDecorator):
    impl = String

    def __init__(self, enumtype, *args, **kwargs):
        super(StrEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
