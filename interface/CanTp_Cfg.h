/**
 * @file CanTp_Cfg.h
 * @author Guillaume Sottas
 * @date 15/01/2018
 *
 * @defgroup CANTP_CFG configuration
 * @ingroup CANTP
 *
 * @brief configuration parameters of CanTp module.
 *
 * @defgroup CANTP_CFG_GDEF API interfaces configuration
 * @ingroup CANTP_CFG
 */

#ifndef CANTP_CFG_H
#define CANTP_CFG_H

#ifdef __cplusplus

extern "C"
{

#endif /* ifdef __cplusplus */


/*-----------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_CFG
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global definitions (#define).                                                                 */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_CFG_GDEF
 * @{
 */

#ifndef CANTP_DEV_ERROR_DETECT

/**
 * @brief enables/disables detection of development error module-wide.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_DEV_ERROR_DETECT STD_ON

#endif /* ifndef CANTP_DEV_ERROR_DETECT */


#ifndef CANTP_GET_VERSION_INFO_API

/**
 * @brief enables/disables @ref CanTp_GetVersionInfo API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_GET_VERSION_INFO_API STD_ON

#endif /* ifndef CANTP_GET_VERSION_INFO_API */


#ifndef CANTP_SHUTDOWN_API

/**
 * @brief enables/disables @ref CanTp_Shutdown API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_SHUTDOWN_API STD_ON

#endif /* ifndef CANTP_SHUTDOWN_API */


#ifndef CANTP_TRANSMIT_API

/**
 * @brief enables/disables @ref CanTp_Transmit API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_TRANSMIT_API STD_ON

#endif /* ifndef CANTP_TRANSMIT_API */


#ifndef CANTP_CANCEL_TRANSMIT_API

/**
 * @brief enables/disables @ref CanTp_CancelTransmit API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_CANCEL_TRANSMIT_API STD_ON

#endif /* ifndef CANTP_CANCEL_TRANSMIT_API */


#ifndef CANTP_CANCEL_RECEIVE_API

/**
 * @brief enables/disables @ref CanTp_CancelReceive API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_CANCEL_RECEIVE_API STD_ON

#endif /* ifndef CANTP_CANCEL_RECEIVE_API */


#ifndef CANTP_CHANGE_PARAMETER_API

/**
 * @brief enables/disables @ref CanTp_ChangeParameter API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_CHANGE_PARAMETER_API STD_ON

#endif /* ifndef CANTP_CHANGE_PARAMETER_API */


#ifndef CANTP_READ_PARAMETER_API

/**
 * @brief enables/disables @ref CanTp_ReadParameter API interface.
 * @note as the define might be defined externally, the definition is protected against
 * redefinition.
 */
#define CANTP_READ_PARAMETER_API STD_ON

#endif /* ifndef CANTP_READ_PARAMETER_API */

/**
 * @brief number of channels available.
 */
#define CANTP_NUM_OF_CHANNEL (0x01u)

/**
 * @brief maximum number network SDU(s) per channel.
 */
#define CANTP_MAX_NUM_OF_N_SDU (0x02u)

/**
 * @brief value of padding byte(s).
 */
#define CANTP_PADDING_BYTE (0x55u)

/** @} */

#ifdef __cplusplus

}

#endif /* ifdef __cplusplus */

#endif /* define CANTP_CFG_H */
