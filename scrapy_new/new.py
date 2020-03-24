# -*- coding: utf-8 -*-
import operator
import os
import re
import sys
import json

from typing import List

import inflection
from mako.template import Template
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.project import get_project_settings


class NewCommand(ScrapyCommand):
    def __init__(self):
        super().__init__()
        self.settings = get_project_settings()
        self.SETTINGS_NAMES = {
            "pipeline": "ITEM_PIPELINES",
            "extension": "EXTENSIONS",
            "middleware": "DOWNLOADER_MIDDLEWARES",
            "spider_middleware": "SPIDER_MIDDLEWARES",
        }

    def syntax(self) -> str:
        return "<template type> <camelcase class name>"

    def short_desc(self) -> str:
        return "Generate new class file from template"

    def add_options(self, parser) -> None:
        super().add_options(parser)

        parser.add_option(
            "--rabbit",
            action="store_true",
            dest="use_rabbit",
            default=False,
            help="add RabbitMQ code (works for some templates)",
        )

        parser.add_option(
            "--item",
            dest="item_class",
            default="",
            metavar="CLASSNAME",
            help="item class for pipeline",
        )

        parser.add_option(
            "-s",
            "--settings",
            dest="priority",
            default=None,
            metavar="PRIORITY",
            help="add pipeline to settings with specified priority",
        )

        parser.add_option(
            "-t",
            "--terminal",
            dest="priority_terminal",
            default=None,
            metavar="PRIORITY",
            help="write pipeline with specified priority settings to terminal",
        )

        parser.add_option(
            "-d",
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="enable debug output for this command",
        )

    def _add_to_settings(
        self, settings_name: str, class_name: str, priority: str
    ) -> None:
        try:
            priority = str(abs(int(priority)))
        except TypeError:
            priority = "300"

        with open("settings.py", "r") as settings_file:
            settings_text = settings_file.read()

        setting_regex = settings_name + r"\s*=\s*{.*?}"

        pipelines_str = re.search(setting_regex, settings_text, re.DOTALL)
        if pipelines_str:
            capture = pipelines_str.group(0)
            capture_inner = re.search(r"{(.*)}", capture, re.DOTALL)
            if capture_inner:
                capture_inner = capture_inner.group(1)
                capture_inner = re.sub(r"\s", "", capture_inner)
                pipelines_list = capture_inner.split(",")
                pipelines_list = [i for i in pipelines_list if i]
                pipelines_list = [i.split(":") for i in pipelines_list]
                pipelines_list = [(i[0].strip("'\""), i[1]) for i in pipelines_list]
                # remove possible duplicates
                pipelines_set = set(pipelines_list)
                for name, val in pipelines_set:
                    if name == class_name:
                        pipelines_set.remove((name, val))
                        break
                pipelines_set.add((class_name, priority))
                # continue processing
                pipelines_list = sorted(list(pipelines_set), key=operator.itemgetter(1))
                pipelines_list = [('"{}"'.format(i[0]), i[1]) for i in pipelines_list]
                pipelines_str = ",\n    ".join((": ".join(i) for i in pipelines_list))
                pipelines_str = "    " + pipelines_str + ","
                pipelines_str = f"{settings_name} = {{\n{pipelines_str}\n}}"
                settings_text = re.sub(
                    setting_regex, pipelines_str, settings_text, flags=re.DOTALL
                )

                with open("settings.py", "w") as settings_file:
                    settings_file.write(settings_text)

    def _add_to_terminal(
        self, settings_name: str, class_name: str, priority: str
    ) -> None:
        try:
            priority = str(abs(int(priority)))
        except TypeError:
            priority = "300"

        setting_dict = {settings_name: {class_name: int(priority)}}
        setting = f"custom_settings = {json.dumps(setting_dict)}"
        print(f"Copy and paste this settings code to your spider:\n\n{setting}\n")

    def run(self, args: list, opts: list) -> None:
        if len(args) < 2:
            raise UsageError()

        templates_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )

        SUPPORTED_TEMPLATE_TYPES = [
            name.split(".")[0] for name in os.listdir(templates_dir)
        ]

        DEST_PREFIXES = {
            "command": ["commands"],
            "extension": ["extensions"],
            "item": ["items"],
            "middleware": ["middlewares"],
            "model": ["database", "models"],
            "pipeline": ["pipelines"],
            "spider_middleware": ["middlewares"],
            "spider": ["spiders"],
        }

        template_type = args[0]

        if template_type not in SUPPORTED_TEMPLATE_TYPES:
            print(f"ERROR: unsupported template type: {template_type}")
            print("supported types: {}".format(repr(SUPPORTED_TEMPLATE_TYPES)))
            sys.exit(1)

        template_name = os.path.join(templates_dir, "{}.py.mako".format(template_type))
        template = Template(filename=template_name)

        class_name = inflection.camelize(args[1])
        command_name = inflection.underscore(class_name)
        spider_name = inflection.underscore(class_name).replace("_spider", "")
        table_name = inflection.pluralize(inflection.underscore(class_name))
        logger_name = inflection.underscore(class_name).upper()
        item_class = inflection.camelize(opts.item_class) if opts.item_class else None

        file_prefix = DEST_PREFIXES.get(template_type, [])
        file_name = command_name
        file_path = os.path.join(*file_prefix, "{}.py".format(file_name))

        if os.path.exists(file_path):
            print("WARNING: file already exists")
            do_overwrite = input("overwrite? [y/N] ")

            if do_overwrite.lower() not in ["y", "yes"]:
                print("aborted")
                return

        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        rendered_code = template.render(
            class_name=class_name,
            command_name=command_name,
            spider_name=spider_name,
            table_name=table_name,
            logger_name=logger_name,
            use_rabbit=opts.use_rabbit,
            item_class=item_class,
        )

        if opts.debug:
            print(rendered_code)

        if template_type in self.SETTINGS_NAMES:
            if opts.priority:
                self._add_to_settings(
                    self.SETTINGS_NAMES[template_type],
                    f"{file_prefix[0]}.{class_name}",
                    opts.priority,
                )
            if opts.priority_terminal:
                self._add_to_terminal(
                    self.SETTINGS_NAMES[template_type],
                    f"{file_prefix[0]}.{class_name}",
                    opts.priority_terminal,
                )

        with open(file_path, "w") as out_file:
            out_file.write(rendered_code)

        self.add_init_import(file_prefix, file_name, class_name)

        print(f"created {template_type} {file_name}")

    def add_init_import(self, file_prefix: List[str], file_name: str, class_name: str):
        init_file_path = os.path.join(*file_prefix, "__init__.py")
        if os.path.isfile(init_file_path):
            with open(init_file_path) as init_file:
                lines = init_file.readlines()
                lines = [line.strip() for line in lines if line.strip()]
        else:
            lines = ["# -*- coding: utf-8 -*-"]

        new_import = f"from .{file_name} import {class_name}"

        imports = [line for line in lines[1:]]
        imports_set = set(imports)
        imports_set.add(new_import)
        imports = sorted(list(imports_set))
        lines = lines[:1] + imports

        with open(init_file_path, "w") as init_file:
            init_file.write("\n".join(lines))
            init_file.write("\n")
