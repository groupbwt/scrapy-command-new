## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from sqlalchemy import func, text
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    Date,
    DateTime,
    Text,
    Float,
    TIMESTAMP,
)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT

from .base import Base
from .mixins import JSONSerializable, MysqlPrimaryKeyMixin, MysqlTimestampsMixin


class ${class_name}(Base, JSONSerializable, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "${table_name}"
