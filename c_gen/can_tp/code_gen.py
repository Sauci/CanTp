import os

from jsonschema import validate
from pystache import Renderer

schema = {
    "type": "object",
    "properties": {
        "default settings": {
            "type": "object",
            "properties": {
                "block size": {
                    "$ref": "#/definitions/block_size"
                },
                "communication type": {
                    "$ref": "#/definitions/communication_type"
                },
                "wait for transmission maximum": {
                    "$ref": "#/definitions/wait_for_transmission_maximum"
                },
                "minimum separation time": {
                    "$ref": "#/definitions/minimum_separation_time"
                },
                "N_As timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Bs timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Cs timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Ar timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Br timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Cr timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                }
            }
        },
        "configurations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "main function period": {
                        "type": "number",
                        "minimum": 0
                    },
                    "channels": {
                        "type": "array",
                        "minItems": 1,
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "channel mode": {
                                        "$ref": "#/definitions/channel_mode"
                                    },
                                    "receivers": {
                                        "type": "array",
                                        "items": {
                                            "oneOf": [
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/receiver_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_STANDARD",
                                                                        "CANTP_NORMALFIXED"
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    ]
                                                },
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/receiver_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_MIXED",
                                                                        "CANTP_MIXED29BIT"
                                                                    ]
                                                                },
                                                                "address extension": {
                                                                    "$ref": "#/definitions/network_address_extension"
                                                                }
                                                            }
                                                        }
                                                    ]
                                                },
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/receiver_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_EXTENDED"
                                                                    ]
                                                                },
                                                                "target address": {
                                                                    "$ref": "#/definitions/network_address_extension"
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    },
                                    "transmitters": {
                                        "type": "array",
                                        "items": {
                                            "oneOf": [
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/transmitter_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_STANDARD",
                                                                        "CANTP_NORMALFIXED"
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    ]
                                                },
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/transmitter_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_MIXED",
                                                                        "CANTP_MIXED29BIT"
                                                                    ]
                                                                },
                                                                "address extension": {
                                                                    "$ref": "#/definitions/network_address_extension"
                                                                }
                                                            }
                                                        }
                                                    ]
                                                },
                                                {
                                                    "allOf": [
                                                        {
                                                            "$ref": "#/definitions/transmitter_common"
                                                        },
                                                        {
                                                            "properties": {
                                                                "addressing format": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "CANTP_EXTENDED"
                                                                    ]
                                                                },
                                                                "target address": {
                                                                    "$ref": "#/definitions/network_address_extension"
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                "required": ["channels"]
            },

            # make sure we have at least one configuration.
            "minItems": 1
        }
    },
    "required": ["configurations"],
    "definitions": {
        "channel_mode": {
            "type": "string",
            "enum": [
                "CANTP_MODE_HALF_DUPLEX",
                "CANTP_MODE_FULL_DUPLEX"
            ]
        },
        "communication_type": {
            "type": "string",
            "enum": [
                "CANTP_FUNCTIONAL",
                "CANTP_PHYSICAL"
            ]
        },
        "receiver_common": {
            "properties": {
                "comment": {
                    "type": "string"
                },
                "network service data unit identifier": {
                    "$ref": "#/definitions/network_address_extension"
                },
                "N_Ar timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Br timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Cr timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "block size": {
                    "$ref": "#/definitions/block_size"
                },
                "minimum separation time": {
                    "$ref": "#/definitions/minimum_separation_time"
                },
                "wait for transmission maximum": {
                    "$ref": "#/definitions/wait_for_transmission_maximum"
                },
                "network service data unit reference": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 4294967295
                },
                "enable padding": {
                    "type": "boolean"
                },
                "communication type": {
                    "$ref": "#/definitions/communication_type"
                }
            },
            "required": [
                "network service data unit reference"
            ]
        },
        "block_size": {
            "type": "integer",
            "minimum": 0
        },
        "minimum_separation_time": {
            "type": "integer",
            "minimum": 0
        },
        "wait_for_transmission_maximum": {
            "type": "integer",
            "minimum": 0
        },
        "transmitter_common": {
            "properties": {
                "comment": {
                    "type": "string"
                },
                "network service data unit identifier": {
                    "$ref": "#/definitions/network_address_extension"
                },
                "N_As timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Bs timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "N_Cs timeout": {
                    "$ref": "#/definitions/network_layer_timeout"
                },
                "network service data unit reference": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 4294967295
                },
                "enable transmit cancellation": {
                    "type": "boolean"
                },
                "enable padding": {
                    "type": "boolean"
                },
                "communication type": {
                    "$ref": "#/definitions/communication_type"
                }
            },
            "required": [
                "network service data unit reference"
            ]
        },
        "network_address_extension": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
        },
        "network_layer_timeout": {
            "type": "number",
            "minimum": 0
        }
    }
}


class CodeGen(object):
    def __init__(self, config):
        self.renderer = Renderer(search_dirs=(os.path.join(os.path.dirname(__file__)),),
                                 file_encoding='utf-8',
                                 escape=lambda x: x,
                                 partials=self.convert)
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

    def convert(self, *args, **kwargs):
        return 0

    @property
    def source(self):
        return self.renderer.render_name('config.c', self.data)

    @property
    def header(self):
        return self.renderer.render_name('config.h', self.data)
