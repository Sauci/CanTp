from behave import *
from unittest.mock import ANY

E_OK = 0x00
E_NOT_OK = 0x01

CANTP_E_PARAM_ID = 0x02
CANTP_E_PARAM_POINTER = 0x03
CANTP_E_OPER_NOT_SUPPORTED = 0xA0


@given('DET is enabled')
def step_impl(context):
    assert context.can_tp.lib.Det_ReportError is not None


@step('the static configuration of the CanTp module is valid')
def step_impl(context):
    rx_nsdu = context.can_tp.ffi.new('CanTp_RxNSduType *')
    rx_nsdu.nSduId = 0
    rx_nsdu.af = context.can_tp.lib.CANTP_STANDARD
    rx_nsdu.bs = 10
    tx_nsdu = context.can_tp.ffi.new('CanTp_TxNSduType *')
    tx_nsdu.nSduId = 1
    tx_nsdu.af = context.can_tp.lib.CANTP_STANDARD
    channel = context.can_tp.ffi.new('CanTp_ChannelType *')
    channel.nSdu.rx = rx_nsdu
    channel.nSdu.tx = tx_nsdu
    channel.nSdu.rxNSduCnt = 1
    channel.nSdu.txNSduCnt = 1
    config = context.can_tp.ffi.new('CanTp_ConfigType *')
    config.pChannel = channel
    config.maxChannelCnt = 1
    config.mainFunctionPeriod = 10
    context.can_tp_config = config


@step('the CanTp module is initialized')
def step_impl(context):
    context.can_tp.lib.CanTp_Init(context.can_tp_config)


@step('pVersionInfo parameter is a NULL pointer')
def step_impl(context):
    context.version_info = context.can_tp.ffi.NULL


@step('the identifier of the reception PDU is valid')
def step_impl(context):
    context.rx_pdu_id = 0


@step('the identifier of the transmission PDU is valid')
def step_impl(context):
    context.tx_pdu_id = 1


@step('the identifier of the reception PDU is invalid')
def step_impl(context):
    context.rx_pdu_id = 0
    for channel_idx in range(context.can_tp_config.maxChannelCnt):
        channel = context.can_tp_config.pChannel + channel_idx
        for rx_nsdu_idx in range(channel.nSdu.rxNSduCnt):
            context.rx_pdu_id += 1
    context.rx_pdu_id += 1


@step('the identifier of the transmission PDU is invalid')
def step_impl(context):
    context.tx_pdu_id = 0
    for channel_idx in range(context.can_tp_config.maxChannelCnt):
        channel = context.can_tp_config.pChannel + channel_idx
        for tx_nsdu_idx in range(channel.nSdu.txNSduCnt):
            context.tx_pdu_id += 1
    context.tx_pdu_id += 1


@step('a PDU info structure containing a long message')
def step_impl(context):
    data_array = context.can_tp.ffi.new('uint8 []', [0xDE for _ in range(100)])
    #p_data_array = context.can_tp.ffi.cast('uint8 *', data_array)
    pdu_info = context.can_tp.ffi.new('PduInfoType *')
    pdu_info.SduDataPtr = data_array
    pdu_info.SduLength = len(data_array)
    pdu_info.MetaDataPtr = context.can_tp.ffi.NULL
    context.pdu_info = pdu_info


@when('we call CanTp_Transmit')
def step_impl(context):
    context.return_value = context.can_tp.lib.CanTp_Transmit(context.tx_pdu_id, context.pdu_info)
    print(context.return_value)


@when('we call CanTp_CancelReceive')
def step_impl(context):
    context.return_value = context.can_tp.lib.CanTp_CancelReceive(context.rx_pdu_id)


@then('the Det_ReportError function is called')
def step_impl(context):
    context.det_report_error.assert_called_once()


@then('Det_ReportRuntimeError is called')
def step_impl(context):
    context.det_report_runtime_error.assert_called_once()


@step('the CanTp_MainFunction is called cyclically')
def step_impl(context):
    context.main_function_thread.start()
    while not context.main_function_thread.is_alive():
        pass


@then('errorId parameter is equal to CANTP_E_PARAM_ID')
def step_impl(context):
    context.det_report_error.assert_called_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)


@then('errorId parameter is equal to CANTP_E_PARAM_POINTER')
def step_impl(context):
    context.det_report_error.assert_called_with(ANY, ANY, ANY, CANTP_E_PARAM_POINTER)


@then('errorId parameter is equal to CANTP_E_OPER_NOT_SUPPORTED')
def step_impl(context):
    context.det_report_runtime_error.assert_called_with(ANY, ANY, ANY, CANTP_E_OPER_NOT_SUPPORTED)


@then('the return value is E_NOT_OK')
def step_impl(context):
    assert context.return_value == E_NOT_OK
