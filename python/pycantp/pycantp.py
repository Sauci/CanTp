import os
import sys

from imp import find_module
from importlib import import_module
from unittest.mock import MagicMock

from .ffi_builder import ffi_builder as builder

E_OK = 0x00
E_NOT_OK = 0x01

CANTP_I_N_AS = 0x00
CANTP_I_N_BS = 0x01
CANTP_I_N_CS = 0x02
CANTP_I_N_AR = 0x03
CANTP_I_N_BR = 0x04
CANTP_I_N_CR = 0x05

CANTP_I_HALF_DUPLEX_RX_SF = 0x80
CANTP_I_HALF_DUPLEX_RX_FF = 0x81
CANTP_I_HALF_DUPLEX_RX_CF = 0x82
CANTP_I_HALF_DUPLEX_RX_FC = 0x83
CANTP_I_HALF_DUPLEX_RX_UNDEF = 0x84

CANTP_I_FULL_DUPLEX_RX_SF = 0x85
CANTP_I_FULL_DUPLEX_RX_FF = 0x86
CANTP_I_FULL_DUPLEX_RX_CF = 0x87
CANTP_I_FULL_DUPLEX_RX_FC = 0x88
CANTP_I_FULL_DUPLEX_RX_UNDEF = 0x89

CANTP_I_N_BUFFER_OVFLW = 0x90

CANTP_E_UNEXP_PDU = 0x85

CANTP_E_PARAM_CONFIG = 0x01
CANTP_E_PARAM_ID = 0x02
CANTP_E_PARAM_POINTER = 0x03
CANTP_E_INIT_FAILED = 0x04
CANTP_E_UNINIT = 0x20

CANTP_E_OPER_NOT_SUPPORTED = 0xA0

CANTP_E_COM = 0xB0
CANTP_E_RX_COM = 0xC0
CANTP_E_TX_COM = 0xD0


class PduInfoType:
    def __init__(self, handle, pdu_info):
        self.sdu_length = pdu_info.SduLength
        self.sdu_data = list(handle.ffi.cast('uint8[{}]'.format(pdu_info.SduLength), pdu_info.SduDataPtr))
        self.meta_data = pdu_info.MetaDataPtr


class CanTp(object):
    def __init__(self, rx_buffer_size=0x0FFF, recompile=False):
        if recompile is False:
            _, module_path, _ = find_module('pycantp')
            library_path = os.path.join(module_path, 'input', 'pycantp')
        else:
            library_path = os.path.dirname(builder.compile())
        sys.path.append(library_path)
        self.module = import_module('_cantp', package='pycantp')
        self.can_if_tx_data = list()
        self.can_tp_rx_data = list()
        self.available_rx_buffer = rx_buffer_size
        self.can_tp_transmit_args = dict()
        self.can_if_transmit = MagicMock(return_value=E_OK)
        self.det_report_error = MagicMock(return_value=E_OK)
        self.det_report_runtime_error = MagicMock(return_value=E_OK)
        self.pdu_r_can_tp_copy_rx_data = MagicMock(side_effect=self._pdu_r_can_tp_copy_rx_data,
                                                   return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_copy_tx_data = MagicMock(side_effect=self._pdu_r_can_tp_copy_tx_data,
                                                   return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_rx_indication = MagicMock(return_value=None)
        self.pdu_r_can_tp_start_of_reception = MagicMock(side_effect=self._pdu_r_can_tp_start_of_reception,
                                                         return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_tx_confirmation = MagicMock(return_value=None)
        self.ffi.def_extern('CanIf_Transmit')(self._can_if_transmit)
        self.ffi.def_extern('Det_ReportError')(self.det_report_error)
        self.ffi.def_extern('Det_ReportRuntimeError')(self.det_report_runtime_error)
        self.ffi.def_extern('PduR_CanTpCopyRxData')(self.pdu_r_can_tp_copy_rx_data)
        self.ffi.def_extern('PduR_CanTpCopyTxData')(self.pdu_r_can_tp_copy_tx_data)
        self.ffi.def_extern('PduR_CanTpRxIndication')(self.pdu_r_can_tp_rx_indication)
        self.ffi.def_extern('PduR_CanTpStartOfReception')(self.pdu_r_can_tp_start_of_reception)
        self.ffi.def_extern('PduR_CanTpTxConfirmation')(self.pdu_r_can_tp_tx_confirmation)

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

    def _can_if_transmit(self, tx_pdu_id, pdu_info):
        result = self.can_if_transmit(tx_pdu_id, pdu_info)
        if pdu_info != self.ffi.NULL and pdu_info.SduDataPtr != self.ffi.NULL:
            self.can_if_tx_data.append(list(self.ffi.cast('uint8[{}]'.format(pdu_info.SduLength), pdu_info.SduDataPtr)))
        else:
            self.can_if_tx_data.append(list())
        return result

    def can_tp_init(self, config):
        return self.lib.CanTp_Init(config)

    def can_tp_main_function(self):
        return self.lib.CanTp_MainFunction()

    def can_tp_rx_indication(self, rx_pdu_id, pdu_info):
        return self.lib.CanTp_RxIndication(rx_pdu_id, pdu_info)

    def can_tp_transmit(self, tx_pdu_id, pdu_info):
        if pdu_info != self.ffi.NULL:
            pdu_info_python = PduInfoType(self, pdu_info)
        else:
            pdu_info_python = None
        self.can_tp_transmit_args[tx_pdu_id] = pdu_info_python
        return self.lib.CanTp_Transmit(tx_pdu_id, pdu_info)

    def can_tp_tx_confirmation(self, tx_pdu_id, result):
        return self.lib.CanTp_TxConfirmation(tx_pdu_id, result)

    @property
    def available_rx_buffer(self):
        return self._available_rx_buffer - len(self.can_tp_rx_data)

    @available_rx_buffer.setter
    def available_rx_buffer(self, value):
        self._available_rx_buffer = value

    @property
    def ffi(self):
        return self.module.ffi

    @property
    def lib(self):
        return self.module.lib
