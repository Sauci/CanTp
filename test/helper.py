from pycantp import *


class Helper:
    dummy_byte = 0xDE

    @staticmethod
    def create_single_rx_sdu_config(handle,
                                    pdu_id=0,
                                    n_ar=1000,
                                    n_br=1000,
                                    n_cr=1000,
                                    block_size=1,
                                    af='standard',
                                    main_function_period=1,
                                    channel_mode='half duplex'):
        configurator = CanTpConfigurator(handle, main_function_period=main_function_period)
        channel = configurator.add_channel(mode=channel_mode)
        configurator.add_rx_sdu(channel,
                                identifier=pdu_id,
                                addressing_format=af,
                                ar_timeout=n_ar,
                                br_timeout=n_br,
                                cr_timeout=n_cr,
                                block_size=block_size,
                                network_source_address=handle.ffi.NULL,
                                network_target_address=handle.ffi.NULL,
                                network_address_extension=handle.ffi.NULL)
        return configurator

    @staticmethod
    def create_single_tx_sdu_config(handle,
                                    pdu_id=0,
                                    n_as=1000,
                                    n_bs=1000,
                                    n_cs=0,
                                    n_ar=1000,
                                    n_br=0,
                                    n_cr=1000,
                                    af='standard',
                                    main_function_period=1,
                                    padding_byte=None,
                                    channel_mode='half duplex'):
        configurator = CanTpConfigurator(handle,
                                         main_function_period=main_function_period,
                                         padding_byte=padding_byte if padding_byte is not None else 0xDD)
        channel = configurator.add_channel(mode=channel_mode)
        if channel_mode == 'full duplex':
            configurator.add_rx_sdu(channel,
                                    identifier=pdu_id,
                                    ar_timeout=n_ar,
                                    br_timeout=n_br,
                                    cr_timeout=n_cr,
                                    addressing_format=af,
                                    enable_padding=padding_byte is not None,
                                    network_source_address=handle.ffi.NULL,
                                    network_target_address=handle.ffi.NULL,
                                    network_address_extension=handle.ffi.NULL)
        configurator.add_tx_sdu(channel,
                                identifier=pdu_id,
                                as_timeout=n_as,
                                bs_timeout=n_bs,
                                cs_timeout=n_cs,
                                addressing_format=af,
                                enable_padding=padding_byte is not None,
                                network_source_address=handle.ffi.NULL,
                                network_target_address=handle.ffi.NULL,
                                network_address_extension=handle.ffi.NULL)
        return configurator

    @staticmethod
    def create_pdu_info(handle, payload, meta_data=None):
        if isinstance(payload, str):
            payload = [ord(c) for c in payload]
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
    def create_rx_sf_can_frame(payload=(dummy_byte,), ai=None, padding=None):
        if ai is None:
            ai = []
        else:
            ai = [ai]
        payload = list(payload)
        pci = [(0 << 4) | (len(payload) & 0x0F)]
        tmp_return = ai + pci + payload
        if padding is not None:
            [tmp_return.append(padding) for _ in range(8 - len(tmp_return))]
        return tmp_return

    @staticmethod
    def create_rx_ff_can_frame(payload=(dummy_byte,), ai=None):
        if ai is None:
            ai = []
        else:
            ai = [ai]
        payload = list(payload)
        pci = [(1 << 4) | ((len(payload) & 0xF00) >> 8), len(payload) & 0x0FF]
        return ai + pci + payload[0:8 - (len(ai) + len(pci))]

    @staticmethod
    def create_rx_cf_can_frame(payload=(dummy_byte,), ai=None, sn=1, padding=None):
        if ai is None:
            ai = []
        else:
            ai = [ai]
        payload = list(payload)
        pci = [(2 << 4) | (sn & 0x0F)]
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
        return ai + pci + (([padding] * (4 if ai else 5)) if padding is not None else [])
