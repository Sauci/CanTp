//
// Created by Guillaume Sottas on 2019-08-08.
//

#include "iso_tp.h"

ISOTPInterface::status ISOTP::Initialize(ISOTPInterface::handle can_tp_handle,
                                         ISOTPInterface::can_handle can_handle)
{
    CanTp_Init(&this->config);

    return 0;
}

ISOTPInterface::status ISOTP::AddMapping(ISOTPInterface::handle can_tp_handle,
                                         ISOTPInterface::can_id id,
                                         ISOTPInterface::can_id id_response,
                                         CanTp_AddressingFormatType format_type,
                                         ISOTPInterface::TPCANTPMessageType message_type,
                                         CanTp_NSaType source_address,
                                         CanTp_NTaType target_address,
                                         CanTp_NAeType address_extension,
                                         CanTp_ComTypeType addressing_type)
{
    return 0;
}

ISOTPInterface::status ISOTP::Read(ISOTPInterface::handle can_tp_handle,
                                   can_tp_message &message)
{
    return 0;
}

ISOTPInterface::status ISOTP::Write(ISOTPInterface::handle can_tp_handle,
                                    can_tp_message &message)
{
    PduInfoType pdu_info = {
        .MetaDataPtr = nullptr,
        .SduDataPtr = message.message,
        .SduLength = message.size
    };

    return CanTp_Transmit(0, &pdu_info);
}
