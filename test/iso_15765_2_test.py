from math import ceil
from .parameter import *
from .ffi import CanTpTest


class TestSTMinValue:
    """
    6.5.5.5 Definition of SeparationTime (STmin) parameter
    The STmin parameter shall be encoded in byte #3 of the FC N_PCI.
    This time is specified by the receiving entity and shall be kept by the sending network entity for the duration of a
    segmented message transmission.
    The STmin parameter value specifies the minimum time gap allowed between the transmission of consecutive frame
    network protocol data units.

    Hex value | Description
    ----------+---------------------------------------------------------------------------------------------------------
    00 - 7F   | SeparationTime (STmin) range: 0 ms – 127 ms
              | The units of STmin in the range 00 hex – 7F hex are absolute milliseconds (ms).
    ----------+---------------------------------------------------------------------------------------------------------
    80 – F0   | Reserved
              | This range of values is reserved by this part of ISO 15765.
    ----------+---------------------------------------------------------------------------------------------------------
    F1 – F9   | SeparationTime (STmin) range: 100 μs – 900 μs
              | The units of STmin in the range F1 hex – F9 hex are even 100 microseconds (μs), where parameter value F1
              | hex represents 100 μs and parameter value F9 hex represents 900 μs.
    ----------+---------------------------------------------------------------------------------------------------------
    FA – FF   | Reserved
              | This range of values is reserved by this part of ISO 15765.
    ----------+---------------------------------------------------------------------------------------------------------

    The measurement of the STmin starts after completion of transmission of a ConsecutiveFrame (CF) and ends at the
    request for the transmission of the next CF.

    If an FC N_PDU message is received with a reserved ST parameter value, then the sending network entity shall use the
    longest ST value specified by this part of ISO 15765 (7F hex – 127 ms) instead of the value received from the
    receiving network entity for the duration of the ongoing segmented message transmission.
    """

    @pytest.mark.parametrize('st_min, call_count', [
        pytest.param(v,
                     lambda st_min: st_min * 1000,
                     id='STmin = {} [ms]'.format(v)) for v in range(0x00, 0x7F)] + [
                                 pytest.param(v,
                                              lambda st_min: 0x7F * 1000,
                                              id='STmin = reserved (0x{:02X})'.format(v)) for v in
                                 (i + 0x80 for i in range(0xF0 - 0x80 + 0x01))] + [
                                 pytest.param(0xF1 + v,
                                              lambda st_min: (st_min & 0x0F) * 100,
                                              id='STmin = {} [us]'.format(100 + v * 100)) for v in range(9)] + [
                                 pytest.param(v,
                                              lambda st_min: 0x7F * 1000,
                                              id='STmin = reserved (0x{:02X})'.format(v)) for v in
                                 (i + 0xFA for i in range(0xFF - 0xFA + 0x01))])
    def test_sender_side(self, st_min, call_count):
        handle = CanTpTest(DefaultSender(padding=0xFF))
        fc = handle.get_receiver_flow_control(padding=0xFF, bs=0, st_min=st_min)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * 100))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 1  # sent FF
        handle.can_if_transmit.assert_called_once()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2  # sent first CF
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        for _ in range(call_count(st_min)):
            handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2  # wait for timeout
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 3  # sent next CF after timeout

    @pytest.mark.parametrize('st_min, expected',
                             [pytest.param(v, v, id='STmin = {} [ms]'.format(v)) for v in range(0x00, 0x7F)] +
                             [pytest.param(v, 127, id='STmin = reserved (0x{:02X})'.format(v)) for v in
                             (i + 0x80 for i in range(0xF0 - 0x80 + 0x01))] +
                             [pytest.param(0xF1 + v, 0xF1 + v, id='STmin = {} [us]'.format(100 + v * 100)) for v in range(9)] +
                             [pytest.param(v, 127, id='STmin = reserved (0x{:02X})'.format(v)) for v in
                             (i + 0xFA for i in range(0xFF - 0xFA + 0x01))])
    def test_receiver_side(self, st_min, expected):
        handle = CanTpTest(DefaultReceiver(st_min=st_min))
        ff, _ = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[2] == expected


@pytest.mark.skip('non-deterministic fails, should be investigated...')
@pytest.mark.parametrize('data_size', multi_frames_sizes)
@pytest.mark.parametrize('bs', block_sizes)
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
    user_pdu = Helper.create_tx_pdu_info(handle, [Helper.dummy_byte] * data_size)
    fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=bs, st_min=0)

    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_Transmit(pdu_id, user_pdu)
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_rx_pdu_info(handle, fc_frame))
    expected_sn = 1
    if bs != 0:
        num_of_blocks = ceil(((data_size - ff_payload_size) / cf_payload_size) / bs)
    else:
        num_of_blocks = 1
    num_of_frames_in_last_block = ceil(
        ((data_size - ff_payload_size) - ((num_of_blocks - 1) * bs * cf_payload_size)) / cf_payload_size)
    for block_index in range(num_of_blocks):
        for frame_index in range(bs if block_index < (num_of_blocks - 1) else num_of_frames_in_last_block):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
            assert handle.can_if_transmit.call_args_list[-1][0][1].SduDataPtr[0] & 0x0F == expected_sn
            if expected_sn < 15:
                expected_sn += 1
            else:
                expected_sn = 0
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_rx_pdu_info(handle, fc_frame))
