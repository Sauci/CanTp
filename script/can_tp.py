import argparse
import os

from jinja2 import Environment, FileSystemLoader
from json import load
from jsonschema import validate


class CodeGen(object):
    def __init__(self, config):
        self._config = config
        self.environment = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

    @property
    def config(self):
        return self._config

    @property
    def source(self):
        template = self.environment.get_template('config.c.jinja2')
        return template.render(**self.config)

    @property
    def header(self):
        template = self.environment.get_template('config.h.jinja2')
        return template.render(**self.config)


def main():
    parser = argparse.ArgumentParser(description='AUTOSAR CAN transport layer code generator')

    parser.add_argument('configuration', help='configuration file path')
    parser.add_argument('-schema', help='schema file path')
    parser.add_argument('-source', help='output source file path')
    parser.add_argument('-header', help='output header file path')

    args = parser.parse_args()

    with open(args.configuration, 'r') as fp:
        data = load(fp)

    if args.schema:
        with open(args.schema, 'r') as fp:
            validate(data, load(fp))

    code_generator = CodeGen(data)

    if args.source:
        with open(args.source, 'wb') as fp:
            fp.write(code_generator.source.encode())

    if args.header:
        with open(args.header, 'wb') as fp:
            fp.write(code_generator.header.encode())


if __name__ == '__main__':
    main()
