//
// Created by Guillaume Sottas on 2019-08-08.
//

#ifndef ISO_TP_H
#define ISO_TP_H

#include "iso_tp_interface.h"

class ISOTP : public ISOTPInterface
{

    CanTp_ConfigType config = {
        .mainFunctionPeriod = 0,
        .maxChannelCnt = 0,
        .paddingByte = 0,
        .pChannel = nullptr
    };

public:
    ISOTP() = default;

    ISOTPInterface::status Initialize(handle can_tp_handle, can_handle can_handle) override;

    ISOTPInterface::status AddMapping(handle can_tp_handle,
                                      can_id id,
                                      can_id id_response,
                                      CanTp_AddressingFormatType format_type,
                                      TPCANTPMessageType message_type,
                                      CanTp_NSaType source_address,
                                      CanTp_NTaType target_address,
                                      CanTp_NAeType address_extension,
                                      CanTp_ComTypeType addressing_type) override;

    ISOTPInterface::status Read(handle can_tp_handle, can_tp_message &message) override;

    ISOTPInterface::status Write(handle can_tp_handle, can_tp_message &message) override;
};

#endif //ISO_TP_H
