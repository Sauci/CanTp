import os
import sys
from imp import find_module

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


class PduInfoType:
    def __init__(self, handle, pdu_info):
        self.sdu_length = pdu_info.SduLength
        self.sdu_data = list(handle.ffi.cast('uint8[{}]'.format(pdu_info.SduLength), pdu_info.SduDataPtr))
        self.meta_data = pdu_info.MetaDataPtr


class CanTp(object):
    def __init__(self, recompile=False):
        if recompile is False:
            _, module_path, _ = find_module('pycantp')
            library_path = os.path.join(module_path, 'input', 'pycantp')
        else:
            library_path = os.path.dirname(builder.compile())
        sys.path.append(library_path)
        self.module = import_module('_cantp', package='pycantp')
        self.can_tp_transmit_args = dict()
        self.can_if_transmit = MagicMock(return_value=E_OK)
        self.det_report_error = MagicMock(return_value=E_OK)
        self.det_report_runtime_error = MagicMock(return_value=E_OK)
        self.pdu_r_can_tp_copy_rx_data = MagicMock(return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_copy_tx_data = MagicMock(side_effect=self._copy_tx_data,
                                                   return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_rx_indication = MagicMock(return_value=None)
        self.pdu_r_can_tp_start_of_reception = MagicMock(return_value=self.lib.BUFREQ_OK)
        self.pdu_r_can_tp_tx_confirmation = MagicMock(return_value=None)
        self.ffi.def_extern('CanIf_Transmit')(self._can_if_transmit)
        self.ffi.def_extern('Det_ReportError')(self.det_report_error)
        self.ffi.def_extern('Det_ReportRuntimeError')(self.det_report_runtime_error)
        self.ffi.def_extern('PduR_CanTpCopyRxData')(self.pdu_r_can_tp_copy_rx_data)
        self.ffi.def_extern('PduR_CanTpCopyTxData')(self.pdu_r_can_tp_copy_tx_data)
        self.ffi.def_extern('PduR_CanTpRxIndication')(self.pdu_r_can_tp_rx_indication)
        self.ffi.def_extern('PduR_CanTpStartOfReception')(self.pdu_r_can_tp_start_of_reception)
        self.ffi.def_extern('PduR_CanTpTxConfirmation')(self.pdu_r_can_tp_tx_confirmation)

    def _can_if_transmit(self, tx_pdu_id, pdu_info):
        result = self.can_if_transmit(tx_pdu_id, pdu_info)
        type_name = self.ffi.typeof(self.can_if_transmit.call_args_list[-1][0][1].SduDataPtr).cname
        p_value = [pdu_info.SduDataPtr[i] for i in range(pdu_info.SduLength)]
        c_value = self.ffi.new('uint8[]', p_value)
        self.can_if_transmit.call_args_list[-1][0][1].SduDataPtr = self.ffi.cast(type_name, c_value)
        print(p_value)
        return result

    def _copy_tx_data(self, tx_pdu_id, pdu_info, retry_info, available_data):
        try:
            args = self.can_tp_transmit_args[tx_pdu_id][-1]
        except KeyError:
            pass
        else:
            if args['pdu_info'] is not None and pdu_info.SduDataPtr != self.ffi.NULL:
                for idx in range(pdu_info.SduLength):
                    try:
                        pdu_info.SduDataPtr[idx] = args['pdu_info'].sdu_data.pop(0)
                    except IndexError:
                        pass
        return self.pdu_r_can_tp_copy_tx_data.return_value

    def can_tp_transmit(self, tx_pdu_id, pdu_info):
        if pdu_info != self.ffi.NULL:
            pdu_info_python = PduInfoType(self, pdu_info)
        else:
            pdu_info_python = None
        self.can_tp_transmit_args[tx_pdu_id] = dict(tx_pdu_id=tx_pdu_id, pdu_info=pdu_info_python)
        return self.lib.CanTp_Transmit(tx_pdu_id, pdu_info)

    @property
    def ffi(self):
        return self.module.ffi

    @property
    def lib(self):
        return self.module.lib
