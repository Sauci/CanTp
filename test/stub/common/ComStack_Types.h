/**
 * @file ComStack_Types.h
 * @author Guillaume Sottas
 * @date 06/12/2017
 */

#ifndef COMSTACK_TYPES_H
#define COMSTACK_TYPES_H

#ifdef __cplusplus

extern "C" {

#endif /* ifdef __cplusplus */

#ifndef STD_TYPES_H
#include "Std_Types.h"
#endif /* #ifndef STD_TYPES_H */

typedef uint16 PduIdType;

typedef uint32 PduLengthType;

typedef uint8 NetworkHandleType;

typedef uint8 IcomConfigIdType;

typedef enum
{
    ICOM_SWITCH_E_OK = 0x00u,
    ICOM_SWITCH_E_FAILED = 0x01u
} IcomSwitch_ErrorType;

typedef enum
{
    TP_STMIN = 0x00u,
    TP_BS = 0x01u,
    TP_BC = 0x02u
} TPParameterType;

typedef enum
{
    BUFREQ_OK = 0x00u,
    BUFREQ_E_NOT_OK = 0x01u,
    BUFREQ_E_BUSY = 0x02u,
    BUFREQ_E_OVFL = 0x03u
} BufReq_ReturnType;

typedef enum
{
    TP_DATACONF = 0x00u,
    TP_DATARETRY = 0x01u,
    TP_CONFPENDING = 0x02u
} TpDataStateType;

typedef struct
{
    uint8 *SduDataPtr;
    uint8 *MetaDataPtr;
    PduLengthType SduLength;
} PduInfoType;

typedef struct
{
    TpDataStateType TpDataState;
    PduLengthType TxTpDataCnt;
} RetryInfoType;

#ifdef __cplusplus
}

#endif /* ifdef __cplusplus */

#endif /* #ifndef COMSTACK_TYPES_H */
