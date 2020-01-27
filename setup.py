# -*- coding: utf-8 -*-
import setuptools


setuptools.setup(
    entry_points={"scrapy.commands": ["new=scrapy_new.new:NewCommand"]},
)
