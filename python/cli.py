import argparse
import os
import pystache
from json import load
from jsonschema import validate

renderer = pystache.Renderer(search_dirs=(os.path.join(os.path.dirname(__file__), 'pycantp', 'template'),),
                             file_encoding='utf-8',
                             escape=lambda x: x)


def main():
    parser = argparse.ArgumentParser(prog='pycantp',
                                     description='post-build configuration generator for CanTp module')

    parser.add_argument('configuration', help='full path to JSON configuration')
    parser.add_argument('-source', help='output source file path')
    parser.add_argument('-header', help='output header file path')

    args = parser.parse_args()

    with open(args.configuration, 'r') as fp:
        data = load(fp)

    with open(os.path.join(os.path.dirname(__file__), 'pycantp', 'template', 'config.schema.json'), 'r') as fp:
        schema = load(fp)

    validate(data, schema=schema)

    if args.source:
        with open(args.source, 'w') as fp:
            fp.write(renderer.render_name('config.c', dict(config=data, num_of_config=len(data))))

    rx_cnt = sum(sum(len(d['receivers']) for d in c['channels'] if 'receivers' in d.keys())
                 for c in data if 'channels' in c.keys())
    tx_cnt = sum(sum(len(d['transmitters']) for d in c['channels'] if 'transmitters' in d.keys())
                 for c in data if
                 'channels' in c.keys())
    ch_cnt = sum(len(c['channels']) for c in data if 'channels' in c.keys())

    if args.header:
        with open(args.header, 'w') as fp:
            fp.write(renderer.render_name('config.h', dict(config=data,
                                                           num_of_config=len(data),
                                                           num_of_channel=ch_cnt,
                                                           num_of_n_sdu=sum((rx_cnt, tx_cnt)))))


if __name__ == '__main__':
    main()
