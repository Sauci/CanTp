/**
 * @file CanIf.h
 * @author Guillaume Sottas
 * @date 07/12/2017
 */

#ifndef CANIF_H
#define CANIF_H

#ifdef __cplusplus

extern "C"
{

#endif /* ifdef __cplusplus */

#include "CanIf_Types.h"

extern Std_ReturnType CanIf_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo);

#ifdef __cplusplus

}

#endif /* ifdef __cplusplus */

#endif /* define CANIF_H */
