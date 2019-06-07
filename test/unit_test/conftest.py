import os
from can_tp import CodeGen
from math import ceil
from cffi.verifier import cleanup_tmpdir

from test.ffi import MockGen
import test.cffi_config as ffi_cfg


class DefaultReceiver(dict):
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


class DefaultSender(dict):
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


class DefaultFullDuplex(dict):
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


class CanTpTest(MockGen):
    def __init__(self,
                 config,
                 name='can_tp_ffi',
                 initialize=True,
                 rx_buffer_size=0x0FFF):
        self.available_rx_buffer = rx_buffer_size
        self.can_if_tx_data = list()
        self.can_tp_rx_data = list()
        code_gen = CodeGen(config)
        with open(os.path.join(ffi_cfg.output, 'CanTp_Cfg.c'), 'w') as fp:
            fp.write(code_gen.source)
        with open(os.path.join(ffi_cfg.output, 'CanTp_Cfg.h'), 'w') as fp:
            fp.write(code_gen.header)
        with open(ffi_cfg.source, 'r') as fp:
            source = fp.read()
        with open(ffi_cfg.header, 'r') as fp:
            header = fp.read()
        cleanup_tmpdir()
        super(CanTpTest, self).__init__(name,
                                        source,
                                        header,
                                        ffi_cfg.output,
                                        sources=[os.path.join(ffi_cfg.output, 'CanTp_Cfg.c')],
                                        define_macros=ffi_cfg.compile_definitions,
                                        include_dirs=ffi_cfg.include_directories + [ffi_cfg.output])

        if initialize:
            self.lib.CanTp_Init(self.ffi.cast('const CanTp_ConfigType *', self.lib.CanTp_Config))
            if self.lib.CanTp_State != self.lib.CANTP_ON:
                raise ValueError('CanTp module not initialized correctly...')
        self.can_if_transmit.return_value = 0
        self.det_report_error.return_value = 0
        self.det_report_runtime_error.return_value = 0
        self.det_report_transient_fault.return_value = 0
        self.pdu_r_can_tp_start_of_reception.return_value = self.lib.BUFREQ_OK
        self.pdu_r_can_tp_copy_rx_data.return_value = self.lib.BUFREQ_OK
        self.pdu_r_can_tp_copy_tx_data.return_value = self.lib.BUFREQ_OK
        self.pdu_r_can_tp_start_of_reception.side_effect = self._pdu_r_can_tp_start_of_reception

    def _pdu_r_can_tp_start_of_reception(self, _i_pdu_id, _pdu_info, _tp_sdu_length, buffer_size):
        buffer_size[0] = self.available_rx_buffer
        return self.pdu_r_can_tp_start_of_reception.return_value

    def _pdu_r_can_tp_copy_rx_data(self, _rx_pdu_id, pdu_info, buffer_size):
        if pdu_info.SduDataPtr != self.ffi.NULL and pdu_info.SduLength != 0:
            for idx in range(pdu_info.SduLength):
                self.can_tp_rx_data.append(pdu_info.SduDataPtr[idx])
        buffer_size[0] = self.available_rx_buffer
        return self.pdu_r_can_tp_copy_rx_data.return_value

    def _pdu_r_can_tp_copy_tx_data(self, tx_pdu_id, pdu_info, _retry_info, _available_data):
        if tx_pdu_id in self.can_tp_transmit_args.keys():
            args = self.can_tp_transmit_args[tx_pdu_id]
            if args is not None and pdu_info.SduDataPtr != self.ffi.NULL:
                for idx in range(pdu_info.SduLength):
                    try:
                        pdu_info.SduDataPtr[idx] = args.sdu_data.pop(0)
                    except IndexError:
                        pass
        return self.pdu_r_can_tp_copy_tx_data.return_value

    def get_pdu_info(self, payload, overridden_size=None, meta_data=None):
        if isinstance(payload, str):
            payload = [ord(c) for c in payload]
        sdu_data = self.ffi.new('uint8 []', list(payload))
        if overridden_size is not None:
            sdu_length = overridden_size
        else:
            sdu_length = len(payload)
        pdu_info = self.ffi.new('PduInfoType *')
        pdu_info.SduDataPtr = sdu_data
        pdu_info.SduLength = sdu_length
        if meta_data:
            raise NotImplementedError
        else:
            pdu_info.MetaDataPtr = self.ffi.NULL
        return pdu_info

    def get_receiver_single_frame(self,
                                  payload=(0xFF,),
                                  af='CANTP_STANDARD',
                                  n_ae=0xAE,
                                  n_ta=0x7A,
                                  padding=None):
        if len(payload) > self.get_payload_size(af, 'SF'):
            raise ValueError('multi frame message...')
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]
        payload = list(payload)
        pci = [(0 << 4) | (len(payload) & 0x0F)]
        tmp_return = n_ai + pci + payload
        if padding is not None:
            [tmp_return.append(padding) for _ in range(8 - len(tmp_return))]
        return tmp_return

    @staticmethod
    def get_receiver_flow_control(flow_status='continue to send',
                                  bs=1,
                                  st_min=0,
                                  af='CANTP_STANDARD',
                                  n_ae=0xAE,
                                  n_ta=0x7A,
                                  padding=None):
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]
        pci = [(3 << 4) | {'continue to send': 0,
                           'wait': 1,
                           'overflow': 2}[flow_status],
               bs,
               st_min]
        return n_ai + pci + (([padding] * (4 if n_ai else 5)) if padding is not None else [])

    @staticmethod
    def get_payload_size(af, frame_type):
        return 8 - {
            'CANTP_STANDARD': {
                'SF': 1, 'FF': 2, 'CF': 1, 'FC': 3
            },
            'CANTP_NORMALFIXED': {
                'SF': 1, 'FF': 2, 'CF': 1, 'FC': 3
            },
            'CANTP_EXTENDED': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            },
            'CANTP_MIXED': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            },
            'CANTP_MIXED29BIT': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            }
        }[af][frame_type]

    def get_receiver_multi_frame(self,
                                 payload=(0xFF,) * 8,
                                 af='CANTP_STANDARD',
                                 n_ae=0xAE,
                                 n_ta=0x7A,
                                 bs=1,
                                 padding=None):
        if len(payload) < self.get_payload_size(af, 'FF'):
            raise ValueError('single frame message...')
        cf = list()
        tmp_pl = list(payload)
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]

        ff_pci = [(1 << 4) | ((len(payload) & 0xF00) >> 8), len(payload) & 0x0FF]
        pl = [tmp_pl.pop(0) for _ in range(8 - len(n_ai) - len(ff_pci))]
        ff = n_ai + ff_pci + pl
        if bs:
            fbc = ceil(len(tmp_pl) / self.get_payload_size(af, 'CF') * bs)
        else:
            fbc = ceil(len(tmp_pl) / self.get_payload_size(af, 'CF'))
        sn = 0
        for _ in range(fbc) if bs else range(1):
            for _ in range(bs) if bs else range(fbc):
                sn += 1
                cf_pci = [(2 << 4) | (sn & 0x0F)]
                pl = [tmp_pl.pop(0) for _ in range(8 - len(n_ai) - len(cf_pci)) if len(tmp_pl)]
                cf.append(n_ai + cf_pci + pl)
        if padding and len(cf[-1]) < 8:
            cf[-1] += [padding] * (8 - len(cf[-1]))
        return ff, cf

    def define(self, name):
        return self.pp.defines[name]

    @property
    def available_rx_buffer(self):
        return self._available_rx_buffer - len(self.can_tp_rx_data)

    @available_rx_buffer.setter
    def available_rx_buffer(self, value):
        self._available_rx_buffer = value
