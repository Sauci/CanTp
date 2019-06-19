/**
 * @file CanTp_Cbk.h
 * @author Guillaume Sottas
 * @date 15/01/2018
 *
 * @defgroup CANTP_CBK notifications
 * @ingroup CANTP
 *
 * @brief notifications provided by CAN transport layer.
 *
 * @defgroup CANTP_CBK_GCFDECL global callback function declarations
 * @ingroup CANTP_CBK
 */

#ifndef CANTP_CBK_H
#define CANTP_CBK_H

#ifdef __cplusplus

extern "C"
{

#endif /* #ifdef __cplusplus */

/*-----------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_CBK
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global callback function declarations.                                                        */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_CBK_GCFDECL
 * @{
 */

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief indication of a received PDU from a lower layer communication interface module.
 * @param [in] rxPduId ID of the received PDU.
 * @param [in] pPduInfo contains the length (SduLength) of the received PDU, a pointer to a buffer (SduDataPtr) containing the PDU, and the meta-data related to this PDU.
 * @satisfy{@req{SWS_CanTp_00214}}
 * @satisfy{@req{SWS_CanTp_00235}}
 * @satisfy{@req{SWS_CanTp_00322}}
 */
void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief the lower layer communication interface module confirms the transmission of a PDU, or the failure to transmit a PDU.
 * @param [in] txPduId ID of the PDU that has been transmitted
 * @param [in] result E_OK: the PDU was transmitted, E_NOT_OK: transmission of the PDU failed
 * @satisfy{@req{SWS_CanTp_00215}}
 * @satisfy{@req{SWS_CanTp_00236}}
 */
void CanTp_TxConfirmation(PduIdType txPduId, Std_ReturnType result);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/** @} */

#ifdef __cplusplus

}

#endif /* #ifdef __cplusplus */

#endif /* #ifndef CANTP_CBK_H */
