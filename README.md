# scrapy-command-new

A package providing code generation command for scrapy CLI.

*The project is a WIP, so expect major changes and additions (latter, mostly).
Master branch is to be considered as always ready to use, with major changes/features introduced in feature branches.*

This is a part of a bigger project - [Scrapy Boilerplate](https://github.com/groupbwt/scrapy-boilerplate).

The command works with a specific scrapy project structure (not the default one). Rationale for this is described [here](https://github.com/groupbwt/scrapy-boilerplate#file-and-folder-structure).

## Usage

This is a scrapy command to generate class files and automatically add imports to respective module's `__init__` files. It can be used as follows:

```
scrapy new spider SampleSpider
```

The first argument (`spider`) is a type of class file to be generated, and can be one of the following:

- command
- extension
- item
- middleware
- model
- pipeline
- spider_middleware
- spider

The second argument is class name.

Also for `pipeline` and `spider` class an option `--rabbit` can be used to add RabbitMQ connection code to generated source.

Option `--item` with value `CLASSNAME` is supported for generating pipelines, which adds an import and type-check for a provided item class to the resulting code.

Option `--settings` is also supported for pipelines, with an optional integer value `PRIORITY` that adds the pipeline being generated to scrapy `settings.py` file with specified priority (default 300).

## Installation

This command is included in the [Scrapy Boilerplate](https://github.com/groupbwt/scrapy-boilerplate) out of the box. If you want to install it manually, you can get it from PyPi:

```
pip install scrapy-new
```

**Please note** that this package won't work with default Scrapy project structure, it requires a specific custom one, as described [here](https://github.com/groupbwt/scrapy-boilerplate#file-and-folder-structure).
