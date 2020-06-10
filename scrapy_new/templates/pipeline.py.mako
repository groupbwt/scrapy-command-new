## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from scrapy import Item, Spider

% if use_rabbit:
from helpers import PikaBlockingConnection, mysql_connection_string
% else:
from helpers import mysql_connection_string
% endif
% if item_class:
from items import ${item_class}
% endif
from sqlalchemy import create_engine
from sqlalchemy.exc import DataError, IntegrityError, InvalidRequestError
from sqlalchemy.orm import Session


class ${class_name}:
    def __init__(self):
        self.engine = create_engine(mysql_connection_string())
        % if use_rabbit:
        self.connection = None
        self.channel = None
        % endif

    def open_spider(self, spider: Spider) -> None:
        % if use_rabbit:
        queue_name = spider.settings.get("SAVER_QUEUE")
        rabbitmq = PikaBlockingConnection(queue_name, spider.settings)
        self.connection = rabbitmq.rabbit_connection
        self.channel = rabbitmq.rabbit_channel
        self.channel.queue_declare(queue=queue_name, durable=True)
        % else:
        pass
        % endif

    def process_item(self, item: Item, spider: Spider) -> Item:
        % if item_class:
        if isinstance(item, ${item_class}):
            pass  # TODO process item
        % endif
        return item

    def close_spider(self, spider: Spider) -> None:
        % if use_rabbit:
        self.channel.close()
        self.connection.close()
        % else:
        pass
        % endif
