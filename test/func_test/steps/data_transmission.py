from behave import *
from test.helper import *


@step('an initialized instance of CanTp module with a single tx N-SDU')
def step_impl(context):
    context.configuration = Helper.create_single_tx_sdu_config(context.can_tp, padding_byte=0xFF).config
    context.tx_pdu_id = 0
    context.can_tp.can_tp_init(context.configuration)


@when('we call CanTp_Transmit for a large block of tx data')
def step_impl(context):
    context.tx_data = 'I am a very large block of tx data, which will be transmitted over segmented transmission...'
    context.tx_pdu_info = Helper.create_pdu_info(context.can_tp, context.tx_data)
    context.return_value = context.can_tp.can_tp_transmit(context.tx_pdu_id, context.tx_pdu_info)


@step('we perform the transmission process correctly')
def step_impl(context):
    current_can_if_transmit_count = context.can_tp.can_if_transmit.call_count
    while context.can_tp.pdu_r_can_tp_tx_confirmation.call_count == 0:
        context.can_tp.can_tp_main_function()
        if current_can_if_transmit_count != context.can_tp.can_if_transmit.call_count:
            context.can_tp.can_tp_tx_confirmation(context.tx_pdu_id, E_OK)
            if context.can_tp.can_if_transmit.call_count == 1:
                fc = Helper.create_rx_fc_can_frame(bs=0)
                context.can_tp.can_tp_rx_indication(context.tx_pdu_id, Helper.create_pdu_info(context.can_tp, fc))
            current_can_if_transmit_count = context.can_tp.can_if_transmit.call_count
    assert context.can_tp.pdu_r_can_tp_tx_confirmation.called_once_with(context.tx_pdu_id, E_OK)


@when('we assemble the pPduInfo.SduDataPtr of CanIf_Transmit parameter')
def step_impl(context):
    tx_data = context.can_tp.can_if_tx_data

    # FF assertions.
    assert tx_data[0][0] == (1 << 4) | ((len(context.tx_data) & 0x0F00) >> 8)
    assert tx_data[0][1] == len(context.tx_data) & 0x00FF
    assert tx_data[0][2:] == [ord(c) for c in context.tx_data[0:6]]

    # CF assertions.
    for sn, fi, ss, se in list((fi & 0x0F, fi, fi * 7 - 1, 6 + fi * 7) for fi in range(len(tx_data)))[1:]:
        assert tx_data[fi][0] == (2 << 4) | (sn & 0x0F)
        assert tx_data[fi][1:len(context.tx_data[ss:se]) + 1] == [ord(c) for c in context.tx_data[ss:se]]

    # last CF padding assertions.
    assert tx_data[-1][(len(context.tx_data) - 6) % 7 + 1:] == [0xFF] * (8 - ((len(context.tx_data) - 6) % 7 + 1))
