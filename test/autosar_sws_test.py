#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import ANY

from .parameter import *
from .conftest import CanTpTest


def assert_rx_session_aborted(handle):
    assert handle.lib.CanTp_AbortedRxSession == handle.define('TRUE')


def assert_tx_session_aborted(handle):
    assert handle.lib.CanTp_AbortedTxSession == handle.define('TRUE')


class TestSWS00031:
    """
    If development error detection for the CanTp module is enabled the CanTp module shall raise an error (CANTP_E_UNINIT
    ) when the PDU Router or CAN Interface tries to use any function (except CanTp_GetVersionInfo) before the function
    CanTp_Init has been called.
    """

    @pytest.mark.parametrize('function, parameters', [
        pytest.param('CanTp_Shutdown', tuple(), id='shutdown'),
        pytest.param('CanTp_Transmit', (lambda h: 0, lambda h: h.ffi.NULL), id='transmit'),
        pytest.param('CanTp_CancelTransmit', (lambda h: 0,), id='cancel_transmit'),
        pytest.param('CanTp_CancelReceive', (lambda h: 0,), id='cancel_receive'),
        pytest.param('CanTp_ChangeParameter', (lambda h: 0, lambda h: 0, lambda h: 0), id='change_parameter'),
        pytest.param('CanTp_ReadParameter', (lambda h: 0, lambda h: 0, lambda h: h.ffi.NULL), id='read_parameter'),
        pytest.param('CanTp_MainFunction', tuple(), id='main_function')])
    def test_uninit_error_raised(self, function, parameters):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        getattr(handle.lib, function)(*[l(handle) for l in parameters])
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_UNINIT'))

    @pytest.mark.parametrize('function, parameters', [
        pytest.param('CanTp_Shutdown', tuple(), id='shutdown'),
        pytest.param('CanTp_Transmit', (lambda h: 0, lambda h: h.ffi.NULL), id='transmit'),
        pytest.param('CanTp_CancelTransmit', (lambda h: 0,), id='cancel_transmit'),
        pytest.param('CanTp_CancelReceive', (lambda h: 0,), id='cancel_receive'),
        pytest.param('CanTp_ChangeParameter', (lambda h: 0, lambda h: 0, lambda h: 0), id='change_parameter'),
        pytest.param('CanTp_ReadParameter', (lambda h: 0, lambda h: 0, lambda h: h.ffi.NULL), id='read_parameter'),
        pytest.param('CanTp_MainFunction', tuple(), id='main_function')])
    def test_uninit_error_not_raised(self, function, parameters):
        handle = CanTpTest(DefaultReceiver(), initialize=True)
        getattr(handle.lib, function)(*[l(handle) for l in parameters])
        if handle.det_report_error.call_count:
            assert handle.det_report_error.call_args[0][3] != handle.define('CANTP_E_UNINIT')


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
        rx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + handle.get_payload_size(af, 'CF') * 2)
        ff, cfs = handle.get_receiver_multi_frame(af=af, payload=rx_data)
        cf_ok = list(cfs[0])
        cf_ko = list(cfs[0])
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf_ok))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cf_ko))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()
        assert handle.pdu_r_can_tp_copy_rx_data.call_count == 2
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))

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

    @pytest.mark.parametrize('status', ['BUFREQ_E_NOT_OK', 'BUFREQ_E_BUSY'])
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, status, data_size):
        handle = CanTpTest(DefaultReceiver())
        handle.pdu_r_can_tp_start_of_reception.return_value = getattr(handle.lib, status)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_single_frame()))
        handle.lib.CanTp_MainFunction()
        assert_rx_session_aborted(handle)
        handle.can_if_transmit.assert_not_called()
        handle.pdu_r_can_tp_rx_indication.assert_not_called()

    @pytest.mark.parametrize('status', ['BUFREQ_E_NOT_OK', 'BUFREQ_E_BUSY'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, status, data_size):
        handle = CanTpTest(DefaultReceiver())
        ff, _ = handle.get_receiver_multi_frame()
        handle.pdu_r_can_tp_start_of_reception.return_value = getattr(handle.lib, status)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.pdu_r_can_tp_rx_indication.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()


class TestSWS00087:
    """
    If PduR_CanTpCopyTxData() returns BUFREQ_E_NOT_OK, the CanTp module shall abort the transmit request and notify the
    upper layer of this failure by calling the callback function PduR_CanTpTxConfirmation() with the result E_NOT_OK.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, data_size):
        handle = CanTpTest(DefaultSender())
        handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_E_NOT_OK
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_tx_session_aborted(handle)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_multi_frame(self, data_size):
        handle = CanTpTest(DefaultSender())
        handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_E_NOT_OK
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_tx_session_aborted(handle)


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
    assert_rx_session_aborted(handle)


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
    def test_as_timeout_not_confirmed(self, data_size, n_as):
        config = DefaultSender(n_as=n_as)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        for _ in range(int(n_as / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_AS'), ANY, handle.define('CANTP_E_TX_COM'))

    @pytest.mark.parametrize('data_size', single_frame_sizes + multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    def test_as_timeout_confirmed(self, data_size, n_as):
        config = DefaultSender(n_as=n_as)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        for _ in range(int(n_as / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()

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
    @pytest.mark.parametrize('return_value', ['BUFREQ_E_BUSY', 'BUFREQ_E_OVFL'])
    def test_cs_timeout(self, data_size, n_cs, return_value):
        config = DefaultSender(n_cs=n_cs)
        handle = CanTpTest(config)
        fc_frame = handle.get_receiver_flow_control(padding=0xFF, bs=0, st_min=0)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc_frame))
        handle.pdu_r_can_tp_copy_tx_data.return_value = getattr(handle.lib, return_value)
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
    assert_tx_session_aborted(handle)


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
    assert_rx_session_aborted(handle)


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


class TestSWS00271:
    """
    If the PduR_CanTpCopyRxData() returns BUFREQ_E_NOT_OK after reception of a Consecutive Frame in a block the CanTp
    shall abort the reception of N-SDU and notify the PduR module by calling the PduR_CanTpRxIndication() with the
    result E_NOT_OK.
    """

    @pytest.mark.parametrize('result', ['BUFREQ_E_NOT_OK', 'BUFREQ_E_OVFL', 'BUFREQ_E_BUSY'])
    def test_single_frame(self, result):
        handle = CanTpTest(DefaultReceiver())
        handle.pdu_r_can_tp_copy_rx_data.return_value = getattr(handle.lib, result)
        sf = handle.get_receiver_single_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(sf))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_rx_session_aborted(handle)

    @pytest.mark.parametrize('result', ['BUFREQ_E_NOT_OK', 'BUFREQ_E_OVFL', 'BUFREQ_E_BUSY'])
    def test_first_frame(self, result):
        handle = CanTpTest(DefaultReceiver())
        handle.pdu_r_can_tp_copy_rx_data.return_value = getattr(handle.lib, result)
        ff, _ = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_rx_session_aborted(handle)

    @pytest.mark.parametrize('result', ['BUFREQ_E_NOT_OK', 'BUFREQ_E_OVFL', 'BUFREQ_E_BUSY'])
    def test_consecutive_frame(self, result):
        handle = CanTpTest(DefaultReceiver())
        ff, cfs = handle.get_receiver_multi_frame()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.pdu_r_can_tp_copy_rx_data.return_value = getattr(handle.lib, result)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_rx_session_aborted(handle)


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
        fc = handle.get_receiver_flow_control(af=af)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
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
    """
    The CanTp module shall be able to detect the following errors:

    Type of error                                               | Relevance   | Related error code         | Value [hex]
    ------------------------------------------------------------+-------------+----------------------------+------------
    API service called with wrong parameter(s): When            | Development | Could be a combination of: |
    CanTp_Transmit is called for a none configured PDU          |             | CANTP_E_PARAM_CONFIG       | 0x01
    identifier or with an identifier for a received PDU.        |             | CANTP_E_PARAM_ID           | 0x02
    ------------------------------------------------------------+-------------+----------------------------+------------
    API service called with a NULL pointer. In case of this     | Development | CANTP_E_PARAM_POINTER      | 0x03
    error, the API service shall return immediately without any |             |                            |
    further action, besides reporting this development error.   |             |                            |
    ------------------------------------------------------------+-------------+----------------------------+------------
    Module initialization has failed, e.g. CanTp_Init() called  | Development | CANTP_E_INIT_FAILED        | 0x04
    with an invalid pointer in postbuild.                       |             |                            |
    ------------------------------------------------------------+-------------+----------------------------+------------
    API service used without module initialization : On any API | Development | CANTP_E_UNINIT             | 0x20
    call except CanTp_Init(), CanTp_GetVersionInfo() and        |             |                            |
    CanTp_MainFunction() if CanTp is in state CANTP_OFF.        |             |                            |
    ------------------------------------------------------------+-------------+----------------------------+------------
    Invalid Transmit PDU identifier (e.g. a service is called   | Development | CANTP_E_INVALID_TX_ID      | 0x30
    with an inexistent Tx PDU identifier).                      |             |                            |
    ------------------------------------------------------------+-------------+----------------------------+------------
    Invalid Receive PDU identifier (e.g. a service is called    | Development | CANTP_E_INVALID_RX_ID      | 0x40
    with an inexistent Rx PDU identifier).                      |             |                            |
    ------------------------------------------------------------+-------------+----------------------------+------------
    """

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

    def test_e_param_pointer(self):
        handle = CanTpTest(DefaultReceiver(), initialize=False)
        handle.lib.CanTp_Init(handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))

    def test_e_invalid_rx_id(self):
        handle = CanTpTest(DefaultReceiver())
        sf = handle.get_receiver_single_frame()
        handle.lib.CanTp_RxIndication(1, handle.get_pdu_info(sf))
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_RX_ID'))

    def test_e_invalid_tx_id(self):
        handle = CanTpTest(DefaultSender())
        handle.lib.CanTp_Transmit(1, handle.get_pdu_info((dummy_byte,) * 100))
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_INVALID_TX_ID'))


@pytest.mark.parametrize('parameter', modifiable_parameter_api)
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

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_invalid_pdu_id(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(1, getattr(handle.lib, parameter), 0) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_invalid_parameter(self):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(0, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, 0) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_invalid_value(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(0, getattr(handle.lib, parameter), 0xFF + 1) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_valid_parameters(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        assert handle.lib.CanTp_ChangeParameter(0, getattr(handle.lib, parameter), 0xFF) == handle.define('E_OK')
        handle.det_report_error.assert_not_called()


@pytest.mark.parametrize('af', addressing_formats)
@pytest.mark.parametrize('data_size', multi_frames_sizes)
def test_sws_00314(af, data_size):
    """
    The CanTp shall check the correctness of each SN received during a segmented reception. In case
    of wrong SN received the CanTp module shall abort reception and notify the upper layer of this
    failure by calling the indication function PduR_CanTpRxIndication() with the result E_NOT_OK.
    """
    handle = CanTpTest(DefaultReceiver(af=af))
    ff, cfs = handle.get_receiver_multi_frame(payload=(dummy_byte,) * data_size, af=af)
    pci_byte = cfs[0][8 - handle.get_payload_size(af, 'CF') - 1]
    cfs[0][8 - handle.get_payload_size(af, 'CF') - 1] = (pci_byte & 0xF0) | (((pci_byte & 0x0F) + 1) & 0x0F)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0]))
    handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
    assert_rx_session_aborted(handle)


class TestSWS00315:
    """
    The CanTp module shall start a timeout observation for N_Bs time at confirmation of the FF transmission, last CF of
    a block transmission and at each indication of FC with FS=WT (i.e. time until reception of the next FC).
    """

    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame_confirmation(self, n_bs, data_size):
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

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('bs', [bs for bs in block_sizes if bs.values[0] != 0])
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    def test_last_consecutive_frame_confirmation(self, af, bs, n_bs):
        config = DefaultSender(af=af, n_bs=n_bs)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * (handle.get_payload_size(af, 'FF') +
                                                                          bs * handle.get_payload_size(af, 'CF') + 1)))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK')) # sent FF
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(bs=bs, af=af)))
        for _ in range(bs):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        for _ in range(int(n_bs / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_BS'), ANY, handle.define('CANTP_E_TX_COM'))

    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_flow_control_wait_indication(self, n_bs, data_size):
        config = DefaultSender(n_bs=n_bs)
        handle = CanTpTest(config)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(fs='wait')))
        for _ in range(int(n_bs / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, handle.define('CANTP_I_N_BS'), ANY, handle.define('CANTP_E_TX_COM'))


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
    assert_rx_session_aborted(handle)


class TestSWS00319:
    """
    If DET is enabled the function CanTp_GetVersionInfo shall rise CANTP_E_PARAM_POINTER error if the argument is a NULL
    pointer and return without any action.
    """

    def test_null_parameter(self):
        handle = CanTpTest(DefaultSender())
        handle.lib.CanTp_GetVersionInfo(handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))

    def test_non_null_parameter(self):
        handle = CanTpTest(DefaultSender())
        version_info = handle.ffi.new('Std_VersionInfoType *')
        handle.lib.CanTp_GetVersionInfo(version_info)
        handle.det_report_error.assert_not_called()


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

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_invalid_pdu_id(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        output = handle.ffi.new('uint16 *', 0)
        assert handle.lib.CanTp_ReadParameter(1, getattr(handle.lib, parameter), output) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    def test_invalid_parameter(self):
        handle = CanTpTest(DefaultReceiver())
        output = handle.ffi.new('uint16 *', 0)
        assert handle.lib.CanTp_ReadParameter(0, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, output) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_ID'))

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_invalid_output(self, parameter):
        # NOTE: this is not specified in AUTOSAR specification.
        handle = CanTpTest(DefaultReceiver())
        output = handle.ffi.NULL
        assert handle.lib.CanTp_ReadParameter(1, getattr(handle.lib, parameter), output) == handle.define('E_NOT_OK')
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PARAM_POINTER'))

    @pytest.mark.parametrize('parameter', modifiable_parameter_api)
    def test_valid_parameters(self, parameter):
        handle = CanTpTest(DefaultReceiver())
        output = handle.ffi.new('uint16 *', 0)
        assert handle.lib.CanTp_ReadParameter(0, getattr(handle.lib, parameter), output) == handle.define('E_OK')
        handle.det_report_error.assert_not_called()


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


class TestSWS00330:
    """
    When CanTp_RxIndication is called for a SF or FF N-PDU with MetaData (indicating a generic connection), the CanTp
    module shall store the addressing information contained in the MetaData of the PDU and use this information for the
    initiation of the connection to the upper layer, for transmission of FC N-PDUs and for identification of CF N-PDUs.
    The addressing information in the MetaData depends on the addressing format:
    - Normal, Extended, Mixed 11 bit: none
    - Normal fixed, Mixed 29 bit: N_SA, N_TA
    """

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_flow_control_transmission_for_addressing_formats_with_meta_data(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af, n_sa=default_n_sa, n_ta=default_n_ta))
        ff, _ = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[0] == n_ta
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[1] == n_sa


class TestSWS00331:
    """
    When calling PduR_CanTpStartOfReception() for a generic connection (N-SDU with MetaData), the CanTp module shall
    forward the extracted addressing information via the MetaData of the N-SDU. The addressing information in the
    MetaData depends on the addressing format:
    - Normal: none
    - Extended: N_TA
    - Mixed 11 bit: N_AE
    - Normal fixed: N_SA, N_TA
    - Mixed 29 bit: N_SA, N_TA, N_AE
    """

    @pytest.mark.parametrize('frame', [pytest.param(lambda h, **kw: h.get_receiver_single_frame(**kw), id='SF'),
                                       pytest.param(lambda h, **kw: h.get_receiver_multi_frame(**kw)[0], id='FF')])
    def test_normal_addressing_format(self, frame):
        handle = CanTpTest(DefaultReceiver(af='CANTP_STANDARD'))
        frame = frame(handle, af='CANTP_STANDARD')
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(frame, meta_data=[]))
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('frame', [pytest.param(lambda h, **kw: h.get_receiver_single_frame(**kw), id='SF'),
                                       pytest.param(lambda h, **kw: h.get_receiver_multi_frame(**kw)[0], id='FF')])
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_extended_addressing_format(self, frame, n_ta):
        handle = CanTpTest(DefaultReceiver(af='CANTP_EXTENDED'))
        frame = frame(handle, af='CANTP_EXTENDED', n_ta=n_ta)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(frame, meta_data=[]))
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[0] == n_ta

    @pytest.mark.parametrize('frame', [pytest.param(lambda h, **kw: h.get_receiver_single_frame(**kw), id='SF'),
                                       pytest.param(lambda h, **kw: h.get_receiver_multi_frame(**kw)[0], id='FF')])
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_mixed_addressing_format(self, frame, n_ae):
        handle = CanTpTest(DefaultReceiver(af='CANTP_MIXED'))
        frame = frame(handle, af='CANTP_MIXED', n_ae=n_ae)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(frame, meta_data=[]))
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[0] == n_ae

    @pytest.mark.parametrize('frame', [pytest.param(lambda h, **kw: h.get_receiver_single_frame(**kw), id='SF'),
                                       pytest.param(lambda h, **kw: h.get_receiver_multi_frame(**kw)[0], id='FF')])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_normal_fixed_addressing_format(self, frame, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af='CANTP_NORMALFIXED'))
        frame = frame(handle, af='CANTP_NORMALFIXED')
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(frame, meta_data=[n_sa, n_ta]))
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[0] == n_sa
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[1] == n_ta

    @pytest.mark.parametrize('frame', [pytest.param(lambda h, **kw: h.get_receiver_single_frame(**kw), id='SF'),
                                       pytest.param(lambda h, **kw: h.get_receiver_multi_frame(**kw)[0], id='FF')])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_mixed_29_bits_addressing_format(self, frame, n_sa, n_ta, n_ae):
        handle = CanTpTest(DefaultReceiver(af='CANTP_MIXED29BIT'))
        frame = frame(handle, af='CANTP_MIXED29BIT', n_ae=n_ae)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(frame, meta_data=[n_sa, n_ta]))
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[0] == n_sa
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[1] == n_ta
        assert handle.pdu_r_can_tp_start_of_reception.call_args[0][1].MetaDataPtr[2] == n_ae


class TestSWS00332:
    """
    When calling CanIf_Transmit() for an FC on a generic connection (N-PDU with MetaData), the CanTp module shall
    provide the stored addressing information via the MetaData of the N-PDU. The addressing information in the MetaData
    depends on the addressing format:
    - Normal, Extended, Mixed 11 bit: none
    - Normal fixed, Mixed 29 bit: N_SA (saved N_TA), N_TA (saved N_SA)
    """

    @pytest.mark.parametrize('af', ['CANTP_STANDARD', 'CANTP_EXTENDED', 'CANTP_MIXED'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_addressing_formats_without_meta_data(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, _ = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_addressing_formats_with_meta_data(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, _ = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[0] == n_ta
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[1] == n_sa


class TestSWS00333:
    """
    When CanTp_RxIndication is called for a CF on a generic connection (N-PDU with MetaData), the CanTp module shall
    check the addressing information contained in the MetaData of the N-PDU against the stored values from the FF.
    """

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_meta_data_pointer(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, cfs = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0], meta_data=None))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_n_sa_value(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, cfs = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0], meta_data=[n_sa + 1, n_ta]))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_n_ta_value(self, af, n_sa, n_ta):
        handle = CanTpTest(DefaultReceiver(af=af))
        ff, cfs = handle.get_receiver_multi_frame(af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(cfs[0], meta_data=[n_sa, n_ta + 1]))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))


class TestSWS00334:
    """
    When CanTp_Transmit is called for an N-SDU with MetaData, the CanTp module shall store the addressing information
    contained in the MetaData of the N-SDU and use this information for transmission of SF, FF, and CF N-PDUs and for
    identification of FC N-PDUs. The addressing information in the MedataData depends on the addressing format:
    - Normal: none
    - Extended: N_TA
    - Mixed 11 bit: N_AE
    - Normal fixed: N_SA, N_TA
    - Mixed 29 bit: N_SA, N_TA, N_AE.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_non_segmented_message_for_standard_addressing_format(self, data_size):
        handle = CanTpTest(DefaultSender(af='CANTP_STANDARD'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_non_segmented_message_for_extended_addressing_format(self, data_size, n_ta):
        handle = CanTpTest(DefaultSender(af='CANTP_EXTENDED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == n_ta

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_non_segmented_message_for_mixed_addressing_format(self, data_size, n_ae):
        handle = CanTpTest(DefaultSender(af='CANTP_MIXED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_ae]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == n_ae

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_non_segmented_message_for_normal_fixed_addressing_format(self, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af='CANTP_NORMALFIXED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[1] == n_ta

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_non_segmented_message_for_mixed_29_bits_format(self, data_size, n_sa, n_ta, n_ae):
        handle = CanTpTest(DefaultSender(af='CANTP_MIXED29BIT'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size,
                                                         meta_data=[n_sa, n_ta, n_ae]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0] == n_ae
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[1] == n_ta

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_segmented_message_for_standard_addressing_format(self, data_size):
        handle = CanTpTest(DefaultSender(af='CANTP_STANDARD'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr == handle.ffi.NULL
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af='CANTP_STANDARD'),
                                                             meta_data=[]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_segmented_message_for_extended_addressing_format(self, data_size, n_ta):
        handle = CanTpTest(DefaultSender(af='CANTP_EXTENDED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].SduDataPtr[0] == n_ta
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af='CANTP_EXTENDED'),
                                                             meta_data=[n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] == n_ta

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_segmented_message_for_mixed_addressing_format(self, data_size, n_ae):
        handle = CanTpTest(DefaultSender(af='CANTP_MIXED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_ae]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].SduDataPtr[0] == n_ae
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af='CANTP_MIXED'),
                                                             meta_data=[n_ae]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] == n_ae

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_segmented_message_for_normal_fixed_addressing_format(self, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af='CANTP_NORMALFIXED'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[1] == n_ta
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af='CANTP_NORMALFIXED'),
                                                             meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[1] == n_ta

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    @pytest.mark.parametrize('n_ae', custom_n_ae)
    def test_segmented_message_for_mixed_29_bits_addressing_format(self, data_size, n_sa, n_ta, n_ae):
        handle = CanTpTest(DefaultSender(af='CANTP_MIXED29BIT'))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size,
                                                         meta_data=[n_sa, n_ta, n_ae]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].SduDataPtr[0] == n_ae
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[1] == n_ta
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af='CANTP_MIXED29BIT'),
                                                             meta_data=[n_sa, n_ta, n_ae]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].SduDataPtr[0] == n_ae
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[1] == n_ta


class TestSWS00335:
    """
    When calling CanIf_Transmit() for an SF, FF, or CF of a generic connection (N-PDU with MetaData), the CanTp module
    shall provide the stored addressing information via MetaData of the N-PDU. The addressing information in the
    MetaData depends on the addressing format:
    - Normal, Extended, Mixed 11 bit: none
    - Normal fixed, Mixed 29 bit: N_SA, N_TA.
    """

    @pytest.mark.parametrize('af', ['CANTP_STANDARD', 'CANTP_EXTENDED', 'CANTP_MIXED'])
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_non_segmented_message_for_addressing_formats_without_meta_data(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('data_size', single_frame_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_non_segmented_message_for_addressing_formats_with_meta_data(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args[0][1].MetaDataPtr[1] == n_ta

    @pytest.mark.parametrize('af', ['CANTP_STANDARD', 'CANTP_EXTENDED', 'CANTP_MIXED'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_segmented_message_for_addressing_formats_without_meta_data(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr == handle.ffi.NULL
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af=af),
                                                             meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr == handle.ffi.NULL

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_segmented_message_for_addressing_formats_with_meta_data(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[0][0][1].MetaDataPtr[1] == n_ta
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af=af),
                                                             meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[0] == n_sa
        assert handle.can_if_transmit.call_args_list[1][0][1].MetaDataPtr[1] == n_ta


class TestSWS00336:
    """
    When CanTp_RxIndication is called for an FC on a generic connection (N-PDU with MetaData), the CanTp module shall
    check the addressing information contained in the MetaData against the stored values.
    """

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_meta_data_pointer(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af=af), meta_data=None))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_n_sa_value(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af=af),
                                                             meta_data=[n_sa + 1, n_ta]))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))

    @pytest.mark.parametrize('af', ['CANTP_NORMALFIXED', 'CANTP_MIXED29BIT'])
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_sa', custom_n_sa)
    @pytest.mark.parametrize('n_ta', custom_n_ta)
    def test_invalid_n_ta_value(self, af, data_size, n_sa, n_ta):
        handle = CanTpTest(DefaultSender(af=af))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size, meta_data=[n_sa, n_ta]))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(handle.get_receiver_flow_control(af=af),
                                                             meta_data=[n_sa, n_ta + 1]))
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_COM'))


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
        assert_rx_session_aborted(handle)

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
        assert_rx_session_aborted(handle)


class TestSWS00341:
    """
    If the N_Br timer expires and the available buffer size is still not big enough, the CanTp module shall send a new
    FC(WAIT) to suspend the N- SDU reception and reload the N_Br timer.
    """

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_br', n_br_timeouts)
    def test_flow_status_wait(self, af, data_size, n_br):
        config = DefaultReceiver(af=af, n_br=n_br, bs=0, wft_max=1)
        handle = CanTpTest(config, rx_buffer_size=data_size - 1)
        ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        for _ in range(int(n_br / config.main_period)):
            handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0 if af in ('CANTP_STANDARD',
                                                                             'CANTP_NORMALFIXED') else 1] & 0x0F == 1

    @pytest.mark.parametrize('af', addressing_formats)
    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_br', n_br_timeouts)
    def test_flow_status_continue_to_send(self, af, data_size, n_br):
        config = DefaultReceiver(af=af, n_br=n_br, bs=0, wft_max=1)
        handle = CanTpTest(config, rx_buffer_size=data_size - 1)
        ff, _ = handle.get_receiver_multi_frame((dummy_byte,) * data_size, af=af)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()
        handle.available_rx_buffer = data_size
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_args[0][1].SduDataPtr[0 if af in ('CANTP_STANDARD',
                                                                             'CANTP_NORMALFIXED') else 1] & 0x0F == 0


@pytest.mark.parametrize('status', ['BUFREQ_OK', 'BUFREQ_E_OVFL'])
def test_sws_00342(status):
    """
    CanTp shall terminate the current reception connection when CanIf_Transmit() returns E_NOT_OK when transmitting an
    FC.
    """

    handle = CanTpTest(DefaultReceiver())
    handle.pdu_r_can_tp_start_of_reception.return_value = getattr(handle.lib, status)
    handle.can_if_transmit.return_value = handle.define('E_NOT_OK')
    ff, cfs = handle.get_receiver_multi_frame((0xFF,) * 80, bs=0)
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_called_once()
    assert_rx_session_aborted(handle)


class TestSWS00343:
    """
    CanTp shall terminate the current transmission connection when CanIf_Transmit() returns E_NOT_OK when transmitting
    an SF, FF, of CF.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, data_size):
        handle = CanTpTest(DefaultSender())
        handle.can_if_transmit.return_value = handle.define('E_NOT_OK')
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        assert_tx_session_aborted(handle)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, data_size):
        handle = CanTpTest(DefaultSender())
        handle.can_if_transmit.return_value = handle.define('E_NOT_OK')
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        assert_tx_session_aborted(handle)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_consecutive_frame(self, data_size):
        handle = CanTpTest(DefaultSender())
        fc = handle.get_receiver_flow_control()
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * data_size))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.can_if_transmit.return_value = handle.define('E_NOT_OK')
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2
        assert_tx_session_aborted(handle)


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
        assert_rx_session_aborted(handle)

    @pytest.mark.parametrize('af', addressing_formats)
    def test_invalid_first_frame(self, af):
        handle = CanTpTest(DefaultReceiver(af=af, padding=0xAA))
        ff, _ = handle.get_receiver_multi_frame(payload=(dummy_byte,) * (handle.get_payload_size(af, 'FF') - 1), af=af)
        ff_pdu = handle.get_pdu_info(ff)
        assert ff_pdu.SduLength != 8
        handle.lib.CanTp_RxIndication(0, ff_pdu)
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
        assert_rx_session_aborted(handle)

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
        assert_rx_session_aborted(handle)


class TestSWS00348:
    """
    If frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD frames) are used for a Tx N-SDU and if
    CanTpTxPaddingActivation is equal to CANTP_ON, CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU
    or last CF Tx N-PDU that belongs to that Tx N-SDU with the length of eight bytes(i.e. PduInfoPtr.SduLength = 8).
    Unused bytes in N-PDU shall be updated with CANTP_PADDING_BYTE (see ECUC_CanTp_00298).
    """

    @pytest.mark.parametrize('af', addressing_formats)
    def test_single_frame(self, af):
        handle = CanTpTest(DefaultSender(af=af, padding=0xAA))
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(payload=(dummy_byte,) * 1))
        handle.lib.CanTp_MainFunction()
        for i in range(1 + 8 - handle.get_payload_size(af, 'SF'), 8):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[i] == 0xAA

    @pytest.mark.parametrize('af', addressing_formats)
    def test_last_consecutive_frame(self, af):
        handle = CanTpTest(DefaultSender(af=af, padding=0xAA))
        tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
        fc = handle.get_receiver_flow_control(af=af, padding=0xAA)
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
        handle.lib.CanTp_MainFunction()
        for i in range(1 + 8 - handle.get_payload_size(af, 'FF'), 8):
            assert handle.can_if_transmit.call_args[0][1].SduDataPtr[i] == 0xAA


@pytest.mark.parametrize('af', addressing_formats)
def test_sws_00349(af):
    """
    If CanTpTxPaddingActivation is equal to CANTP_ON for a Tx N-SDU, and if a FC N-PDU is received for that Tx N-SDU on
    a ongoing transmission, by means of CanTp_RxIndication() call, and the length of this FC is smaller than eight bytes
    (i.e. PduInfoPtr.SduLength <8) the CanTp module shall abort the transmission session by calling
    PduR_CanTpTxConfirmation() with the result E_NOT_OK. The runtime error code CANTP_E_PADDING shall be reported to the
    Default Error Tracer.
    """
    handle = CanTpTest(DefaultSender(af=af, padding=0xAA))
    tx_data = (dummy_byte,) * (handle.get_payload_size(af, 'SF') + 1)
    fc = handle.get_receiver_flow_control(af=af)
    handle.lib.CanTp_Transmit(0, handle.get_pdu_info(tx_data))
    handle.lib.CanTp_MainFunction()
    handle.lib.CanTp_TxConfirmation(0, handle.define('E_OK'))
    handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(fc))
    handle.lib.CanTp_MainFunction()
    handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, handle.define('E_NOT_OK'))
    handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, handle.define('CANTP_E_PADDING'))
    assert_tx_session_aborted(handle)


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
    assert_rx_session_aborted(handle)


class TestSWS00355:
    """
    CanTp shall abort the corresponding session, when CanTp_TxConfirmation() is called with the result E_NOT_OK.
    """

    def test_sender_side(self):
        handle = CanTpTest(DefaultSender())
        handle.lib.CanTp_Transmit(0, handle.get_pdu_info((dummy_byte,) * 8))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_NOT_OK'))
        handle.lib.CanTp_MainFunction()
        assert_tx_session_aborted(handle)

    def test_receiver_side(self):
        handle = CanTpTest(DefaultReceiver())
        ff, cfs = handle.get_receiver_multi_frame((0xFF,) * 8)
        handle.lib.CanTp_RxIndication(0, handle.get_pdu_info(ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(0, handle.define('E_NOT_OK'))
        assert_rx_session_aborted(handle)
