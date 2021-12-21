/**
 * @file CanTp.h
 * @author Guillaume Sottas
 * @date 15/01/2018
 *
 * @defgroup CANTP CAN transport layer
 *
 * @defgroup CANTP_H_GDEF identification informations
 * @ingroup CANTP_H
 * @defgroup CANTP_H_E errors classification
 * @ingroup CANTP_H
 * @defgroup CANTP_H_E_D development errors
 * @ingroup CANTP_H_E
 * @defgroup CANTP_H_E_R runtime errors
 * @ingroup CANTP_H_E
 * @defgroup CANTP_H_E_T transient faults
 * @ingroup CANTP_H_E
 * @defgroup CANTP_H_GTDEF global data type definitions
 * @ingroup CANTP_H
 * @defgroup CANTP_H_EFDECL external function declarations
 * @ingroup CANTP_H
 * @defgroup CANTP_H_GCDECL global constant declarations
 * @ingroup CANTP_H
 * @defgroup CANTP_H_GVDECL global variable declarations
 * @ingroup CANTP_H
 * @defgroup CANTP_H_GFDECL global function declarations
 * @ingroup CANTP_H
 * @defgroup CANTP_H_GSFDECL global scheduled function declarations
 * @ingroup CANTP_H
 */

#ifndef CANTP_H
#define CANTP_H

#ifdef __cplusplus

extern "C" {

#endif /* #ifdef __cplusplus */

/*------------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                     */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H
 * @{
 */

#include "CanTp_Types.h"

#if defined(CFFI_ENABLE)

/**
 * @brief if CFFI_ENABLE is defined, expose the CanTp callback function to CFFI module as well as
 * the external functions.
 */
#include "CanTp_Cbk.h"

#ifndef CANIF_H
#include "CanIf.h"
#endif /* #ifndef CANIF_H */

#include "PduR.h"

#if (CANTP_DEV_ERROR_DETECT == STD_ON)

#include "Det.h"

#endif /* #if (CANTP_DEV_ERROR_DETECT == STD_ON) */

#endif /* #if defined(CFFI_ENABLE) */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global definitions (#define).                                                                  */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GDEF
 * @{
 */

/**
 * @brief unique identifier of the CAN transport layer.
 * @note this value corresponds to document ID of corresponding Autosar software specification.
 */
#define CANTP_MODULE_ID (0x0Eu)

#ifndef CANTP_SW_MAJOR_VERSION

/**
 * @brief CAN transport layer major version number.
 */
#define CANTP_SW_MAJOR_VERSION (0x00u)

#endif /* #ifndef CANTP_SW_MAJOR_VERSION */

#ifndef CANTP_SW_MINOR_VERSION

/**
 * @brief CAN transport layer minor version number.
 */
#define CANTP_SW_MINOR_VERSION (0x01u)

#endif /* #ifndef CANTP_SW_MINOR_VERSION */

#ifndef CANTP_SW_PATCH_VERSION

/**
 * @brief CAN transport layer patch version number.
 */
#define CANTP_SW_PATCH_VERSION (0x00u)

#endif /* #ifndef CANTP_SW_PATCH_VERSION */

/**
 * @brief @ref CanTp_Init API ID.
 */
#define CANTP_INIT_API_ID (0x01u)

/**
 * @brief @ref CanTp_GetVersionInfo API ID.
 */
#define CANTP_GET_VERSION_INFO_API_ID (0x07u)

/**
 * @brief @ref CanTp_Shutdown API ID.
 */
#define CANTP_SHUTDOWN_API_ID (0x02u)

/**
 * @brief @ref CanTp_Transmit API ID.
 */
#define CANTP_TRANSMIT_API_ID (0x49u)

/**
 * @brief @ref CanTp_CancelTransmit API ID.
 */
#define CANTP_CANCEL_TRANSMIT_API_ID (0x4Au)

/**
 * @brief @ref CanTp_CancelReceive API ID.
 */
#define CANTP_CANCEL_RECEIVE_API_ID (0x4Cu)

/**
 * @brief @ref CanTp_ChangeParameter API ID.
 */
#define CANTP_CHANGE_PARAMETER_API_ID (0x4Bu)

/**
 * @brief @ref CanTp_ReadParameter API ID.
 */
#define CANTP_READ_PARAMETER_API_ID (0x0Bu)

/**
 * @brief @ref CanTp_RxIndication API ID.
 */
#define CANTP_RX_INDICATION_API_ID (0x42u)

/**
 * @brief @ref CanTp_MainFunction API ID.
 */
#define CANTP_MAIN_FUNCTION_API_ID (0x06u)

/** @} */

/**
 * @addtogroup CANTP_H_E_D
 * @{
 */

/**
 * @brief API service called with wrong parameter(s): when @ref CanTp_Transmit is called for a none
 * configured PDU identifier or with an identifier for a received PDU.
 */
#define CANTP_E_PARAM_CONFIG (0x01u)

/**
 * @brief API service called with wrong parameter(s): when @ref CanTp_Transmit is called for a none
 * configured PDU identifier or with an identifier for a received PDU.
 */
#define CANTP_E_PARAM_ID (0x02u)

/**
 * @brief API service called with a NULL pointer. in case of this error, the API service shall
 * return immediately without any further action, besides reporting this development error.
 */
#define CANTP_E_PARAM_POINTER (0x03u)

/**
 * @brief module initialization has failed, e.g. @ref CanTp_Init called with an invalid pointer in
 * post-build.
 */
#define CANTP_E_INIT_FAILED (0x04u)

/**
 * @brief API service used without module initialization: on any API call except @ref CanTp_Init and
 * @ref CanTp_GetVersionInfo if CanTp is in state CANTP_OFF.
 */
#define CANTP_E_UNINIT (0x20u)

/**
 * @brief invalid transmit PDU identifier (e.g. a service is called with an inexistent tx PDU
 * identifier).
 */
#define CANTP_E_INVALID_TX_ID (0x30u)

/**
 * @brief invalid receive PDU identifier (e.g. a service is called with an inexistent rx PDU
 * identifier).
 */
#define CANTP_E_INVALID_RX_ID (0x40u)

/** @} */

/**
 * @addtogroup CANTP_H_E_R
 * @{
 */

/**
 * @brief PDU received with a length smaller than 8 bytes (i.e. PduInfoPtr.SduLength < 8).
 */
#define CANTP_E_PADDING (0x70u)

/**
 * @brief @ref CanTp_Transmit is called for a configured tx I-Pdu with functional addressing and the
 * length parameter indicates, that the message can not be sent with a SF.
 */
#define CANTP_E_INVALID_TATYPE (0x90u)

/**
 * @brief requested operation is not supported - a cancel transmission/reception request for an
 * N-SDU that it is not on transmission/reception process.
 */
#define CANTP_E_OPER_NOT_SUPPORTED (0xA0u)

/**
 * @brief event reported in case of an implementation specific error other than a protocol timeout
 * error during a reception or a transmission.
 */
#define CANTP_E_COM (0xB0u)

/**
 * @brief event reported in case of a protocol timeout error during reception.
 */
#define CANTP_E_RX_COM (0xC0u)

/**
 * @brief event reported in case of a protocol timeout error during transmission.
 */
#define CANTP_E_TX_COM (0xD0u)

#define CANTP_I_NONE (0xFFu)
#define CANTP_I_N_AS (0x00u)
#define CANTP_I_N_BS (0x01u)
#define CANTP_I_N_CS (0x02u)
#define CANTP_I_N_AR (0x03u)
#define CANTP_I_N_BR (0x04u)
#define CANTP_I_N_CR (0x05u)
#define CANTP_I_ST_MIN (0x06u)
#define CANTP_I_RX_SF (0x85u)
#define CANTP_I_RX_FF (0x86u)
#define CANTP_I_N_BUFFER_OVFLW (0x90u)
#define CANTP_E_UNEXP_PDU (0x85u)

/** @} */

/**
 * @addtogroup CANTP_H_E_T
 * @{
 */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* external function declarations (extern).                                                       */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_EFDECL
 * @{
 */

#if (OS_GET_TIME_API == STD_ON)

extern uint32 CanTp_GetElapsedValue();

#endif

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global constant declarations (extern const).                                                   */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GCDECL
 * @{
 */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global variable declarations (extern).                                                         */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GVDECL
 * @{
 */

extern CanTp_StateType CanTp_State;

#ifdef CFFI_ENABLE

extern boolean CanTp_AbortedRxSession;

extern boolean CanTp_AbortedTxSession;

#endif /* #ifndef CFFI_ENABLE */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global function declarations.                                                                  */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GFDECL
 * @{
 */

#define CanTp_START_SEC_CODE_SLOW
#include "CanTp_MemMap.h"

/**
 * @brief this function initializes the CanTp module.
 * @param [in] pConfig pointer to the CanTp post-build configuration data
 */
void CanTp_Init(const CanTp_ConfigType *pConfig);

#define CanTp_STOP_SEC_CODE_SLOW
#include "CanTp_MemMap.h"

#if (CANTP_GET_VERSION_INFO_API == STD_ON)

#define CanTp_START_SEC_CODE_SLOW
#include "CanTp_MemMap.h"

/**
 * @brief this function returns the version information of the CanTp module.
 * @param [out] pVersionInfo indicator as to where to store the version information of this module
 */
void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo);

#define CanTp_STOP_SEC_CODE_SLOW
#include "CanTp_MemMap.h"

#endif /* #if (CANTP_GET_VERSION_INFO_API == STD_ON) */

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief this function is called to shutdown the CanTp module.
 */
void CanTp_Shutdown(void);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief requests transmission of a PDU.
 * @param [in] txPduId identifier of the PDU to be transmitted
 * @param [in] pPduInfo length of and pointer to the PDU data and pointer to meta-data
 *
 * @retval E_OK transmit request has been accepted
 * @retval E_NOT_OK transmit request has not been accepted
 */
Std_ReturnType CanTp_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief requests cancellation of an ongoing transmission of a PDU in a lower layer communication
 * module.
 * @param [in] txPduId identification of the PDU to be cancelled
 *
 * @retval E_OK cancellation was executed successfully by the destination module
 * @retval E_NOT_OK cancellation was rejected by the destination module
 */
Std_ReturnType CanTp_CancelTransmit(PduIdType txPduId);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief requests cancellation of an ongoing reception of a PDU in a lower layer transport protocol
 * module.
 * @param [in] rxPduId identification of the PDU to be cancelled
 *
 * @retval E_OK cancellation was executed successfully by the destination module
 * @retval E_NOT_OK cancellation was rejected by the destination module
 */
Std_ReturnType CanTp_CancelReceive(PduIdType rxPduId);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#if (CANTP_CHANGE_PARAMETER_API == STD_ON)

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief request to change a specific transport protocol parameter (e.g. block size).
 * @param [in] pduId identification of the PDU which the parameter change shall affect
 * @param [in] parameter ID of the parameter that shall be changed
 * @param [in] value the new value of the parameter
 *
 * @retval E_OK the parameter was changed successfully
 * @retval E_NOT_OK the parameter change was rejected
 */
Std_ReturnType CanTp_ChangeParameter(PduIdType pduId, TPParameterType parameter, uint16 value);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#endif /* #if (CANTP_CHANGE_PARAMETER_API == STD_ON) */

#if (CANTP_READ_PARAMETER_API == STD_ON)

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief this service is used to read the current value of reception parameters BS and STmin for a
 * specified N-SDU.
 * @param [in] pduId identifier of the received N-SDU on which the reception parameter are read
 * @param [in] parameter specify the parameter to which the value has to be read (BS or STmin)
 * @param [out] pValue pointer where the parameter value will be provided
 *
 * @retval E_OK request is accepted
 * @retval E_NOT_OK request is not accepted
 */
Std_ReturnType CanTp_ReadParameter(PduIdType pduId, TPParameterType parameter, uint16 *pValue);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#endif /* #if (CANTP_READ_PARAMETER_API == STD_ON) */

/** @} */

/*------------------------------------------------------------------------------------------------*/
/* global scheduled function declarations.                                                        */
/*------------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_H_GSFDECL
 * @{
 */

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief the main function for scheduling the CAN TP.
 */
void CanTp_MainFunction(void);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/** @} */

#ifdef __cplusplus
};

#endif /* #ifdef __cplusplus */

#endif /* #ifndef CANTP_H */
