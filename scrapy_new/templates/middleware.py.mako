## -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from scrapy import Request, Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Response


class ${class_name}:
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_request(self, request: Request, spider: Spider) -> None:
        return None

    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Response:
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ) -> None:
        pass

    def spider_opened(self, spider: Spider) -> None:
        pass
