import hashlib
import json
import pytest

single_frame_sizes = [pytest.param(fs, id='SF_DL = {}'.format(fs)) for fs in (1, 2, 6)]
multi_frames_sizes = [pytest.param(fs, id='FF_DL = {}'.format(fs)) for fs in (8, 4095)]

channel_modes = [pytest.param('CANTP_MODE_HALF_DUPLEX', id='half duplex'),
                 pytest.param('CANTP_MODE_FULL_DUPLEX', id='full duplex')]

addressing_formats = [pytest.param('CANTP_EXTENDED', id='extended addressing format'),
                      pytest.param('CANTP_MIXED', id='11 bits mixed addressing format'),
                      pytest.param('CANTP_MIXED29BIT', id='29 bits mixed addressing format'),
                      pytest.param('CANTP_NORMALFIXED', id='fixed addressing format'),
                      pytest.param('CANTP_STANDARD', id='standard addressing format')]

change_parameter_api = [pytest.param('TP_STMIN', id='separation time minimum'),
                        pytest.param('TP_BS', id='block size')]

n_xx_timeouts = [1.0 / 1000000.0 * n for n in (10, 100, 0xFF)]

n_as_timeouts = [pytest.param(t, id='N_As = {}s'.format(t)) for t in n_xx_timeouts]
n_bs_timeouts = [pytest.param(t, id='N_Bs = {}s'.format(t)) for t in n_xx_timeouts]
n_cs_timeouts = [pytest.param(t, id='N_Cs = {}s'.format(t)) for t in n_xx_timeouts]

n_ar_timeouts = [pytest.param(t, id='N_Ar = {}s'.format(t)) for t in n_xx_timeouts]
n_br_timeouts = [pytest.param(t, id='N_Br = {}s'.format(t)) for t in n_xx_timeouts]
n_cr_timeouts = [pytest.param(t, id='N_Cr = {}s'.format(t)) for t in n_xx_timeouts]

addresses = (0, 10, 100, 255)

n_sa = [pytest.param(a, id='N_Sa = 0x{:02X}'.format(a)) for a in addresses]
n_ta = [pytest.param(a, id='N_Ta = 0x{:02X}'.format(a)) for a in addresses]

block_sizes = [pytest.param(bs, id='BS = {}'.format(bs)) for bs in (0, 1, 10, 15)]
wait_for_tx_max = [pytest.param(i, id='WFT max = {}'.format(i)) for i in (1, 2, 3, 4, 5, 6, 7)]


class Config(dict):

    @property
    def get_id(self):
        return hashlib.sha224(json.dumps(self, sort_keys=True, indent=0).encode('utf-8')).hexdigest()


class DefaultReceiver(Config):
    def __init__(self,
                 af='CANTP_STANDARD',
                 n_ar=1.0,
                 n_br=0.9,
                 n_cr=1.0,
                 bs=2,
                 st_min=2,
                 wft_max=1,
                 main_period=1.0 / 1000000.0,
                 com_type='CANTP_FUNCTIONAL',
                 ch_mode='CANTP_MODE_HALF_DUPLEX',
                 padding=None):
        super(DefaultReceiver, self).__init__({
            "configurations": [
                {
                    "padding byte": 255 if padding is None else padding,
                    "main function period": main_period,
                    "channels": [
                        {
                            "channel mode": ch_mode,
                            "receivers": [
                                {
                                    "enable padding": padding is not None,
                                    "communication type": com_type,
                                    "network service data unit identifier": 0,
                                    "addressing format": af,
                                    "N_Ar timeout": n_ar,
                                    "N_Br timeout": n_br,
                                    "N_Cr timeout": n_cr,
                                    "block size": bs,
                                    "minimum separation time": st_min,
                                    "wait for transmission maximum": wft_max,
                                    "network service data unit reference": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        })

    @property
    def main_period(self):
        return self['configurations'][0]['main function period']

    @property
    def receivers(self):
        return self['configurations'][0]['channels'][0]['receivers']


class DefaultSender(Config):
    def __init__(self,
                 af='CANTP_STANDARD',
                 n_as=1.0,
                 n_bs=1.0,
                 n_cs=0.9,
                 main_period=1.0 / 1000000.0,
                 com_type='CANTP_FUNCTIONAL',
                 ch_mode='CANTP_MODE_HALF_DUPLEX',
                 padding=None):
        super(DefaultSender, self).__init__({
            "configurations": [
                {
                    "padding byte": 255 if padding is None else padding,
                    "main function period": main_period,
                    "channels": [
                        {
                            "channel mode": ch_mode,
                            "transmitters": [
                                {
                                    "enable padding": padding is not None,
                                    "communication type": com_type,
                                    "network service data unit identifier": 0,
                                    "addressing format": af,
                                    "N_As timeout": n_as,
                                    "N_Bs timeout": n_bs,
                                    "N_Cs timeout": n_cs,
                                    "network service data unit reference": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        })

    @property
    def main_period(self):
        return self['configurations'][0]['main function period']

    @property
    def senders(self):
        return self['configurations'][0]['channels'][0]['transmitters']


class DefaultFullDuplex(Config):
    def __init__(self,
                 af='CANTP_STANDARD',
                 n_as=1.0,
                 n_bs=1.0,
                 n_cs=0.9,
                 n_ar=1.0,
                 n_br=0.9,
                 n_cr=1.0,
                 bs=2,
                 st_min=2,
                 wft_max=1,
                 main_period=1.0 / 1000000.0,
                 com_type='CANTP_FUNCTIONAL',
                 padding=None):
        receiver = DefaultReceiver(af=af,
                                   n_ar=n_ar,
                                   n_br=n_br,
                                   n_cr=n_cr,
                                   bs=bs,
                                   st_min=st_min,
                                   wft_max=wft_max,
                                   main_period=main_period,
                                   com_type=com_type,
                                   ch_mode='CANTP_MODE_FULL_DUPLEX').receivers[0]
        sender = DefaultSender(af=af,
                               n_as=n_as,
                               n_bs=n_bs,
                               n_cs=n_cs,
                               main_period=main_period,
                               com_type=com_type,
                               ch_mode='CANTP_MODE_FULL_DUPLEX',
                               padding=padding).senders[0]
        super(DefaultFullDuplex, self).__init__({"configurations": [
            {
                "padding byte": 255 if padding is None else padding,
                "main function period": main_period,
                "channels": [
                    {
                        "channel mode": 'CANTP_MODE_FULL_DUPLEX',
                        "receivers": [receiver],
                        "transmitters": [sender]
                    }
                ]
            }
        ]})
