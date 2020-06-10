## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from typing import Iterator, Union

import scrapy
from scrapy import Item, Request, Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Response
% if use_rabbit:

from pika.spec import BasicProperties
from rabbitmq import RabbitSpider
% endif
<%
    ancestors = ["Spider"]
    if use_rabbit:
        ancestors.append("RabbitSpider")

    ancestors = ", ".join(ancestors)
%>

class ${class_name}(${ancestors}):
    name = "${spider_name}"

    custom_settings = {}

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self, *args, **kwargs):
        Spider.__init__(self, *args, **kwargs)
        % if use_rabbit:
        RabbitSpider.__init__(self, *args, **kwargs)
        % endif

    % if use_rabbit:
    def prepare_request(self, method, header_frame: BasicProperties, body: str) -> Request:
        pass

    % endif
    def start_requests(self) -> Iterator[Request]:
        % if use_rabbit:
        yield self.next_request()
        % else:
        pass
        % endif

    def parse(self, response: Response) -> Iterator[Union[Item, Request]]:
        pass

    def spider_closed(self) -> None:
        % if use_rabbit:
        self.channel.close()
        self.connection.close()
        % else:
        pass
        % endif
