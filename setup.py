# -*- coding: utf-8 -*-
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapy_new",
    version="0.0.8",
    author="Kristobal Junta",
    author_email="junta.kristobal@gmail.com",
    description="A package providing code generation command for scrapy CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/groupbwt/scrapy-command-new",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    entry_points={"scrapy.commands": ["new=scrapy_new.new:NewCommand"]},
    install_requires=[
        "scrapy",
        "mako",
        "inflection",
    ],
    zip_safe=False,
    include_package_data=True,
)
