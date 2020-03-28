## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from typing import Iterable, Iterator, Union

from scrapy import Item, Request, Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Response


class ${class_name}:
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        return None

    def process_spider_output(
        self, response: Response, result: Iterable[Union[Request, Item]], spider: Spider
    ) -> Iterator[Union[Request, Item]]:
        for i in result:
            yield i

    def process_spider_exception(
        self, response: Response, exception: Exception, spider: Spider
    ) -> None:
        pass

    def process_start_requests(
        self, start_requests: Iterable[Request], spider: Spider
    ) -> Iterator[Request]:
        for r in start_requests:
            yield r

    def spider_opened(self, spider: Spider) -> None:
        pass
