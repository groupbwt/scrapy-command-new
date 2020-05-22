## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, Date, DateTime,
                        Float, ForeignKey, Integer, String, Text, func, text)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import JSONSerializable, MysqlPrimaryKeyMixin, MysqlTimestampsMixin


class ${class_name}(Base, JSONSerializable, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "${table_name}"

    # TODO
    pass
