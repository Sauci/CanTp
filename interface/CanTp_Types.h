/**
 * @file CanTp_Types.h
 * @author Guillaume Sottas
 * @date 15/01/2018
 */

#ifndef CANTP_TYPES_H
#define CANTP_TYPES_H

#ifdef __cplusplus

extern "C" {

#endif /* ifdef __cplusplus */

/*------------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                     */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_TYPES_H
 * @{
 */

#ifndef COMSTACK_TYPES_H
#include "ComStack_Types.h"
#endif /* #ifndef COMSTACK_TYPES_H */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global data type definitions (typedef, struct).                                                */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GTDEF
 * @{
 */

typedef enum
{
    /**
     * @brief full duplex channel
     */
    CANTP_MODE_FULL_DUPLEX,

    /**
     * @brief half duplex channel
     */
    CANTP_MODE_HALF_DUPLEX

} CanTp_ChannelMode; /* CanTpChannelMode. */

typedef enum
{
    /**
     * @brief extended addressing format
     */
    CANTP_EXTENDED,

    /**
     * @brief mixed 11 bit addressing format
     */
    CANTP_MIXED,

    /**
     * @brief mixed 29 bit addressing format
     */
    CANTP_MIXED29BIT,

    /**
     * @brief normal fixed addressing format
     */
    CANTP_NORMALFIXED,

    /**
     * @brief normal addressing format
     */
    CANTP_STANDARD

} CanTp_AddressingFormatType;

typedef enum
{
    /**
     * @brief padding is used
     */
    CANTP_OFF,

    /**
     * @brief padding is not used
     */
    CANTP_ON

} CanTp_StateType;

typedef CanTp_StateType CanTp_RxPaddingActivationType;

typedef CanTp_StateType CanTp_TxPaddingActivationType;

typedef enum
{
    /**
     * @brief functional request type
     */
    CANTP_FUNCTIONAL,

    /**
     * @brief physical request type
     */
    CANTP_PHYSICAL

} CanTp_ComTypeType;

typedef struct
{
    uint8 nSa; /* CanTpNSa. */
} CanTp_NSaType; /* CanTpNSa. */

typedef struct
{
    uint8 nTa; /* CanTpNTa. */
} CanTp_NTaType; /* CanTpNTa. */

typedef struct
{
    uint8 nAe; /* CanTpNAe. */
} CanTp_NAeType; /* CanTpNAe. */

typedef struct
{
    const uint32 rxFcNPduRef; /* CanTpRxFcNPduRef. */
    const uint16 rxFcNPduId; /* CanTpRxFcNPduId. */
} CanTp_RxFcNPduType; /* CanTpRxFcNPdu. */

typedef struct
{
    /**
     * @brief reference to a Pdu in the COM stack
     */
    const uint32 fcNPduRef; /* CanTpTxFcNPduRef. */

    /**
     * @brief used for grouping of the ID of a PDU and the reference to a PDU. this N-PDU produces
     * a meta data item of type CAN_ID_32
     */
    const uint16 fcNPduId; /* CanTpTxFcNPduConfirmationPduId. */

} CanTp_TxFcNPduType; /* CanTpTxFcNPdu. */

typedef struct
{
    /**
     * @brief unique identifier to a structure that contains all useful information to process the
     * reception of a network SDU.
     *
     * @warning this identifier must be unique in the scope of CanTp configuration module (both
     * directions).
     */
    const uint16 nSduId; /* CanTpRxNSduId. */
    const CanTp_NSaType *pNSa;
    const CanTp_NTaType *pNTa;
    const CanTp_NAeType *pNAe;
    const uint8 bs; /* CanTpBs. */
    const uint32 nar; /* CanTpNar. */
    const uint32 nbr; /* CanTpNbr. */
    const uint32 ncr; /* CanTpNcr. */
    const uint16 wftMax; /* CanTpRxWftMax. */

    /**
     * @brief separation time minimum between two consecutive frames [us].
     */
    const uint32 sTMin; /* CanTpSTmin. */
    const CanTp_AddressingFormatType af; /* CanTpRxAddressingFormat. */
    const CanTp_RxPaddingActivationType padding; /* CanTpRxPaddingActivation. */
    const CanTp_ComTypeType taType; /* CanTpRxTaType. */
    const PduIdType rxNSduRef; /* CanTpRxNSduRef. */
} CanTp_RxNSduType; /* CanTpRxNSdu. */

typedef struct
{
    /**
     * @brief unique identifier to a structure that contains all useful information to process the
     * transmission of a network SDU.
     *
     * @warning this identifier must be unique in the scope of CanTp configuration module (both
     * directions).
     */
    const uint16 nSduId; /* CanTpTxNSduId. */

    const CanTp_NSaType *pNSa;
    const CanTp_NTaType *pNTa;
    const CanTp_NAeType *pNAe;

    /**
     * @brief value [us] of the N_As timeout. N_As is the time for transmission of a CAN frame (any
     * N-PDU) on the part of the sender
     */
    const uint32 nas; /* CanTpNas. */

    /**
     * @brief value [us] of the N_Bs timeout. N_Bs is the time of transmission until reception of
     * the next flow control N-PDU
     */
    const uint32 nbs; /* CanTpNbs. */

    /**
     * @brief value [us] of the performance requirement of (N_Cs + N_As). N_Cs is the time in which
     * CanTp is allowed to request the tx data of a consecutive frame N-PDU
     */
    const uint32 ncs; /* CanTpNcs. */

    /**
     * @brief switch for enabling transmit cancellation
     */
    const boolean tc; /* CanTpTc. */

    /**
     * @brief declares which communication addressing format is supported for this TxNSdu
     */
    const CanTp_AddressingFormatType af; /* CanTpTxAddressingFormat. */

    /**
     * @brief defines if the transmit frame use padding or not. this parameter is restricted to 8
     * byte N-PDUs.
     */
    const CanTp_TxPaddingActivationType padding; /* CanTpTxPaddingActivation. */

    /**
     * @brief declares the communication type of this TxNSdu
     */
    const CanTp_ComTypeType taType; /* CanTpTxTaType. */

    /**
     * @brief reference to a PDU in the COM stack
     */
    const uint32 txNSduRef; /* CanTpTxNSduRef. */

} CanTp_TxNSduType; /* CanTpTxNSdu. */

typedef struct
{
    const uint16 id; /* CanTpRxNPduId. */
    const uint32 rxNPduId; /* CanTpRxNPduRef. */
} CanTp_RxNPduType; /* CanTpRxNPdu. */

typedef struct
{
    const uint32 pduRef; /* CanTpTxNPduRef. */
    const uint16 pduConfirmationPduId; /* CanTpTxNPduConfirmationPduId. */
} CanTp_TxNPduType; /* CanTpTxNPdu. */

typedef struct
{
    struct
    {
        const CanTp_RxNSduType *rx;
        const uint32 rxNSduCnt;
        const CanTp_TxNSduType *tx;
        const uint32 txNSduCnt;
    } nSdu;
    const CanTp_ChannelMode channelMode;
} CanTp_ChannelType; /* CanTpChannel. */

/**
 * @brief data structure type for the post-build configuration parameters.
 */
typedef struct
{
    /**
     * @brief period between two calls of CanTp_MainFunction [us].
     * @note see CanTpMainFunctionPeriod parameter
     */
    const uint32 mainFunctionPeriod;
    const uint32 maxChannelCnt; /* CanTpMaxChannelCnt. */
    const CanTp_ChannelType *pChannel;
    const uint8 paddingByte; /* CanTpPaddingByte. */
} CanTp_ConfigType;

/** @} */

#ifdef __cplusplus
};

#endif /* ifdef __cplusplus */

#endif /* define CANTP_TYPES_H */
