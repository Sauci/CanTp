import argparse

from json import load

from code_gen import CodeGen


def main():
    parser = argparse.ArgumentParser(description='AUTOSAR CAN transport layer code generator')

    parser.add_argument('configuration', help='configuration file path')
    parser.add_argument('-source', help='output source file path')
    parser.add_argument('-header', help='output header file path')

    args = parser.parse_args()

    with open(args.configuration, 'r') as fp:
        data = load(fp)

    code_generator = CodeGen(data)

    if args.source:
        with open(args.source, 'w') as fp:
            fp.write(code_generator.source)

    if args.header:
        with open(args.header, 'w') as fp:
            fp.write(code_generator.header)


if __name__ == '__main__':
    main()
