import os
from jsonschema import validate
from pystache import Renderer


class CodeGen(object):
    def __init__(self, schema, config):
        self.renderer = Renderer(search_dirs=(os.path.join(os.path.dirname(__file__), 'template'),),
                                 file_encoding='utf-8',
                                 escape=lambda x: x)
        self.data = config
        validate(self.data, schema=schema)

        for config_idx, config in enumerate(self.data['configurations']):
            config.setdefault('CONFIG_ID', '{:02X}'.format(config_idx))
            for channel_idx, channel in enumerate(config['channels']):
                channel.setdefault('CHANNEL_ID', '{:02X}'.format(channel_idx))
                channel.setdefault('channel_has_rx_n_sdu', 'receivers' in channel.keys())
                channel.setdefault('channel_has_tx_n_sdu', 'transmitters' in channel.keys())

        max_rx = max(sum(len(d['receivers']) for d in c['channels'] if 'receivers' in d.keys())
                     for c in self.data['configurations'] if 'channels' in c.keys())
        max_tx = max(sum(len(d['transmitters']) for d in c['channels'] if 'transmitters' in d.keys())
                     for c in self.data['configurations'] if
                     'channels' in c.keys())
        max_ch = max(len(c['channels']) for c in self.data['configurations'])
        self.data.setdefault('num_of_config', len(self.data['configurations']))
        self.data.setdefault('max_num_of_channel', max_ch)
        self.data.setdefault('num_of_n_sdu', max_rx + max_tx)

    @property
    def source(self):
        return self.renderer.render_name('config.c', self.data)

    @property
    def header(self):
        return self.renderer.render_name('config.h', self.data)
