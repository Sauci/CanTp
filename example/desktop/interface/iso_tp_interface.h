//
// Created by Guillaume Sottas on 2019-08-06.
//

#ifndef ISO_TP_INTERFACE_H
#define ISO_TP_INTERFACE_H

#include "CanTp.h"

struct ISOTPInterface
{
    typedef unsigned int status;

    typedef unsigned int handle;
    typedef unsigned int can_handle;

    typedef uint32 can_id;

    typedef enum
    {
        UNKNOWN = 0x00,
        DIAGNOSTIC = 0x01,
        REMOTE_DIAGNOSTIC = 0x02,
        REQUEST_CONFIRMATION = 0x03,
        INDICATION = 0x04,
    } TPCANTPMessageType;

    typedef struct
    {
        uint8 *message;
        unsigned int size;
    } can_tp_message;

    virtual status Initialize(handle can_tp_handle, can_handle can_handle) = 0;

    virtual status AddMapping(handle can_tp_handle,
                              can_id id,
                              can_id id_response,
                              CanTp_AddressingFormatType format_type,
                              TPCANTPMessageType message_type,
                              CanTp_NSaType source_address,
                              CanTp_NTaType target_address,
                              CanTp_NAeType address_extension,
                              CanTp_ComTypeType addressing_type) = 0;

    virtual status Read(handle can_tp_handle, can_tp_message &message) = 0;

    virtual status Write(handle can_tp_handle, can_tp_message &message) = 0;
};

#endif //ISO_TP_INTERFACE_H
