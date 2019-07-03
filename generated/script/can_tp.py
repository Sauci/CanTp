import argparse
import os

from jinja2 import Environment, FileSystemLoader
from json import load

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
    parser.add_argument('-source', help='output source file path')
    parser.add_argument('-header', help='output header file path')

    args = parser.parse_args()

    with open(args.configuration, 'r') as fp:
        data = load(fp)

    code_generator = CodeGen(data)

    if args.source:
        with open(args.source, 'wb') as fp:
            fp.write(code_generator.source.encode())

    if args.header:
        with open(args.header, 'wb') as fp:
            fp.write(code_generator.header.encode())


if __name__ == '__main__':
    main()
