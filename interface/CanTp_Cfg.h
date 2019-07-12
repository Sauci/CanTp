/**
 * @file CanTp_Cfg.h
 * @author Guillaume Sottas
 * @date 04/07/2019
 */

#ifndef CANTP_CFG_H
#define CANTP_CFG_H

/* SWS_BSW_00059 */
#ifndef CANTP_AR_RELEASE_MAJOR_VERSION
#error unknown AUTOSAR release major version
#elif (CANTP_AR_RELEASE_MAJOR_VERSION != 4)
#error incompatible AUTOSAR release major version
#endif

/* SWS_BSW_00059 */
#ifndef CANTP_AR_RELEASE_MINOR_VERSION
#error unknown AUTOSAR release minor version
#elif (CANTP_AR_RELEASE_MINOR_VERSION != 4)
#error incompatible AUTOSAR release minor version
#endif

#ifndef CANTP_MAX_NUM_OF_CHANNEL
#define CANTP_MAX_NUM_OF_CHANNEL (0x10u)
#endif

#ifndef CANTP_MAX_NUM_OF_N_SDU
#define CANTP_MAX_NUM_OF_N_SDU (0x10u)
#endif

#endif /* #ifndef CANTP_CFG_H */
