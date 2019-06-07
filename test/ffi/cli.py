import argparse

from ffi_mock import MockGen


def main():
    parser = argparse.ArgumentParser(description='AUTOSAR CAN transport layer code generator')
    parser.add_argument('name',
                        help='name of the FFI')
    parser.add_argument('source',
                        help='path to source file')
    parser.add_argument('header',
                        help='path to public interface header file')
    parser.add_argument('-o',
                        dest='output',
                        help='output directory')
    parser.add_argument('-D',
                        dest='defines',
                        metavar='macro[=val]',
                        default=list(),
                        action='append',
                        help='predefine name as a macro [with value]')
    parser.add_argument('-I',
                        dest='includes',
                        metavar='path',
                        default=list(),
                        action='append',
                        help="#include search path")

    args = parser.parse_args()

    with open(args.source, 'r') as fp:
        source = fp.read()

    with open(args.header, 'r') as fp:
        header = fp.read()

    ffi = MockGen(args.name,
                  source,
                  header,
                  args.output,
                  include_dirs=args.includes,
                  define_macros=args.defines)


if __name__ == '__main__':
    main()
