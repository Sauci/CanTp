from behave import fixture, use_fixture
from pycantp import CanTp
from threading import Thread
from unittest.mock import MagicMock

E_OK = 0x00
E_NOT_OK = 0x01

CANTP_E_PARAM_ID = 0x02
CANTP_E_PARAM_POINTER = 0x03
CANTP_E_OPER_NOT_SUPPORTED = 0xA0


def main_function(context):
    cnt = context.main_function_call_number
    dt = context.can_tp_config.mainFunctionPeriod
    while cnt:
        context.can_tp.lib.CanTp_MainFunction()
        cnt -= 1


@fixture
def module_can_tp(context):
    can_tp = CanTp()
    can_if_transmit = MagicMock(return_value=E_OK)
    det_report_error = MagicMock(return_value=E_OK)
    det_report_runtime_error = MagicMock(return_value=E_OK)

    @can_tp.ffi.def_extern('PduR_CanTpTxConfirmation')
    def pdu_r_can_tp_tx_confirmation(*args, **kwargs):
        return None

    @can_tp.ffi.def_extern('PduR_CanTpTxConfirmation')
    def pdu_r_can_tp_rx_indication(*args, **kwargs):
        return None

    @can_tp.ffi.def_extern('PduR_CanTpCopyTxData')
    def pdu_r_can_tp_copy_tx_data(*args, **kwargs):
        return None

    # pdu_r_can_tp_tx_confirmation = MagicMock(return_value=can_tp.lib.BUFREQ_OK)
    can_tp.ffi.def_extern('CanIf_Transmit')(can_if_transmit)
    can_tp.ffi.def_extern('Det_ReportError')(det_report_error)
    can_tp.ffi.def_extern('Det_ReportRuntimeError')(det_report_runtime_error)
    context.det_report_error = det_report_error
    context.det_report_runtime_error = det_report_runtime_error
    context.can_tp = can_tp
    context.main_function_call_number = 1000000
    context.main_function_thread = Thread(target=main_function, args=(context,), daemon=True)
    yield context.can_tp
    if context.main_function_thread.is_alive():
        context.main_function_thread.join()


def before_tag(context, tag):
    if tag == 'fixture.can_tp':
        use_fixture(module_can_tp, context)
