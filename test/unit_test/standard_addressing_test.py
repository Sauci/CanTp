from math import ceil
from unit_test import *


class TestSWS00350:
    """
    The received data link layer data length (RX_DL) shall be derived from the first received payload length of the CAN
    frame/PDU (CAN_DL) as follows:
    - For CAN_DL values less than or equal to eight bytes the RX_DL value shall be eight.
    - For CAN_DL values greater than eight bytes the RX_DL value equals the CAN_DL value.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_sf_can_frame(payload=[Helper.dummy_byte] * data_size)
        pdu_info = Helper.create_pdu_info(handle, can_frame)
        handle.lib.CanTp_RxIndication(pdu_id, pdu_info)
        handle.mock.pdu_r_can_tp_start_of_reception.assert_called_once_with(ANY, ANY, 8, ANY)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_br=0)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * data_size)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.lib.CanTp_MainFunction()
        handle.mock.pdu_r_can_tp_start_of_reception.assert_called_once_with(ANY, ANY, data_size, ANY)


@pytest.mark.parametrize('data_size', multi_frames_sizes)
@pytest.mark.parametrize('bs', [pytest.param(1, id='BS = 1'),
                                pytest.param(10, id='BS = 10'),
                                pytest.param(15, id='BS = 15')])
def test_sequence_number(handle, data_size, bs):
    """
    6.5.4.2 SequenceNumber (SN) parameter definition
    The parameter SN is used in the CF N_PDU to specify the order of the consecutive frames.

    The SN shall start with zero (0) for all segmented messages. The FF shall be assigned the value zero (0). It does
    not include an explicit SequenceNumber in the N_PCI field but shall be treated as the segment number zero (0).

    The SN of the first CF that immediately follows the FF shall be set to one (1).

    The SN shall be incremented by one (1) for each new CF that is transmitted during a segmented message transmission.

    The SN value shall not be affected by any FC frame.
    When the SN reaches the value of fifteen (15), it shall wraparound and be set to zero (0) for the next CF.
    """
    ff_payload_size = 6
    cf_payload_size = 7

    pdu_id = 0
    configurator = Helper.create_single_tx_sdu_config(handle)
    user_pdu = Helper.create_pdu_info(handle, [Helper.dummy_byte] * data_size)
    fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=bs, st_min=0)

    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_Transmit(pdu_id, user_pdu)
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
    expected_sn = 1
    num_of_blocks = ceil(((data_size - ff_payload_size) / cf_payload_size) / bs)
    num_of_frames_in_last_block = ceil(
        ((data_size - ff_payload_size) - ((num_of_blocks - 1) * bs * cf_payload_size)) / cf_payload_size)
    for block_index in range(num_of_blocks):
        for frame_index in range(bs if block_index < (num_of_blocks - 1) else num_of_frames_in_last_block):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
            print(handle.mock.can_if_transmit_args[-1][1].sdu_data)
            assert handle.mock.can_if_transmit_args[-1][1].sdu_data[0] & 0x0F == expected_sn
            if expected_sn < 15:
                expected_sn += 1
            else:
                expected_sn = 0
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
