from math import ceil
from unit_test import *


class TestSWS00031:
    """
    If development error detection for the CanTp module is enabled the CanTp module shall raise an error (CANTP_E_UNINIT
    ) when the PDU Router or CAN Interface tries to use any function (except CanTp_GetVersionInfo) before the function
    CanTp_Init has been called.
    """

    def test_shutdown(self, handle):
        handle.lib.CanTp_Shutdown()
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_transmit(self, handle):
        handle.can_tp_transmit(0, handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_cancel_transmit(self, handle):
        handle.lib.CanTp_CancelTransmit(0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_cancel_receive(self, handle):
        handle.lib.CanTp_CancelReceive(0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_change_parameter(self, handle):
        handle.lib.CanTp_ChangeParameter(0, 0, 0)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_read_parameter(self, handle):
        handle.lib.CanTp_ReadParameter(0, 0, handle.ffi.NULL)
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)

    def test_main_function(self, handle):
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_UNINIT)


class TestSWS00057:
    """
    If unexpected frames are received, the CanTp module shall behave according to the table below. This table specifies
    the N-PDU handling considering the current CanTp internal status (CanTp status).

    CanTp     | Reception of
    ----------+--------------------+--------------------+--------------------+--------------------+--------------------+
    status    | SF N-PDU           | FF N-PDU           | CF N-PDU           | FC N-PDU           | Unknow n N-PDU
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
    pdu_id = 0
    rx_fc = Helper.create_rx_fc_can_frame(padding=0xFF, bs=5, st_min=0)
    rx_data = 'expected received payload......'
    tx_data = 'expected transmitted payload...'

    def perform_segmented_transmit_sequence(self, handle, channel_mode, can_frame):
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          channel_mode=channel_mode,
                                                          n_cs=0,
                                                          main_function_period=1)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(self.pdu_id, Helper.create_pdu_info(handle, list(ord(c) for c in self.tx_data)))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, self.rx_fc))
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
        for _ in range(ceil((len(self.tx_data) - 6) / 7)):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, E_OK)

    def perform_segmented_receive_sequence(self, handle, channel_mode, can_frame):
        configurator = Helper.create_single_rx_sdu_config(handle,
                                                          channel_mode=channel_mode,
                                                          main_function_period=1)
        handle.lib.CanTp_Init(configurator.config)
        ff_frame = Helper.create_rx_ff_can_frame(list(ord(c) for c in self.rx_data))
        a = ''.join(chr(c) for c in ff_frame)
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, ff_frame))
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
        for cf_index in range(ceil((len(self.rx_data) - 6) / 7)):
            cf_frame = Helper.create_rx_cf_can_frame(list(ord(c) for c in self.rx_data[6 + (cf_index * 7):]))
            handle.lib.CanTp_MainFunction()
            a = ''.join(chr(c) for c in cf_frame)
            handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, cf_frame))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, E_OK)

    @pytest.mark.parametrize('can_frame', [
        pytest.param(Helper.create_rx_sf_can_frame(), id='single frame'),
        pytest.param(Helper.create_rx_ff_can_frame(), id='first frame')])
    def test_unexpected_sf_ff_reception_while_segmented_transmit_is_in_progress_half_duplex(self,
                                                                                            handle,
                                                                                            can_frame):
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          channel_mode='half duplex',
                                                          n_cs=0,
                                                          main_function_period=1)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(self.pdu_id, Helper.create_pdu_info(handle, list(ord(c) for c in self.tx_data)))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, self.rx_fc))
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
        for _ in range(ceil((len(self.tx_data) - 6) / 7)):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, E_OK)
        handle.pdu_r_can_tp_rx_indication.assert_not_called()
        handle.det_report_runtime_error.assert_not_called()

    @pytest.mark.parametrize('can_frame, instance_id', [
        pytest.param(Helper.create_rx_sf_can_frame(), CANTP_I_FULL_DUPLEX_RX_SF, id='single frame'),
        pytest.param(Helper.create_rx_ff_can_frame(), CANTP_I_FULL_DUPLEX_RX_FF, id='first frame')])
    def test_unexpected_sf_ff_reception_while_segmented_transmit_is_in_progress_full_duplex(self,
                                                                                            handle,
                                                                                            can_frame,
                                                                                            instance_id):
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          channel_mode='full duplex',
                                                          main_function_period=1)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(self.pdu_id, Helper.create_pdu_info(handle, list(ord(c) for c in self.tx_data)))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, self.rx_fc))
        # in full-duplex mode, the first SF/FF might be expected.
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
        for _ in range(ceil((len(self.tx_data) - 6) / 7)):
            handle.lib.CanTp_MainFunction()
            handle.lib.CanTp_TxConfirmation(self.pdu_id, E_OK)
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, E_OK)
        handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, E_NOT_OK)
        handle.det_report_runtime_error.assert_called_once_with(ANY, instance_id, ANY, CANTP_E_UNEXP_PDU)

    # @pytest.mark.xfail(reason='not implemented...')
    # @pytest.mark.parametrize('can_frame', [
    #     pytest.param(Helper.create_rx_sf_can_frame(), id='single frame'),
    #     pytest.param(Helper.create_rx_ff_can_frame(), id='first frame')])
    # def test_unexpected_sf_ff_reception_while_segmented_receive_is_in_progress_half_duplex(self,
    #                                                                                        handle,
    #                                                                                        can_frame):
    #     configurator = Helper.create_single_rx_sdu_config(handle,
    #                                                       channel_mode='half duplex',
    #                                                       main_function_period=1)
    #     handle.lib.CanTp_Init(configurator.config)
    #     ff_frame = Helper.create_rx_ff_can_frame(list(ord(c) for c in self.rx_data))
    #     a = ''.join(chr(c) for c in ff_frame)
    #     handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, ff_frame))
    #     handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, can_frame))
    #     for cf_index in range(ceil((len(self.rx_data) - 6) / 7)):
    #         cf_frame = Helper.create_rx_cf_can_frame(list(ord(c) for c in self.rx_data[6 + (cf_index * 7):]))
    #         handle.lib.CanTp_MainFunction()
    #         a = ''.join(chr(c) for c in cf_frame)
    #         handle.lib.CanTp_RxIndication(self.pdu_id, Helper.create_pdu_info(handle, cf_frame))
    #     handle.lib.CanTp_MainFunction()
    #     handle.pdu_r_can_tp_rx_indication.assert_called_once_with(ANY, E_OK)
    #     handle.pdu_r_can_tp_rx_indication.assert_not_called()
    #     handle.det_report_runtime_error.assert_not_called()

    @pytest.mark.parametrize('channel_mode', [pytest.param(t, id=t) for t in ('half duplex', 'full duplex')])
    @pytest.mark.parametrize('can_frame', [pytest.param(Helper.create_rx_cf_can_frame(), id='consecutive frame'),
                                           pytest.param(Helper.create_rx_fc_can_frame(), id='flow control frame')])
    def test_unexpected_cf_fc_reception_while_segmented_transmit_is_in_progress(self,
                                                                                handle,
                                                                                channel_mode,
                                                                                can_frame):
        self.perform_segmented_transmit_sequence(handle, channel_mode, can_frame)
        handle.pdu_r_can_tp_copy_rx_data.assert_not_called()


class TestSWS00079:
    """
    When receiving an SF or an FF N-PDU, the CanTp module shall notify the upper layer (PDU Router) about this reception
    using the PduR_CanTpStartOfReception function.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_br=0)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_sf_can_frame()
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_br=0)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_ff_can_frame()
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()


class TestSWS00166:
    """
    At the reception of a FF or last CF of a block, the CanTp module shall start a time-out N_Br before calling
    PduR_CanTpStartOfReception or PduR_CanTpCopyRxData.
    """

    @pytest.mark.parametrize('n_br', n_br_timeouts)
    def test_first_frame(self, handle, n_br):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_br=n_br)
        ff = Helper.create_rx_ff_can_frame()
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
        for _ in range(int(n_br / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.pdu_r_can_tp_start_of_reception.assert_called_once()

    @pytest.mark.parametrize('n_br', n_br_timeouts)
    def test_last_consecutive_frame(self, handle, n_br):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_br=n_br)
        ff = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * 10)
        cf = Helper.create_rx_cf_can_frame(sn=1)
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
        cnt = 0
        for _ in range(int(n_br / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, cf))
        for cnt in range(int(n_br / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        assert handle.pdu_r_can_tp_copy_rx_data.call_count == 2 * (cnt + 1)  # see SWS00222


def test_sws_00176(handle):
    """
    The function CanTp_Transmit() shall be asynchronous.
    """
    configurator = Helper.create_single_tx_sdu_config(handle)
    handle.lib.CanTp_Init(configurator.config)
    handle.can_tp_transmit(0, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 10))
    handle.can_if_transmit.assert_not_called()
    handle.lib.CanTp_MainFunction()
    handle.can_if_transmit.assert_called_once()


@pytest.mark.parametrize('n_br', n_br_timeouts)
def test_sws_00222(handle, n_br):
    """
    While the timer N_Br is active, the CanTp module shall call the service PduR_CanTpCopyRxData() with a data length 0
    (zero) and NULL_PTR as data buffer during each processing of the MainFunction.
    """

    pdu_id = 0
    configurator = Helper.create_single_rx_sdu_config(handle, n_br=n_br)
    ff = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * 10)
    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
    cnt = 0
    for cnt in range(int(n_br / configurator.config.mainFunctionPeriod)):
        handle.lib.CanTp_MainFunction()
        assert handle.pdu_r_can_tp_copy_rx_data.call_args[0][1].SduLength == 0
        assert handle.pdu_r_can_tp_copy_rx_data.call_args[0][1].SduDataPtr == handle.ffi.NULL
    assert handle.pdu_r_can_tp_copy_rx_data.call_count == cnt + 1


def test_sws_00223(handle):
    """
    The CanTp module shall send a maximum of WFTmax consecutive FC(WAIT) N-PDU. If this number is reached, the CanTp
    module shall abort the reception of this N-SDU (the receiver did not send any FC N-PDU, so the N_Bs timer expires on
    the sender side and then the transmission is aborted) and a receiving indication with E_NOT_OK occurs.
    """
    pytest.mark.xfail()


def test_sws_00224(handle):
    """
    When the Rx buffer is large enough for the next block (directly after the First Frame or the last Consecutive Frame
    of a block, or after repeated calls to PduR_CanTpCopyRxData() according to SWS_CanTp_00222), the CanTp module shall
    send a Flow Control N-PDU with ClearToSend status (FC(CTS)) and shall then expect the reception of Consecutive Frame
    N-PDUs.
    """
    pytest.mark.xfail()


class TestSWS00229:
    """
    If the task was aborted due to As, Bs, Cs, Ar, Br, Cr timeout, the CanTp module shall raise the DET error
    CANTP_E_RX_COM (in case of a reception operation) or CANTP_E_TX_COM (in case of a transmission operation). If the
    task was aborted due to any other protocol error, the CanTp module shall raise the runtime error code CANTP_E_COM to
    the Default Error Tracer.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes + multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('n_cs', n_cs_timeouts)
    def test_as_timeout(self, handle, data_size, n_as, n_bs, n_cs):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle, n_as=n_as, n_bs=n_bs, n_cs=n_cs)
        pdu_info = Helper.create_pdu_info(handle, [Helper.dummy_byte] * data_size)

        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, pdu_info)
        for _ in range(int(n_as / configurator.config.mainFunctionPeriod)):
            handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_OK
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, CANTP_I_N_AS, ANY, CANTP_E_TX_COM)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('n_cs', n_cs_timeouts)
    def test_bs_timeout(self, handle, data_size, n_as, n_bs, n_cs):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle, n_as=n_as, n_bs=n_bs, n_cs=n_cs)
        pdu_info = Helper.create_pdu_info(handle, [Helper.dummy_byte] * data_size)

        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, pdu_info)
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(int(n_bs / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, CANTP_I_N_BS, ANY, CANTP_E_TX_COM)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('n_cs', n_cs_timeouts)
    def test_cs_timeout(self, handle, data_size, n_as, n_bs, n_cs):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle, n_as=n_as, n_bs=n_bs, n_cs=n_cs)
        pdu_info = Helper.create_pdu_info(handle, [Helper.dummy_byte] * data_size)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=1, st_min=0)
        handle.lib.CanTp_Init(configurator.config)

        handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_OK
        handle.can_tp_transmit(pdu_id, pdu_info)
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        # TODO: add test for busy and overflow return values.
        handle.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_E_BUSY
        for _ in range(int(n_cs / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, CANTP_I_N_CS, ANY, CANTP_E_TX_COM)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ar', n_ar_timeouts)
    @pytest.mark.parametrize('n_cr', n_cr_timeouts)
    def test_ar_timeout(self, handle, data_size, n_ar, n_cr):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_ar=n_ar, n_br=0, n_cr=n_cr)
        ff = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * data_size)
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
        for _ in range(int(n_ar / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, CANTP_I_N_AR, ANY, CANTP_E_RX_COM)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ar', n_ar_timeouts)
    @pytest.mark.parametrize('n_br', n_br_timeouts)
    @pytest.mark.parametrize('n_cr', n_cr_timeouts)
    def test_br_timeout(self, handle, data_size, n_ar, n_br, n_cr):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_ar=n_ar, n_br=n_br, n_cr=n_cr)
        ff = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * data_size)
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
        for _ in range(int(n_br / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_ar', n_ar_timeouts)
    @pytest.mark.parametrize('n_cr', n_cr_timeouts)
    def test_cr_timeout(self, handle, data_size, n_ar, n_cr):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, n_ar=n_ar, n_br=0, n_cr=n_cr)
        ff = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * data_size)
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, ff))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(int(n_cr / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.det_report_error.assert_called_once_with(ANY, CANTP_I_N_CR, ANY, CANTP_E_RX_COM)


class TestSWS00254:
    """
    If development error detection is enabled the function CanTp_CancelTransmit shall check the validity of TxPduId
    parameter. If the parameter value is invalid, the CanTp_CancelTransmit function shall raise the development error
    CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    If the parameter value indicates a cancel transmission request for an N-SDU that it is not on transmission process
    the CanTp module shall report a runtime error code CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the
    service shall return E_NOT_OK.
    """

    def test_invalid_tx_pdu_id(self, handle):
        configurator = Helper.create_single_tx_sdu_config(handle, pdu_id=0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_CancelTransmit(1) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)

    def test_no_tx_operation_in_progress(self, handle):
        configurator = Helper.create_single_tx_sdu_config(handle, pdu_id=0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_CancelTransmit(0) == E_NOT_OK
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_OPER_NOT_SUPPORTED)


def test_sws_00255(handle):
    """
    If the CanTp_CancelTransmit service has been successfully executed the CanTp shall call the PduR_CanTpTxConfirmation
    with notification result E_NOT_OK.
    """
    pdu_id = 0
    configurator = Helper.create_single_tx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte]))
    handle.lib.CanTp_CancelTransmit(pdu_id)
    handle.pdu_r_can_tp_tx_confirmation.assert_called_once_with(ANY, E_NOT_OK)


def test_sws_00256(handle):
    """
    The CanTp shall abort the transmission of the current N-SDU if the service returns E_OK.
    """
    pdu_id = 0
    configurator = Helper.create_single_tx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte]))
    assert handle.lib.CanTp_CancelTransmit(pdu_id) == E_OK


class TestSWS00260:
    """
    If development error detection is enabled the function CanTp_CancelReceive shall check the validity of RxPduId
    parameter. If the parameter value is invalid, the CanTp_CancelReceive function shall raise the development error
    CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    If the parameter value indicates a cancel reception request for an N-SDU that it is not on reception process the
    CanTp module shall report the runtime error code CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the
    service shall return E_NOT_OK.
    """

    def test_invalid_rx_pdu_id(self, handle):
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_CancelReceive(1) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)

    def test_no_rx_operation_in_progress(self, handle):
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_CancelReceive(0) == E_NOT_OK
        handle.det_report_runtime_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_OPER_NOT_SUPPORTED)


def test_sws_00261(handle):
    """
    The CanTp shall abort the reception of the current N-SDU if the service returns E_OK.
    """
    pdu_id = 0
    configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, Helper.create_rx_ff_can_frame()))
    assert handle.lib.CanTp_CancelReceive(pdu_id) == E_OK


class TestSWS00262:
    """
    The CanTp shall reject the request for receive cancellation in case of a Single Frame reception or if the CanTp is
    in the process of receiving the last Consecutive Frame of the N-SDU (i.e. the service is called after N-Cr timeout
    is started for the last Consecutive Frame). In this case the CanTp shall return E_NOT_OK.
    """

    def test_single_frame(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, Helper.create_rx_sf_can_frame()))
        assert handle.lib.CanTp_CancelReceive(pdu_id) == E_NOT_OK

    def test_last_consecutive_frame(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=1)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 8))
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        handle.lib.CanTp_MainFunction()
        assert handle.lib.CanTp_CancelReceive(pdu_id) == E_NOT_OK


def test_sws_00263(handle):
    """
    If the CanTp_CancelReceive service has been successfully executed the CanTp shall call the PduR_CanTpRxIndication
    with notification result E_NOT_OK.
    """
    pdu_id = 0
    configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, Helper.create_rx_ff_can_frame()))
    handle.lib.CanTp_CancelReceive(pdu_id)
    handle.pdu_r_can_tp_rx_indication.called_once_with(ANY, E_NOT_OK)


def test_sws_00304(handle):
    """
    If the change of a parameter is requested for an N-SDU that is on reception process the service
    CanTp_ChangeParameter immediately returns E_NOT_OK and no parameter value is changed
    """
    pdu_id = 0
    configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, Helper.create_rx_ff_can_frame()))
    assert handle.lib.CanTp_ChangeParameter(pdu_id, handle.lib.TP_STMIN, 0) == E_NOT_OK
    handle.det_report_error.assert_not_called()


class TestSWS00305:
    """
    If development error detection is enabled, the function CanTp_ChangeParameter shall check the validity of function
    parameters (Identifier, Parameter and requested value). If any of the parameter value is invalid, the
    CanTp_ChangeParameter function shall raise the development error CANTP_E_PARAM_ID and return E_NOT_OK
    """

    def test_invalid_pdu_id(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_ChangeParameter(1, handle.lib.TP_STMIN, 0) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)

    def test_invalid_parameter(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_ChangeParameter(pdu_id, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, 0) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)

    @pytest.mark.parametrize('parameter, value', [pytest.param('TP_STMIN', 0xFF + 1, id='STmin out of range'),
                                                  pytest.param('TP_BS', 0xFF + 1, id='BS out of range')])
    def test_invalid_value(self, handle, parameter, value):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_ChangeParameter(pdu_id, getattr(handle.lib, parameter), value) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)


def test_sws_00321(handle):
    """
    If DET is enabled the function CanTp_Transmit shall rise CANTP_E_PARAM_POINTER error if the argument PduInfoPtr is a
    NULL pointer and return without any action.
    """
    pdu_id = 0
    configurator = Helper.create_single_tx_sdu_config(handle)
    handle.lib.CanTp_Init(configurator.config)
    handle.can_tp_transmit(pdu_id, handle.ffi.NULL)
    handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_POINTER)


def test_sws_00322(handle):
    """
    If DET is enabled the function CanTp_RxIndication shall rise CANTP_E_PARAM_POINTER error if the argument PduInfoPtr
    is a NULL pointer and return without any action.
    """
    pdu_id = 0
    configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
    handle.lib.CanTp_Init(configurator.config)
    handle.lib.CanTp_RxIndication(pdu_id, handle.ffi.NULL)
    handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_POINTER)


class TestSWS00324:
    """
    If development error detection is enabled the function CanTp_ReadParameter shall check the validity of function
    parameters (Id and Parameter). If any of the parameter value is invalid, the CanTp_ReadParameter function shall
    raise the development error CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    """

    def test_invalid_pdu_id(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        parameter = handle.ffi.new('uint16 *', 0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_ReadParameter(pdu_id + 1, handle.lib.TP_STMIN, parameter) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)

    def test_invalid_parameter(self, handle):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle, pdu_id=pdu_id)
        parameter = handle.ffi.new('uint16 *', 0)
        handle.lib.CanTp_Init(configurator.config)
        assert handle.lib.CanTp_ReadParameter(pdu_id, handle.lib.TP_STMIN + handle.lib.TP_BS + 1, parameter) == E_NOT_OK
        handle.det_report_error.assert_called_once_with(ANY, ANY, ANY, CANTP_E_PARAM_ID)


class TestSWS00329:
    """
    CanTp shall provide the content of the FF/SF to PduR using the parameter TpSduInfoPtr of
    PduR_CanTpStartOfReception().
    """

    def test_single_frame(self, handle):
        pytest.xfail()

    def test_first_frame(self, handle):
        pytest.xfail()


class TestSeparationTimeMinimum:
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

    @pytest.mark.parametrize('st_min', [pytest.param(v, id='STmin = {} [ms]'.format(v)) for v in range(0x7F + 0x01)])
    def test_st_min_range_h00_h7f(self, handle, st_min):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          pdu_id=pdu_id,
                                                          n_bs=0,
                                                          main_function_period=1)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=0, st_min=st_min)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 100))
        handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(st_min * 1000):
            handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2

    @pytest.mark.parametrize('st_min', [pytest.param(v, id='STmin = rsvd (0x{:02X})'.format(v)) for v in
                                        (i + 0x80 for i in range(0xF0 - 0x80 + 0x01))])
    def test_st_min_range_h80_hf0(self, handle, st_min):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          pdu_id=pdu_id,
                                                          main_function_period=1)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=0, st_min=st_min)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 100))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(0x7F * 1000):
            handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2

    @pytest.mark.parametrize('st_min', [pytest.param(0xF1 + v, id='STmin = {} [us]'.format(100 + v * 100)) for v in
                                        range(9)])
    def test_st_min_range_hf1_hf9(self, handle, st_min):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          pdu_id=pdu_id,
                                                          main_function_period=1)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=0, st_min=st_min)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 100))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range((st_min & 0x0F) * 100):
            handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2

    @pytest.mark.parametrize('st_min', [pytest.param(v, id='STmin = rsvd (0x{:02X})'.format(v)) for v in
                                        (i + 0xFA for i in range(0xFF - 0xFA + 0x01))])
    def test_st_min_range_hfa_hff(self, handle, st_min):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle,
                                                          pdu_id=pdu_id,
                                                          main_function_period=1)
        fc_frame = Helper.create_rx_fc_can_frame(padding=0xFF, bs=0, st_min=st_min)
        handle.lib.CanTp_Init(configurator.config)
        handle.can_tp_transmit(pdu_id, Helper.create_pdu_info(handle, [Helper.dummy_byte] * 100))
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(0x7F * 1000):
            handle.lib.CanTp_MainFunction()
        handle.can_if_transmit.assert_called_once()
        handle.lib.CanTp_MainFunction()
        assert handle.can_if_transmit.call_count == 2
