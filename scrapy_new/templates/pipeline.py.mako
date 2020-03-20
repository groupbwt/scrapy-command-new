## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.exc import DataError, IntegrityError, InvalidRequestError
from sqlalchemy.orm import Session

% if item_class:
from items import ${item_class}
% endif
from helpers import mysql_connection_string
% if use_rabbit:
from helpers import PikaBlockingConnection
% endif


class ${class_name}:
    def __init__(self):
        self.engine = create_engine(mysql_connection_string())
        self.session = None

    def open_spider(self, spider):
        self.session = Session(self.engine)
        % if use_rabbit:

        queue_name = self.settings.get("SAVER_QUEUE")
        rabbitmq = PikaBlockingConnection(queue_name, self.settings)
        self.connection = rabbitmq.rabbit_connection
        self.channel = rabbitmq.rabbit_channel
        self.channel.queue_declare(queue=queue_name, durable=True)
        % endif

    def process_item(self, item, spider):
        % if item_class:
        if isinstance(item, ${item_class}):
            return item

        % endif
        return item

    def close_spider(self, spider):
        % if use_rabbit:
        self.channel.close()
        self.connection.close()
        % endif
        self.session.close()
