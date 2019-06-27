from unittest.mock import ANY
from .parameter import *
from .ffi import CanTpTest


class TestSWS00031:
    """
    If development error detection for the CanTp module is enabled the CanTp module shall raise an error (CANTP_E_UNINIT
    ) when the PDU Router or CAN Interface tries to use any function (except CanTp_GetVersionInfo) before the function
    CanTp_Init has been called.
    """

    def test_shutdown(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_Shutdown()
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_transmit(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_Transmit(0, handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_cancel_transmit(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_CancelTransmit(0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_cancel_receive(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_CancelReceive(0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_change_parameter(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_ChangeParameter(0, 0, 0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_read_parameter(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_ReadParameter(0, 0, handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    def test_main_function(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))


class TestSWS00057:
    """
    If unexpected frames are received, the CanTp module shall behave according to the table below. This table specifies
    the N-PDU handling considering the current CanTp internal status (CanTp status).

    CanTp     | Reception of
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    status    | SF N-PDU           | FF N-PDU           | CF N-PDU           | FC N-PDU           | Unknown n N-PDU
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    Segmented | Full-duplex:       | Full-duplex:       | Full-duplex:       | If awaited,        | Ignore
    transmit  | If a reception is  | If a reception is  | If a reception is  | process the FC     |
    in        | in progress        | in progress        | in progress        | N-PDU, otherwise   |
    progress  | process it         | process it         | process it         | ignore it.         |
              | according to the   | according to the   | according to the   |                    |
              | cell below,        | cell below,        | cell below,        |                    |
              | otherwise process  | otherwise process  | otherwise ignore   |                    |
              | the SF N-PDU as    | the FF N-PDU as    | it.                |                    |
              | the start of a new | the start of a new |                    |                    |
              | reception.         | reception.         |                    |                    |
              | Half-duplex:       | Half-duplex:       | Half-duplex:       |                    |
              | Ignore.            | Ignore.            | Ignore.            |                    |
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    Segmented | Terminate the      | Terminate the      | Process the CF     | If a transmission  | Ignore
    Receive   | current reception, | current reception, | N-PDU in the       | is in progress     |
    in        | report an          | report an          | on-going reception | process it         |
    progress  | indication, with   | indication, with   | and perform the    | according to the   |
              | parameter Result   | parameter Result   | required checks    | cell above,        |
              | set to E_NOT_OK,   | set to E_NOT_OK,   | (e.g. SN in right  | otherwise ignore   |
              | to the upper layer | to the upper layer | order).            | it.                |
              | , and process the  | , and process the  |                    |                    |
              | SF N-PDU as the    | FF N-PDU as the    |                    |                    |
              | start of a new     | start of a new     |                    |                    |
              | reception.         | reception.         |                    |                    |
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    Idle1     | Process the SF     | Process the FF     | Ignore             | Ignore             | Ignore
              | N-PDU as the start | N-PDU as the start |                    |                    |
              | of a new           | of a new           |                    |                    |
              | reception.         | reception.         |                    |                    |
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    """

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_sf_reception_while_segmented_transmit_is_in_progress_half_duplex(self, af):
        handle = CanTpTest(DefaultSender(af=af, n_cs=0))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)  # exactly one CF.
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        sf = handle.get_receiver_single_frame(af=af)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))
        handle.det_report_runtime_error.assert_not_called()

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_ff_reception_while_segmented_transmit_is_in_progress_half_duplex(self, af):
        handle = CanTpTest(DefaultSender(af=af, n_cs=0))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)  # exactly one CF.
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        ff, _ = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))
        handle.det_report_runtime_error.assert_not_called()

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_cf_reception_while_segmented_transmit_is_in_progress_half_duplex(self, af):
        handle = CanTpTest(DefaultSender(af=af, n_cs=0))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        _, cfs = handle.get_receiver_multi_frame()
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))
        handle.det_report_runtime_error.assert_not_called()

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_sf_reception_while_segmented_transmit_is_in_progress_full_duplex(self, af):
        handle = CanTpTest(DefaultFullDuplex(af=af))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)  # exactly one CF.
        sf = handle.get_receiver_single_frame(af=af)
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        assert handle.pdu_r_can_tp_start_of_reception.call_count == 2
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[0][0][1] == handle.define('E_OK')
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[1][0][1] == handle.define('E_NOT_OK')
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[2][0][1] == handle.define('E_OK')
        handle.det_report_runtime_error.assert_called_once_with(ANY, handle.define('CANTP_I_RX_SF'), ANY, handle.define('CANTP_E_UNEXP_PDU'))

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_ff_reception_while_segmented_transmit_is_in_progress_full_duplex(self, af):
        handle = CanTpTest(DefaultFullDuplex(af=af))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)  # exactly one CF.
        ff, _ = handle.get_receiver_multi_frame(af=af)
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        assert handle.pdu_r_can_tp_start_of_reception.call_count == 2
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, handle.define('CANTP_I_RX_FF'), ANY, handle.define('CANTP_E_UNEXP_PDU'))

    @pytest.mark.parametrize('af', addressing_formats)
    def test_unexpected_cf_reception_while_segmented_transmit_is_in_progress_full_duplex(self, af):
        handle = CanTpTest(DefaultFullDuplex(af=af))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        _, cfs = handle.get_receiver_multi_frame()
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('channel_mode', channel_modes)
    def test_unexpected_fc_reception_while_segmented_transmit_is_in_progress(self, af, channel_mode):
        handle = CanTpTest(DefaultSender(af=af, ch_mode=channel_mode, n_cs=0))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_OK'))

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('channel_mode', channel_modes)
    def test_unexpected_sf_reception_while_segmented_receive_is_in_progress(self, af, channel_mode):
        handle = CanTpTest(DefaultReceiver(af=af, ch_mode=channel_mode))
        rx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        ff, _ = handle.get_receiver_multi_frame(af=af, payload=rx_data)
        sf = handle.get_receiver_single_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        assert handle.pdu_r_can_tp_start_of_reception.call_count == 2
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[0][0][1] == handle.define('E_NOT_OK')
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[1][0][1] == handle.define('E_OK')
        handle.det_report_runtime_error.assert_called_once_with(ANY, handle.define('CANTP_I_RX_SF'), ANY, handle.define('CANTP_E_UNEXP_PDU'))

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('channel_mode', channel_modes)
    def test_unexpected_ff_reception_while_segmented_receive_is_in_progress(self, af, channel_mode):
        handle = CanTpTest(DefaultReceiver(af=af, ch_mode=channel_mode))
        rx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        ff, cfs = handle.get_receiver_multi_frame(af=af, payload=rx_data)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
        assert handle.pdu_r_can_tp_start_of_reception.call_count == 2
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[0][0][1] == handle.define('E_NOT_OK')
        assert handle.pdu_r_can_tp_rx_indication.call_args_list[1][0][1] == handle.define('E_OK')
        handle.det_report_runtime_error.assert_called_once_with(ANY, handle.define('CANTP_I_RX_FF'), ANY, handle.define('CANTP_E_UNEXP_PDU'))

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('channel_mode', channel_modes)
    def test_unexpected_cf_reception_while_segmented_receive_is_in_progress(self, af, channel_mode):
        handle = CanTpTest(DefaultReceiver(af=af, ch_mode=channel_mode))
        rx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        ff, cfs = handle.get_receiver_multi_frame(af=af, payload=rx_data)
        cf_ok = list(cfs[0])
        cf_ko = list(cfs[0])
        cf_ko[8 - handle.get_payload_size(af, 'CF') - 1] = 34
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf_ko))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf_ok))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()
        assert handle.pdu_r_can_tp_copy_rx_data.call_count == 2
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_OK'))

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('channel_mode', channel_modes)
    def test_unexpected_fc_reception_while_segmented_receive_is_in_progress(self, af, channel_mode):
        handle = CanTpTest(DefaultReceiver(af=af, ch_mode=channel_mode))
        rx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        ff, cfs = handle.get_receiver_multi_frame(af=af, payload=rx_data)
        fc = handle.get_receiver_flow_control(af=af, bs=0, st_min=0, padding=0xFF)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()
        assert handle.pdu_r_can_tp_copy_rx_data.call_count == 2
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_OK'))


class TestSWS00079:
    """
    When receiving an SF or an FF N-PDU, the CanTp module shall notify the upper layer (PDU Router) about this reception
    using the PduR_CanTpStartOfReception function.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, data_size):
        handle = CanTpTest(DefaultReceiver())
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_single_frame()))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, data_size):
        handle = CanTpTest(DefaultReceiver())
        ff, _ = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()


class TestSWS00081:
    """
    After the reception of a First Frame or Single Frame, if the function PduR_CanTpStartOfReception() returns
    BUFREQ_E_NOT_OK to the CanTp module, the CanTp module shall abort the reception of this N-SDU. No Flow Control will
    be sent and PduR_CanTpRxIndication() will not be called in this case.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, data_size):
        handle = CanTpTest(DefaultReceiver())
        handle.pdu_r_can_tp_start_of_reception.return_value = handle.lib.BUFREQ_E_NOT_OK
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_single_frame()))
        handle.pdu_r_can_tp_rx_indication.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, data_size):
        handle = CanTpTest(DefaultReceiver())
        ff, _ = handle.get_receiver_multi_frame()
        handle.pdu_r_can_tp_start_of_reception.return_value = handle.lib.BUFREQ_E_NOT_OK
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.pdu_r_can_tp_rx_indication.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()


class TestSWS00093:
    """
    If a multiple segmented session occurs (on both receiver and sender side) with a handle whose communication type is
    functional, the CanTp module shall reject the request and report the runtime error code CANTP_E_INVALID_TATYPE to
    the Default Error Tracer.
    """

    def test_receiver_side(self):
        handle = CanTpTest(DefaultReceiver(com_type='CANTP_FUNCTIONAL'))
        ff, _ = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_TATYPE'))

    def test_sender_side(self):
        handle = CanTpTest(DefaultSender(com_type='CANTP_FUNCTIONAL'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * 8))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_TATYPE'))


def test_sws_00176():
    """
    The function CanTp_Transmit() shall be asynchronous.
    """
    handle = CanTpTest(DefaultSender())
    handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * 10))
    handle.can_if_transmit.assert_not_called()
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_called_once()


@pytest.mark.parametrize('data_size', multi_frames_sizes)
@pytest.mark.parametrize('n_br', n_br_timeouts)
def test_sws_00222(data_size, n_br):
    """
    While the timer N_Br is active, the CanTp module shall call the service PduR_CanTpCopyRxData() with a data length 0
    (zero) and NULL_PTR as data buffer during each processing of the MainFunction.
    """
    config = DefaultReceiver(n_br=n_br, bs=0, wft_max=1)
    handle = CanTpTest(config, rx_buffer_size=data_size - 1)
    ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    for _ in range(int(n_br / config.main_period)):
        handle.lib.CanTp_MainFunction()
        assert handle.pdu_r_can_tp_copy_rx_data.call_args[0][1].SduLength == 0
        assert handle.pdu_r_can_tp_copy_rx_data.call_args[0][1].SduDataPtr == handle.ffi.NULL
    assert handle.pdu_r_can_tp_copy_rx_data.call_count == int(n_br / config.main_period) + 1


@pytest.mark.parametrize('wft_max', wait_for_tx_max)
def test_sws_00223(wft_max):
    """
    The CanTp module shall send a maximum of WFTmax consecutive FC(WAIT) N-PDU. If this number is reached, the CanTp
    module shall abort the reception of this N-SDU (the receiver did not send any FC N-PDU, so the N_Bs timer expires on
    the sender side and then the transmission is aborted) and a receiving indication with E_NOT_OK occurs.
    """
    handle = CanTpTest(DefaultReceiver(n_br=0.0, bs=0, wft_max=wft_max), rx_buffer_size=8)
    ff, _ = handle.get_receiver_multi_frame(payload=(dummy_byte,) * 10)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    for _ in range(wft_max):
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_count == wft_max
    handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))


@pytest.mark.parametrize('bs', block_sizes)
@pytest.mark.parametrize('data_size', multi_frames_sizes)
def test_sws_00224(bs, data_size):
    """
    When the Rx buffer is large enough for the next block (directly after the First Frame or the last Consecutive Frame
    of a block, or after repeated calls to PduR_CanTpCopyRxData() according to SWS_CanTp_00222), the CanTp module shall
    send a Flow Control N-PDU with ClearToSend status (FC(CTS)) and shall then expect the reception of Consecutive Frame
    N-PDUs.
    """
    handle = CanTpTest(DefaultReceiver(bs=bs), rx_buffer_size=data_size)
    ff, cfs = handle.get_receiver_multi_frame(payload=(dummy_byte,) * data_size)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
    assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] & 0x0F == 0


class TestSWS00229:
    """
    If the task was aborted due to As, Bs, Cs, Ar, Br, Cr timeout, the CanTp module shall raise the DET error
    CANTP_E_RX_COM (in case of a reception operation) or CANTP_E_TX_COM (in case of a transmission operation). If the
    task was aborted due to any other protocol error, the CanTp module shall raise the runtime error code CANTP_E_COM to
    the Default Error Tracer.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes + multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    def test_as_timeout(self, data_size, n_as):
        config = DefaultSender(n_as=n_as)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        for _ in range(int(n_as / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_AS'), ANY, handle.define('CANTP_E_TX_COM'))

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    def test_bs_timeout(self, data_size, n_bs):
        config = DefaultSender(n_bs=n_bs)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        for _ in range(int(n_bs / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_BS'), ANY, handle.define('CANTP_E_TX_COM'))

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_cs', n_cs_timeouts)
    def test_cs_timeout(self, data_size, n_cs):
        config = DefaultSender(n_cs=n_cs)
        handle = CanTpTest(config)
        fc_frame = handle.get_receiver_flow_control(padding=0xFF, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc_frame))
        # TODO: add test for overflow return values.
        handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_E_BUSY
        for _ in range(int(n_cs / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_CS'), ANY, handle.define('CANTP_E_TX_COM'))

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ar', n_ar_timeouts)
    def test_ar_timeout(self, data_size, n_ar):
        config = DefaultReceiver(n_ar=n_ar)
        handle = CanTpTest(config)
        ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        for _ in range(int(n_ar / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_AR'), ANY, handle.define('CANTP_E_RX_COM'))

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('n_br', n_br_timeouts)
    def test_br_timeout(self, data_size, af, n_br):
        config = DefaultReceiver(n_br=n_br, af=af)
        handle = CanTpTest(config, rx_buffer_size=CanTpTest.get_payload_size(af, 'CF') - 1)
        ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        for _ in range(int(n_br / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_BR'), ANY, handle.define('CANTP_E_RX_COM'))

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_cr', n_cr_timeouts)
    def test_cr_timeout(self, data_size, n_cr):
        config = DefaultReceiver(n_cr=n_cr)
        handle = CanTpTest(config)
        ff, _ = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        for _ in range(int(n_cr / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_CR'), ANY, handle.define('CANTP_E_RX_COM'))


class TestSWS00254:
    """
    If development error detection is enabled the function CanTp_CancelTransmit shall check the validity of TxPduId
    parameter. If the parameter value is invalid, the CanTp_CancelTransmit function shall raise the development error
    CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    If the parameter value indicates a cancel transmission request for an N-SDU that it is not on transmission process
    the CanTp module shall report a runtime error code CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the
    service shall return E_NOT_OK.
    """

    def test_invalid_tx_pdu_id(self):
        handle = CanTpTest(DefaultSender())
        assert handle.lib.CanTp_CancelTransmit(1) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_no_tx_operation_in_progress(self):
        handle = CanTpTest(DefaultSender())
        assert handle.lib.CanTp_CancelTransmit(0) == handle.define('E_NOT_OK')
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_OPER_NOT_SUPPORTED'))


def test_sws_00255():
    """
    If the CanTp_CancelTransmit service has been successfully executed the CanTp shall call the PduR_CanTpTxConfirmation
    with notification result E_NOT_OK.
    """

    handle = CanTpTest(DefaultSender())
    handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,)))
    handle.lib.CanTp_CancelTransmit(0)
    handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))


def test_sws_00256():
    """
    The CanTp shall abort the transmission of the current N-SDU if the service returns E_OK.
    """

    handle = CanTpTest(DefaultSender())
    handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,)))
    assert handle.lib.CanTp_CancelTransmit(0) == handle.define('E_OK')


class TestSWS00260:
    """
    If development error detection is enabled the function CanTp_CancelReceive shall check the validity of RxPduId
    parameter. If the parameter value is invalid, the CanTp_CancelReceive function shall raise the development error
    CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    If the parameter value indicates a cancel reception request for an N-SDU that it is not on reception process the
    CanTp module shall report the runtime error code CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the
    service shall return E_NOT_OK.
    """

    def test_invalid_rx_pdu_id(self):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_CancelReceive(1) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_no_rx_operation_in_progress(self):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_CancelReceive(0) == handle.define('E_NOT_OK')
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_OPER_NOT_SUPPORTED'))


@pytest.mark.parametrize('af', addressing_formats)
def test_sws_00261(af):
    """
    The CanTp shall abort the reception of the current N-SDU if the service returns E_OK.
    """

    handle = CanTpTest(DefaultReceiver(af=af))
    ff, cfs = handle.get_receiver_multi_frame((0xFF,) * 80, bs=0, af=af)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    assert handle.lib.CanTp_CancelReceive(0) == handle.define('E_OK')


class TestSWS00262:
    """
    The CanTp shall reject the request for receive cancellation in case of a Single Frame reception or if the CanTp is
    in the process of receiving the last Consecutive Frame of the N-SDU (i.e. the service is called after N-Cr timeout
    is started for the last Consecutive Frame). In this case the CanTp shall return E_NOT_OK.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    def test_single_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af))
        sf = handle.get_receiver_single_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        assert handle.lib.CanTp_CancelReceive(0) == handle.define('E_NOT_OK')

    @pytest.mark.parametrize('af', addressing_formats)
    def test_last_consecutive_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, cfs = handle.get_receiver_multi_frame((0xFF,) * 8, bs=0, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        for cf in cfs[:-1]:
            handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf))
        assert handle.lib.CanTp_CancelReceive(0) == handle.define('E_NOT_OK')


def test_sws_00263():
    """
    If the CanTp_CancelReceive service has been successfully executed the CanTp shall call the PduR_CanTpRxIndication
    with notification result E_NOT_OK.
    """
    handle = CanTpTest(DefaultReceiver())
    ff, _ = handle.get_receiver_multi_frame((0xFF,) * 16)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_CancelReceive(0)
    handle.pdu_r_can_tp_rx_indication.called_once_with(ANY, handle.define('E_NOT_OK'))


class TestSWS00281:
    """
    However, if the message is configured to use an extended or a mixed addressing format, the CanTp module must fill
    the first byte of each transmitted segment (SF, FF and CF) with the N_TA (in case of extended addressing) or N_AE
    (in case of mixed addressing) value. Therefore a CAN NSduId may also be related to a N_TA or N_AE value.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    def test_single_frame(self, af):
        handle = CanTpTest(DefaultSender(af=af))
        tx_data = (dummy_byte,) * handle.get_payload_size(af, 'SF')
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        if af in ('CANTP_EXTENDED',):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ta
        elif af in ('CANTP_MIXED', 'CANTP_MIXED29BIT'):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ae
        elif af in ('CANTP_STANDARD', 'CANTP_NORMALFIXED'):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] not in (default_n_ta, default_n_ae)
        else:
            pytest.fail()

    @pytest.mark.parametrize('af', addressing_formats)
    def test_first_frame(self, af):
        handle = CanTpTest(DefaultSender(af=af))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        if af in ('CANTP_EXTENDED',):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ta
        elif af in ('CANTP_MIXED', 'CANTP_MIXED29BIT'):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ae
        elif af in ('CANTP_STANDARD', 'CANTP_NORMALFIXED'):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] not in (default_n_ta, default_n_ae)
        else:
            pytest.fail()

    @pytest.mark.parametrize('af', addressing_formats)
    def test_consecutive_frame(self, af):
        handle = CanTpTest(DefaultSender(af=af))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        cf = handle.get_receiver_flow_control(af=af)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2
        if af in ('CANTP_EXTENDED',):
            assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] == default_n_ta
        elif af in ('CANTP_MIXED', 'CANTP_MIXED29BIT'):
            assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] == default_n_ae
        elif af in ('CANTP_STANDARD', 'CANTP_NORMALFIXED'):
            assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] not in (default_n_ta, default_n_ae)
        else:
            pytest.fail()


@pytest.mark.parametrize('af', addressing_formats)
def test_sws_00283(af):
    """
    For extended addressing format, the first data byte of the FC also contains the N_TA value or a unique combination
    of N_TA and N_TAtype value. For mixed addressing format, the first data byte of the FC contains the N_AE value.
    """

    handle = CanTpTest(DefaultReceiver(af=af))
    ff, _ = handle.get_receiver_multi_frame(af=af)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_called_once()
    if af in ('CANTP_EXTENDED',):
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ta
    elif af in ('CANTP_MIXED', 'CANTP_MIXED29BIT'):
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == default_n_ae
    elif af in ('CANTP_STANDARD', 'CANTP_NORMALFIXED'):
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] not in (default_n_ta, default_n_ae)
    else:
        pytest.fail()


class TestSWS00293:

    @pytest.mark.parametrize('code_name, value', [pytest.param('CANTP_E_PARAM_CONFIG', 0x01),
                                                  pytest.param('CANTP_E_PARAM_ID', 0x02),
                                                  pytest.param('CANTP_E_PARAM_POINTER', 0x03),
                                                  pytest.param('CANTP_E_INIT_FAILED', 0x04),
                                                  pytest.param('CANTP_E_UNINIT', 0x20),
                                                  pytest.param('CANTP_E_INVALID_TX_ID', 0x30),
                                                  pytest.param('CANTP_E_INVALID_RX_ID', 0x40)])
    def test_error_codes(self, code_name, value):
        handle = CanTpTest(DefaultSender())
        assert handle.define(code_name) == value

    @pytest.mark.skip(reason='not implemented')
    def test_e_init_failed(self):
        pass

    def test_e_invalid_rx_id(self):
        handle = CanTpTest(DefaultReceiver())
        sf = handle.get_receiver_single_frame()
        handle.lib.CanTp_RxIndication(1, handle.get_pdu_info(sf))
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_RX_ID'))

    def test_e_invalid_tx_id(self):
        handle = CanTpTest(DefaultSender())
        handle.lib.CanTp_Transmit(1, handle.get_pdu_info((dummy_byte,) * 100))
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_TX_ID'))


@pytest.mark.parametrize('parameter', change_parameter_api)
def test_sws_00304(parameter):
    """
    If the change of a parameter is requested for an N-SDU that is on reception process the service
    CanTp_ChangeParameter immediately returns E_NOT_OK and no parameter value is changed
    """
    handle = CanTpTest(DefaultReceiver())
    ff, _ = handle.get_receiver_multi_frame((0xFF,) * 16)
    parameter = getattr(handle.lib, parameter)
    original = handle.ffi.new('uint16 *')
    modified = handle.ffi.new('uint16 *')
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_ReadParameter(0, parameter, original)
    assert handle.lib.CanTp_ChangeParameter(0, parameter, original[0] + 1) == handle.define('E_NOT_OK')
    handle.det_report_error.assert_not_called()
    handle.lib.CanTp_ReadParameter(0, parameter, modified)
    assert modified[0] == original[0]


class TestSWS00305:
    """
    If development error detection is enabled, the function CanTp_ChangeParameter shall check the validity of function
    parameters (Identifier, Parameter and requested value). If any of the parameter value is invalid, the
    CanTp_ChangeParameter function shall raise the development error CANTP_E_PARAM_ID and return E_NOT_OK
    """

    @pytest.mark.parametrize('parameter', change_parameter_api)
    def test_invalid_pdu_id(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(1, getattr(handle.lib, parameter), 0) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_invalid_parameter(self):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(0, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, 0) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    @pytest.mark.parametrize('parameter', change_parameter_api)
    def test_invalid_value(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(0, getattr(handle.lib, parameter), 0xFF + 1) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))


def test_sws_00318():
    """
    After the reception of a First Frame, if the function PduR_CanTpStartOfReception() returns BUFREQ_E_OVFL to the
    CanTp module, the CanTp module shall send a Flow Control N-PDU with overflow status (FC(OVFLW)) and abort the N-SDU
    reception.
    """
    handle = CanTpTest(DefaultReceiver())
    ff, _ = handle.get_receiver_multi_frame((0xFF,) * 16)
    handle.pdu_r_can_tp_start_of_reception.return_value = handle.lib.BUFREQ_E_OVFL
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] & 0x0F == 2
    handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_BUFFER_OVFLW'), ANY, handle.define('CANTP_E_RX_COM'))
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_called_once()


def test_sws_00319():
    """
    If DET is enabled the function CanTp_GetVersionInfo shall rise CANTP_E_PARAM_POINTER error if the argument is a NULL
    pointer and return without any action.
    """
    handle = CanTpTest(DefaultSender())
    handle.lib.CanTp_GetVersionInfo(handle.ffi.NULL)
    handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))


def test_sws_00321():
    """
    If DET is enabled the function CanTp_Transmit shall rise CANTP_E_PARAM_POINTER error if the argument PduInfoPtr is a
    NULL pointer and return without any action.
    """
    handle = CanTpTest(DefaultSender())
    handle.lib.CanTp_Transmit(0, handle.ffi.NULL)
    handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))


def test_sws_00322():
    """
    If DET is enabled the function CanTp_RxIndication shall rise CANTP_E_PARAM_POINTER error if the argument PduInfoPtr
    is a NULL pointer and return without any action.
    """
    handle = CanTpTest(DefaultReceiver())
    handle.lib.CanTp_RxIndication(0, handle.ffi.NULL)
    handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))


class TestSWS00324:
    """
    If development error detection is enabled the function CanTp_ReadParameter shall check the validity of function
    parameters (Id and Parameter). If any of the parameter value is invalid, the CanTp_ReadParameter function shall
    raise the development error CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    """

    def test_invalid_pdu_id(self):
        handle = CanTpTest(DefaultReceiver())
        parameter = handle.ffi.new('uint16 *', 0)
        assert handle.lib.CanTp_ReadParameter(1, handle.lib.TP_STMIN, parameter) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_invalid_parameter(self):
        handle = CanTpTest(DefaultReceiver())
        parameter = handle.ffi.new('uint16 *', 0)
        assert handle.lib.CanTp_ReadParameter(0, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, parameter) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))


class TestSWS00329:
    """
    CanTp shall provide the content of the FF/SF to PduR using the parameter TpSduInfoPtr of
    PduR_CanTpStartOfReception().
    """

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, af, data_size):
        handle = CanTpTest(DefaultReceiver(af=af))
        sf = handle.get_receiver_single_frame(payload=(dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        for idx in range(data_size):
            assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].SduDataPtr[idx] == dummy_byte

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, af, data_size):
        config = DefaultReceiver()
        config['configurations'][0]['channels'][0]['receivers'][0]['addressing_format'] = af
        handle = CanTpTest(config)
        ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        for idx in range(handle.get_payload_size(af, 'FF')):
            assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].SduDataPtr[idx] == dummy_byte


class TestSWS00339:
    """
    After the reception of a First Frame or Single Frame, if the function PduR_CanTpStartOfReception() returns BUFREQ_OK
    with a smaller available buffer size than needed for the already received data, the CanTp module shall abort the
    reception of the N-SDU and call PduR_CanTpRxIndication() with the result E_NOT_OK.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, af, data_size):
        config = DefaultReceiver()
        config['configurations'][0]['channels'][0]['receivers'][0]['addressing_format'] = af
        handle = CanTpTest(config, rx_buffer_size=data_size - 1)
        sf = handle.get_receiver_single_frame(payload=(dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_multi_frame(self, af, data_size):
        config = DefaultReceiver()
        config['configurations'][0]['channels'][0]['receivers'][0]['addressing_format'] = af
        handle = CanTpTest(config, rx_buffer_size=CanTpTest.get_payload_size(af, 'FF') - 1)
        ff, _ = handle.get_receiver_multi_frame(payload=(dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()


@pytest.mark.parametrize('af', addressing_formats)
def test_sws_00345(af):
    """
    If frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD frames) are used for a Rx N-SDU and
    CanTpRxPaddingActivation is equal to CANTP_ON, then CanTp receives by means of CanTp_RxIndication() call an SF Rx
    N-PDU belonging to that N-SDU, with a length smaller than eight bytes (i.e. PduInfoPtr.SduLength < 8), CanTp shall
    reject the reception. The runtime error code CANTP_E_PADDING shall be reported to the Default Error Tracer.
    """
    handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
    sf_pdu = handle.get_pdu_info(handle.get_receiver_single_frame(payload=(dummy_byte,) * 1, af=af))
    assert sf_pdu.SduLength < 8
    handle.lib.CanTp_RxIndication(0, sf_pdu)
    handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
    sf_pdu = handle.get_pdu_info(handle.get_receiver_single_frame(payload=(dummy_byte,) * handle.get_payload_size(af, 'SF'), af=af))
    assert sf_pdu.SduLength == 8
    handle.lib.CanTp_RxIndication(0, sf_pdu)
    assert handle.det_report_runtime_error.call_count == 1
    assert handle.pdu_r_can_tp_rx_indication.called_once_with(ANY, handle.define('E_OK'))


class TestSWS00346:
    """
    If frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD frames) are used for a Rx N-SDU and
    CanTpRxPaddingActivation is equal to CANTP_ON, and CanTp receives by means of CanTp_RxIndication() call a last CF Rx
    N-PDU belonging to that N- SDU, with a length smaller than eight bytes (i.e. PduInfoPtr. SduLength != 8), CanTp
    shall abort the ongoing reception by calling PduR_CanTpRxIndication() with the result E_NOT_OK. The runtime error
    code CANTP_E_PADDING shall be reported to the Default Error Tracer.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    def test_invalid_single_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        sf = handle.get_receiver_single_frame(payload=(dummy_byte,) * (handle.get_payload_size(af, 'SF') - 1), af=af)
        sf_pdu = handle.get_pdu_info(sf)
        assert sf_pdu.SduLength != 8
        handle.lib.CanTp_RxIndication(0, sf_pdu)
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))

    @pytest.mark.parametrize('af', addressing_formats)
    def test_invalid_first_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        ff, _ = handle.get_receiver_multi_frame(payload=(dummy_byte,) * (handle.get_payload_size(af, 'FF') - 1), af=af)
        ff_pdu = handle.get_pdu_info(ff)
        assert ff_pdu.SduLength != 8
        handle.lib.CanTp_RxIndication(0, ff_pdu)
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))

    @pytest.mark.parametrize('af', addressing_formats)
    def test_invalid_last_consecutive_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        ff, cfs = handle.get_receiver_multi_frame(payload=(dummy_byte,) * (handle.get_payload_size(af, 'FF') +
                                                                           handle.get_payload_size(af, 'CF') - 1), af=af)
        ff_pdu = handle.get_pdu_info(ff)
        cf_pdu = handle.get_pdu_info(cfs[0])
        assert cf_pdu.SduLength != 8
        handle.lib.CanTp_RxIndication(0, ff_pdu)
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, cf_pdu)
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.lib.CanTp_MainFunction()


@pytest.mark.skip(reason='I don\'t understand this statement...')
class TestSWS00350:
    """
    The received data link layer data length (RX_DL) shall be derived from the first received payload length of the CAN
    frame/PDU (CAN_DL) as follows:
    - For CAN_DL values less than or equal to eight bytes the RX_DL value shall be eight.
    - For CAN_DL values greater than eight bytes the RX_DL value equals the CAN_DL value.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, af, data_size):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        sf = handle.get_receiver_single_frame(payload=(dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once_with(ANY, ANY, 8, ANY)

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, af, data_size):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        ff, _ = handle.get_receiver_multi_frame(payload=(dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_called_once_with(ANY, ANY, data_size, ANY)


def test_sws_00353():
    """
    After the reception of a Single Frame, if the function PduR_CanTpStartOfReception() returns BUFREQ_E_OVFL to the
    CanTp module, the CanTp module shall abort the N-SDU reception.
    """
    handle = CanTpTest(DefaultReceiver())
    handle.pdu_r_can_tp_start_of_reception.return_value = handle.lib.BUFREQ_E_OVFL
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_single_frame()))
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_not_called()


@pytest.mark.parametrize('st_min, call_count', [
    pytest.param(v,
                 lambda st_min: st_min * 1000,
                 id='STmin = {} [ms]'.format(v)) for v in range(0x7F + 0x01)] + [
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
def test_separation_time_minimum_value(st_min, call_count):
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

    handle = CanTpTest(DefaultSender(padding=0xFF))
    fc_frame = handle.get_receiver_flow_control(padding=0xFF, bs=0, st_min=st_min)
    handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * 100))
    handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_count == 1  # sent FF
    handle.can_if_transmit.assert_called_once()
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc_frame))
    handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_count == 2  # sent first CF
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    for _ in range(call_count(st_min)):
        handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_count == 2  # wait for timeout
    handle.lib.CanTp_MainFunction()
    assert handle.can_if_transmit.call_count == 3  # sent next CF after timeout
