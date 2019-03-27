class CanTpConfigurator(object):
    def __init__(self, can_tp_handle, main_function_period=1000):
        self.handle = can_tp_handle
        self.config = can_tp_handle.ffi.new('CanTp_ConfigType *')
        self.config.mainFunctionPeriod = main_function_period

    def add_channel(self, mode='half duplex'):
        """
        add a new channel to configuration.
        :param mode: the mode of the channel. this parameter can be on of 'half duplex'. 'full duplex'
        :type mode: str
        :return: self
        """
        new_channel = self.handle.ffi.new('CanTp_ChannelType *')
        new_channel.channelMode = {'full duplex': self.handle.lib.CANTP_MODE_FULL_DUPLEX,
                                   'half duplex': self.handle.lib.CANTP_MODE_HALF_DUPLEX}[mode]
        new_channel.nSdu.rx = self.handle.ffi.NULL
        new_channel.nSdu.tx = self.handle.ffi.NULL
        new_channel.nSdu.rxNSduCnt = 0
        new_channel.nSdu.txNSduCnt = 0
        if self.config.pChannel == self.handle.ffi.NULL:
            self.config.pChannel = new_channel
            self.config.maxChannelCnt += 1
        else:
            raise NotImplementedError
        return new_channel

    def add_rx_sdu(self,
                   channel,
                   identifier=0,
                   network_source_address=None,
                   network_target_address=None,
                   network_address_extension=None,
                   block_size=1,
                   ar_timeout=1000,
                   br_timeout=0,
                   cr_timeout=1000,
                   wait_for_transmission_max=0,
                   separation_time_minimum=0,
                   addressing_format='standard',
                   enable_padding=True,
                   network_sdu_type='physical',
                   network_sdu_reference=0):
        new_rx_sdu = self.handle.ffi.new('CanTp_RxNSduType *')
        if network_source_address is None:
            network_source_address = self.handle.ffi.NULL
        if network_target_address is None:
            network_target_address = self.handle.ffi.NULL
        if network_address_extension is None:
            network_address_extension = self.handle.ffi.NULL
        new_rx_sdu.nSduId = identifier
        new_rx_sdu.pNSa = network_source_address
        new_rx_sdu.pNTa = network_target_address
        new_rx_sdu.pNAe = network_address_extension
        new_rx_sdu.bs = block_size
        new_rx_sdu.nar = ar_timeout
        new_rx_sdu.nbr = br_timeout
        new_rx_sdu.ncr = cr_timeout
        new_rx_sdu.wftMax = wait_for_transmission_max
        new_rx_sdu.sTMin = separation_time_minimum
        new_rx_sdu.af = {'standard': self.handle.lib.CANTP_STANDARD,
                         'fixed': self.handle.lib.CANTP_NORMALFIXED,
                         'extended': self.handle.lib.CANTP_EXTENDED,
                         'mixed 11 bits': self.handle.lib.CANTP_MIXED,
                         'mixed 29 bits': self.handle.lib.CANTP_MIXED29BIT}[addressing_format]
        new_rx_sdu.padding = enable_padding
        new_rx_sdu.taType = {'physical': self.handle.lib.CANTP_PHYSICAL,
                             'functional': self.handle.lib.CANTP_FUNCTIONAL}[network_sdu_type]
        new_rx_sdu.rxNSduRef = network_sdu_reference
        if channel.nSdu.rx == self.handle.ffi.NULL:
            channel.nSdu.rx = new_rx_sdu
            channel.nSdu.rxNSduCnt += 1
        else:
            raise NotImplementedError
        return new_rx_sdu

    def add_tx_sdu(self,
                   channel,
                   identifier=0,
                   network_source_address=None,
                   network_target_address=None,
                   network_address_extension=None,
                   as_timeout=0,
                   bs_timeout=0,
                   cs_timeout=0,
                   enable_transmit_cancellation=True,
                   addressing_format='standard',
                   enable_padding=True,
                   network_sdu_type='physical',
                   network_sdu_reference=0):
        new_tx_sdu = self.handle.ffi.new('CanTp_TxNSduType *')
        if network_source_address is None:
            network_source_address = self.handle.ffi.NULL
        if network_target_address is None:
            network_target_address = self.handle.ffi.NULL
        if network_address_extension is None:
            network_address_extension = self.handle.ffi.NULL
        new_tx_sdu.nSduId = identifier
        new_tx_sdu.pNSa = network_source_address
        new_tx_sdu.pNTa = network_target_address
        new_tx_sdu.pNAe = network_address_extension
        new_tx_sdu.nas = as_timeout
        new_tx_sdu.nbs = bs_timeout
        new_tx_sdu.ncs = cs_timeout
        new_tx_sdu.tc = enable_transmit_cancellation
        new_tx_sdu.af = {'standard': self.handle.lib.CANTP_STANDARD,
                         'fixed': self.handle.lib.CANTP_NORMALFIXED,
                         'extended': self.handle.lib.CANTP_EXTENDED,
                         'mixed 11 bits': self.handle.lib.CANTP_MIXED,
                         'mixed 29 bits': self.handle.lib.CANTP_MIXED29BIT}[addressing_format]
        new_tx_sdu.padding = enable_padding
        new_tx_sdu.taType = {'physical': self.handle.lib.CANTP_PHYSICAL,
                             'functional': self.handle.lib.CANTP_FUNCTIONAL}[network_sdu_type]
        new_tx_sdu.txNSduRef = network_sdu_reference
        if channel.nSdu.tx == self.handle.ffi.NULL:
            channel.nSdu.tx = new_tx_sdu
            channel.nSdu.txNSduCnt += 1
        else:
            raise NotImplementedError
        return new_tx_sdu
