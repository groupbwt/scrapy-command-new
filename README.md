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
- spider

The second argument is class name.

Also for `pipeline` and `spider` class an option `--rabbit` can be used to add RabbitMQ connection code to generated source.

Option `--item` with value `CLASSNAME` is supported for generating pipelines, which adds an import and type-check for a provided item class to the resulting code.

Option `--settings` is also supported for pipelines, extension, middlewares and spider middlewares. It has an optional integer value `PRIORITY` that adds specified priority. If only `-s` is used, settings file will be `settings.py`.

(experimental) Option `--file` is used for specifying settings file name (or class). You can use spider file for adding newly generated class to spiders' `custom_settings` property. If you enumerate file names (or class names) using `,` (like `-f SomeSpider,AnotherSpider`) - script will add generated class to custom_settings of each file. If only `-f` is used, will be used default priority (300).

Option `--terminal` will output 'custom_settings' code to terminal.

Option `--custom` can be used for custom template folder path. Template names should be like `{}.py.mako`. Option will enable usage of TEMPLATES_MODULE setting from projects` settings.py. If this setting is not defined, will cause exception.

## Installation

This command is included in the [Scrapy Boilerplate](https://github.com/groupbwt/scrapy-boilerplate) out of the box. If you want to install it manually, you can get it from PyPi:

```
pip install scrapy-new
```

**Please note** that this package won't work with default Scrapy project structure, it requires a specific custom one, as described [here](https://github.com/groupbwt/scrapy-boilerplate#file-and-folder-structure).
