import pytest
from math import ceil
from pycantp import *

try:
    from unittest.mock import ANY
except ImportError:
    from mock import ANY

addressing_formats = [
    pytest.param(af, id='addressing format = {}'.format(af)) for af in ('standard',
                                                                        #'fixed',
                                                                        #'extended',
                                                                        #'mixed 11 bits',
                                                                        #'mixed 29 bits'
                                                                        )]

single_frame_sizes = [pytest.param(fs, id='SF_DL = {}'.format(fs)) for fs in (1, 2, 6)]
multi_frames_sizes = [pytest.param(fs, id='FF_DL = {}'.format(fs)) for fs in (8, 4095)]

n_xs_timeouts = [10, 100, 0xFF]

n_as_timeouts = [pytest.param(t, id='N_As = {}ms'.format(t)) for t in n_xs_timeouts]
n_bs_timeouts = [pytest.param(t, id='N_Bs = {}ms'.format(t)) for t in n_xs_timeouts]
n_cs_timeouts = [pytest.param(t, id='N_Cs = {}ms'.format(t)) for t in n_xs_timeouts]


class Helper:
    dummy_byte = 0xDE

    @staticmethod
    def create_single_rx_sdu_config(handle,
                                    n_as=1000,
                                    n_bs=1000,
                                    n_cs=1000,
                                    af='standard',
                                    n_sa=None,
                                    n_ta=None,
                                    n_ae=None):
        configurator = CanTpConfigurator(handle, main_function_period=1)
        channel = configurator.add_channel()
        if af == 'extended':
            assert n_sa is not None
            assert n_ta is not None
            assert n_ae is None
            sa = handle.ffi.new('CanTp_NSaType *')
            ta = handle.ffi.new('CanTp_NTaType *')
            ae = handle.ffi.NULL
            sa.nSa = n_sa
            ta.nTa = n_ta
        elif af in ('mixed 11 bits', 'mixed 29 bits'):
            assert n_sa is None
            assert n_ta is None
            assert n_ae is not None
            sa = handle.ffi.NULL
            ta = handle.ffi.NULL
            ae = handle.ffi.new('CanTp_NAeType *')
            ae.nAe = n_ae
        else:
            assert n_sa is None
            assert n_ta is None
            assert n_ae is None
            sa = handle.ffi.NULL
            ta = handle.ffi.NULL
            ae = handle.ffi.NULL
        configurator.add_rx_sdu(channel,
                                ar_timeout=n_as,
                                br_timeout=n_bs,
                                cr_timeout=n_cs,
                                addressing_format=af,
                                network_source_address=sa,
                                network_target_address=ta,
                                network_address_extension=ae)
        return configurator

    @staticmethod
    def create_single_tx_sdu_config(handle,
                                    n_as=1000,
                                    n_bs=1000,
                                    n_cs=1000,
                                    af='standard',
                                    n_sa=None,
                                    n_ta=None,
                                    n_ae=None):
        configurator = CanTpConfigurator(handle, main_function_period=1)
        channel = configurator.add_channel()
        if af == 'extended':
            assert n_sa is not None
            assert n_ta is not None
            assert n_ae is None
            sa = handle.ffi.new('CanTp_NSaType *')
            ta = handle.ffi.new('CanTp_NTaType *')
            ae = handle.ffi.NULL
            sa.nSa = n_sa
            ta.nTa = n_ta
        elif af in ('mixed 11 bits', 'mixed 29 bits'):
            assert n_sa is None
            assert n_ta is None
            assert n_ae is not None
            sa = handle.ffi.NULL
            ta = handle.ffi.NULL
            ae = handle.ffi.new('CanTp_NAeType *')
            ae.nAe = n_ae
        else:
            assert n_sa is None
            assert n_ta is None
            assert n_ae is None
            sa = handle.ffi.NULL
            ta = handle.ffi.NULL
            ae = handle.ffi.NULL
        configurator.add_tx_sdu(channel,
                                as_timeout=n_as,
                                bs_timeout=n_bs,
                                cs_timeout=n_cs,
                                addressing_format=af,
                                network_source_address=sa,
                                network_target_address=ta,
                                network_address_extension=ae)
        return configurator

    @staticmethod
    def create_pdu_info(handle, payload, meta_data=None):
        data = handle.ffi.new('uint8 []', list(payload))
        pdu_info = handle.ffi.new('PduInfoType *')
        pdu_info.SduDataPtr = data
        if (payload[0] & 0xF0) >> 4 == 1:
            pdu_info.SduLength = ((payload[0] & 0x0F) << 8) | payload[1]
        else:
            pdu_info.SduLength = len(data)
        if meta_data:
            raise NotImplementedError
        else:
            pdu_info.MetaDataPtr = handle.ffi.NULL
        return pdu_info

    @staticmethod
    def create_rx_sf_can_frame(payload=[dummy_byte], ai=None, padding=None):

        if ai is None:
            ai = []
        else:
            ai = [ai]
        pci = [(0 << 4) | (len(payload) & 0x0F)]
        tmp_return = ai + pci + payload
        if padding is not None:
            tmp_return += [padding * (8 - len(tmp_return))]
        return tmp_return

    @staticmethod
    def create_rx_ff_can_frame(payload=[dummy_byte], ai=None):

        if ai is None:
            ai = []
        else:
            ai = [ai]
        pci = [(1 << 4) | ((len(payload) & 0xF00) >> 8), len(payload) & 0x0FF]
        return ai + pci + payload[0:8 - (len(ai) + len(pci))]

    @staticmethod
    def create_rx_fc_can_frame(flow_status='continue to send', ai=None, bs=1, st_min=0, padding=None):
        """
        returns an array of integers representing the CAN TP flow control frame with the specified parameters.

        :param flow_status: flow status value (one of 'continue to send', 'wait', 'overflow')
        :type flow_status: str
        :param ai: address information byte (N_Ta for extended addressing, N_Ae for mixed addressing, None otherwise)
        :type ai: int/None
        :param bs: block size (BS)
        :type bs: int
        :param st_min: minimum separation time (STmin)
        :type st_min: int
        :param padding: padding value (0x00..0xFF if padding is activated, None otherwise)
        :type padding: int/None
        :return: list
        """
        if ai is None:
            ai = []
        else:
            ai = [ai]
        pci = [(3 << 4) | {'continue to send': 0,
                           'wait': 1,
                           'overflow': 2}[flow_status],
               bs,
               st_min]
        return ai + pci + ([padding] * (4 if ai else 5)) if padding is not None else []


@pytest.fixture()
def handle():
    return CanTp(recompile=True)


@pytest.fixture()
def pdu_r_copy_data_return_value(request):
    return request


class TestSWS00079:
    """
    When receiving an SF or an FF N-PDU, the CanTp module shall notify the upper layer (PDU Router) about this reception
    using the PduR_CanTpStartOfReception function.
    """

    @pytest.mark.parametrize('data_size', single_frame_sizes)
    def test_single_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_sf_can_frame()
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.mock.pdu_r_can_tp_start_of_reception.assert_called_once()

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    def test_first_frame(self, handle, data_size):
        pdu_id = 0
        configurator = Helper.create_single_rx_sdu_config(handle)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_ff_can_frame()
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.mock.pdu_r_can_tp_start_of_reception.assert_called_once()


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
        handle.lib.CanTp_Transmit(pdu_id, pdu_info)
        for _ in range(int(n_as / configurator.config.mainFunctionPeriod)):
            handle.mock.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_OK
            handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_called_once_with(ANY, CANTP_INSTANCE_ID_N_AS, ANY, CANTP_E_TX_COM)

    @pytest.mark.parametrize('data_size', multi_frames_sizes)
    @pytest.mark.parametrize('n_as', n_as_timeouts)
    @pytest.mark.parametrize('n_bs', n_bs_timeouts)
    @pytest.mark.parametrize('n_cs', n_cs_timeouts)
    def test_bs_timeout(self, handle, data_size, n_as, n_bs, n_cs):
        pdu_id = 0
        configurator = Helper.create_single_tx_sdu_config(handle, n_as=n_as, n_bs=n_bs, n_cs=n_cs)
        pdu_info = Helper.create_pdu_info(handle, [Helper.dummy_byte] * data_size)

        handle.lib.CanTp_Init(configurator.config)
        handle.lib.CanTp_Transmit(pdu_id, pdu_info)
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        for _ in range(int(n_bs / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_called_once_with(ANY, CANTP_INSTANCE_ID_N_BS, ANY, CANTP_E_TX_COM)

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

        handle.mock.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_OK
        handle.lib.CanTp_Transmit(pdu_id, pdu_info)
        handle.lib.CanTp_MainFunction()
        handle.lib.CanTp_TxConfirmation(pdu_id, E_OK)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, fc_frame))
        # TODO: add test for busy and overflow return values.
        handle.mock.pdu_r_can_tp_copy_tx_data.return_value = handle.lib.BUFREQ_E_BUSY
        for _ in range(int(n_cs / configurator.config.mainFunctionPeriod)):
            handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_not_called()
        handle.lib.CanTp_MainFunction()
        handle.mock.det_report_error.assert_called_once_with(ANY, CANTP_INSTANCE_ID_N_CS, ANY, CANTP_E_TX_COM)

    def test_ar_timeout(self):
        pytest.xfail('not implemented')

    def test_br_timeout(self):
        pytest.xfail('not implemented')

    def test_cr_timeout(self):
        pytest.xfail('not implemented')


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
        configurator = Helper.create_single_rx_sdu_config(handle)
        handle.lib.CanTp_Init(configurator.config)
        can_frame = Helper.create_rx_ff_can_frame(payload=[Helper.dummy_byte] * data_size)
        handle.lib.CanTp_RxIndication(pdu_id, Helper.create_pdu_info(handle, can_frame))
        handle.mock.pdu_r_can_tp_start_of_reception.assert_called_once_with(ANY, ANY, data_size, ANY)


@pytest.mark.parametrize('af', addressing_formats)
@pytest.mark.parametrize('data_size', multi_frames_sizes)
@pytest.mark.parametrize('bs', [pytest.param(1, id='BS = 1'),
                                pytest.param(10, id='BS = 10'),
                                pytest.param(15, id='BS = 15')])
def test_sequence_number(handle, af, data_size, bs):
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
    if af == 'extended':
        address_info = dict(n_sa=0x5A, n_ta=0x7A, n_ae=None)
    elif af in ('mixed 11 bits', 'mixed 29 bits'):
        address_info = dict(n_sa=None, n_ta=None, n_ae=0xA1)
    else:
        address_info = dict(n_sa=None, n_ta=None, n_ae=None)

    pdu_id = 0
    configurator = Helper.create_single_tx_sdu_config(handle, af=af, **address_info)
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
