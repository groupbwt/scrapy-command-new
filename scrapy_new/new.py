# -*- coding: utf-8 -*-
import json
import operator
import os
import re
import sys
from os import path
from re import Match
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
        self.default_settings_filename = "settings.py"

    def syntax(self) -> str:
        return "<template type> <camelcase class name>"

    def short_desc(self) -> str:
        return "Generate new class file from template"

    def add_options(self, parser) -> None:
        super().add_options(parser)

        parser.add_option(
            "-r",
            "--rabbit",
            action="store_true",
            dest="use_rabbit",
            default=False,
            help="add RabbitMQ code (works for some templates)",
        )

        parser.add_option(
            "-i",
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
            "-f",
            "--file",
            dest="filename",
            default=None,
            metavar="FILENAME",
            help="name of settings or spider class",
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

        parser.add_option(
            "-c",
            "--custom",
            action="store_true",
            dest="custom_templates_dir",
            default=False,
            help="enable using of custom template modules",
        )

    def get_settings_dict(self, setting_str: Match) -> dict:
        """Returns object from setting string"""
        capture = setting_str.group(0)
        capture_inner = re.search(r"{(.*)}", capture, re.DOTALL)
        try:
            return eval(f"{{{capture_inner.group(1)}}}")
        except SyntaxError as se:
            print(f"Got {se}")
        return {}

    def _add_to_settings(
        self, filename: str, settings_name: str, class_name: str, priority: str
    ) -> None:
        try:
            priority = str(abs(int(priority)))
        except TypeError:
            priority = "300"

        if not filename:
            filename = self.default_settings_filename

        with open(filename, "r") as settings_file:
            settings_text = settings_file.read()
        is_custom_settings = (
            "custom_settings" in settings_text or "class" in settings_text
        )
        if not is_custom_settings:
            # common settings.py
            setting_regex = settings_name + r"\s*=\s*{.*?}"
            setting_str = re.search(setting_regex, settings_text, re.DOTALL)
            if setting_str:
                settings_dict = self.get_settings_dict(setting_str)
                settings_dict[class_name] = int(priority)
                # sorted(list(pipelines_set), key=operator.itemgetter(1))
                dict_str = json.dumps(settings_dict, indent=4)
                result_str = f"{settings_name} = {dict_str}".replace("'", '"')
                settings_text = re.sub(
                    setting_regex, result_str, settings_text, flags=re.DOTALL
                )
                with open(filename, "w") as settings_file:
                    settings_file.write(settings_text)
            else:
                # setting does not exist yet
                print(f"Created '{settings_name}' in {filename}")
                # if input("Create one? [y/N] ").lower() not in ["y", "yes"]:
                #    print("aborted setting creation")
                #    return
                with open(filename, "a") as settings_file:
                    settings_file.write(f"\n{settings_name} = {{}}\n")
                self._add_to_settings(filename, settings_name, class_name, priority)
        else:
            # custom_settings
            # TODO create custom_settings inside spider?
            custom_setting_regex = r"custom_settings\s*=\s*\{.*}\n"
            setting_str = re.search(custom_setting_regex, settings_text, re.DOTALL)
            print(self.get_settings_dict(setting_str))
            if setting_str:
                # spider custom settings
                settings_dict = self.get_settings_dict(setting_str)
                if settings_dict.get(settings_name):
                    settings_dict[settings_name][class_name] = int(priority)
                else:
                    settings_dict[settings_name] = {class_name: int(priority)}
                # sorted(list(pipelines_set), key=operator.itemgetter(1))
                temp_dict_str = json.dumps(settings_dict, indent=4)
                dict_str = "    ".join([l + "\n" for l in temp_dict_str.split("\n")])
                result_str = f"custom_settings = {dict_str}".replace("'", '"')
                settings_text = re.sub(
                    custom_setting_regex, result_str, settings_text, flags=re.DOTALL,
                )
                with open(filename, "w") as settings_file:
                    settings_file.write(settings_text)
            else:
                print("ERROR: Given spider has no 'custom_settings' field!")

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
            "helper": ["helpers"],
            "rabbitmq": ["rabbitmq"],
            "pm2": ["pm2"],
            "loader": ["loaders"],
        }

        template_type = args[0]

        if opts.custom_templates_dir:
            # feature for adding custom templates
            # uses TEMPLATES_MODULE setting in settings.py
            if os.path.exists(self.default_settings_filename):
                from settings import TEMPLATES_MODULE  # isort:skip

                tmp = os.path.join(TEMPLATES_MODULE, "{}.py.mako".format(template_type))
                if os.path.exists(tmp):
                    templates_dir = TEMPLATES_MODULE
                    SUPPORTED_TEMPLATE_TYPES.extend(
                        name.split(".")[0] for name in os.listdir(templates_dir)
                    )
            else:
                raise UsageError(f"No settings.py in project!")

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

        if class_name[0].isdigit():
            raise UsageError(f"Class name violation in '{class_name}'")

        file_prefix = DEST_PREFIXES.get(template_type, [])
        file_name = command_name
        file_path = os.path.join(*file_prefix, f"{file_name}.py")

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

        if opts.priority:
            opts.filename = self.default_settings_filename

        if template_type in self.SETTINGS_NAMES and opts.filename:
            filenames = opts.filename.split(",")
            for filename in filenames:
                if not path.exists(filename):
                    # try find spider by class name
                    spider_prefix = DEST_PREFIXES.get("spider", [])
                    spider_file_name = inflection.underscore(filename)
                    filename = os.path.join(*spider_prefix, f"{spider_file_name}.py")
                    if not path.exists(filename):
                        raise UsageError(
                            f"Could not find specified file name: {filename}"
                        )
                self._add_to_settings(
                    filename,
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
                # there will be error in eval if started
                # with not formatted code next time
                # TODO disable when not using settings
                os.system(f"black {filename}")

        with open(file_path, "w") as out_file:
            out_file.write(rendered_code)

        self.add_init_import(file_prefix, file_name, class_name)

        print(f"created {template_type} '{file_name}'")

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
