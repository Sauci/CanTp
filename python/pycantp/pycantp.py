import os
import sys

from glob import glob
from importlib import import_module

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

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


def mock_callback(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class PduInfoType:
    def __init__(self, handle, pdu_info):
        self.sdu_length = pdu_info.SduLength
        self.sdu_data = list(handle.ffi.cast('uint8[{}]'.format(pdu_info.SduLength), pdu_info.SduDataPtr))
        self.meta_data = pdu_info.MetaDataPtr


class CanTpMocked:
    def __init__(self, handle):
        self.handle = handle
        self.can_if_transmit_args = list()
        self.pdu_r_can_tp_copy_rx_data_args = list()
        self.pdu_r_can_tp_start_of_reception_args = list()
        self.can_if_transmit = MagicMock(return_value=E_OK)
        self.det_report_error = MagicMock(return_value=E_OK)
        self.det_report_runtime_error = MagicMock(return_value=E_OK)
        self.pdu_r_can_tp_copy_rx_data = MagicMock(return_value=handle.lib.BUFREQ_OK)
        self.pdu_r_can_tp_copy_tx_data = MagicMock(return_value=handle.lib.BUFREQ_OK)
        self.pdu_r_can_tp_rx_indication = MagicMock(return_value=None)
        self.pdu_r_can_tp_start_of_reception = MagicMock(return_value=handle.lib.BUFREQ_OK)
        self.pdu_r_can_tp_tx_confirmation = MagicMock(return_value=None)
        handle.ffi.def_extern('CanIf_Transmit')(self._can_if_transmit)
        handle.ffi.def_extern('Det_ReportError')(self.det_report_error)
        handle.ffi.def_extern('Det_ReportRuntimeError')(self.det_report_runtime_error)
        handle.ffi.def_extern('PduR_CanTpCopyRxData')(self._pdu_r_can_tp_copy_rx_data)
        handle.ffi.def_extern('PduR_CanTpCopyTxData')(self._pdu_r_can_tp_copy_tx_data)
        handle.ffi.def_extern('PduR_CanTpRxIndication')(self.pdu_r_can_tp_rx_indication)
        handle.ffi.def_extern('PduR_CanTpStartOfReception')(self._pdu_r_can_tp_start_of_reception)
        handle.ffi.def_extern('PduR_CanTpTxConfirmation')(self.pdu_r_can_tp_tx_confirmation)

    @mock_callback
    def _can_if_transmit(self, tx_pdu_id, pdu_info):
        self.can_if_transmit_args.append((tx_pdu_id, PduInfoType(self.handle, pdu_info)))
        return self.can_if_transmit(tx_pdu_id, pdu_info)

    @mock_callback
    def _pdu_r_can_tp_copy_rx_data(self, rx_pdu_id, pdu_info, available_data):
        self.pdu_r_can_tp_copy_rx_data_args.append((rx_pdu_id,
                                                    PduInfoType(self.handle, pdu_info),
                                                    available_data))
        return self.pdu_r_can_tp_copy_rx_data(rx_pdu_id, pdu_info, available_data)

    @mock_callback
    def _pdu_r_can_tp_copy_tx_data(self, tx_pdu_id, pdu_info, retry_info, available_data):
        available_data = available_data[0]
        return self.pdu_r_can_tp_copy_tx_data(tx_pdu_id, pdu_info, retry_info, available_data)

    @mock_callback
    def _pdu_r_can_tp_start_of_reception(self, rx_pdu_id, pdu_info, tp_sdu_length, buffer_size):
        self.pdu_r_can_tp_start_of_reception_args.append((rx_pdu_id,
                                                          PduInfoType(self.handle, pdu_info),
                                                          tp_sdu_length,
                                                          buffer_size))
        return self.pdu_r_can_tp_start_of_reception(rx_pdu_id, pdu_info, tp_sdu_length, buffer_size)


class CanTp(object):
    def __init__(self, recompile=True):
        library_directory = os.getcwd()
        if recompile is False:
            library_path = glob(os.path.join(library_directory, __package__, '*.so'))
            if not library_path:
                library_path = builder.compile(tmpdir=library_directory)
            else:
                library_path = library_path[0]
        else:
            library_path = builder.compile(tmpdir=library_directory)
        sys.path.append(os.path.dirname(library_path))
        try:
            self.module = import_module('_cantp', package='pycantp')
        except (ImportError, SystemError) as e:
            raise e
        self.mock = CanTpMocked(self.module)

    @property
    def ffi(self):
        return self.module.ffi

    @property
    def lib(self):
        return self.module.lib
