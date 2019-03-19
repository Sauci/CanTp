/**
 * @file CanTp_PBcfg.c
 * @author
 * @date
 *
 * @defgroup CANTP_PBCFG post-build configuration
 * @ingroup CANTP
 *
 * @defgroup CANTP_PBCFG_LDEF local definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LTDEF local data type definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LMDEF local macros
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LFDECL local function declarations
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LCDEF local constant definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LVDEF local variable definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_GCDEF global constant definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_GVDEF global variable definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_GFDEF global function definitions
 * @ingroup CANTP_PBCFG
 * @defgroup CANTP_PBCFG_LFDEF local function definitions
 * @ingroup CANTP_PBCFG
 */

/*-----------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG
 * @{
 */

#include "CanTp.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local definitions (#define).                                                                  */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local data type definitions (typedef, struct).                                                */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LTDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local macros definitions (#define, inline).                                                   */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LMDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local function declarations (static).                                                         */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LFDECL
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local constant definitions (static const).                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LCDEF
 * @{
 */

#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_NSaType CanTp_NSaConfig[] = {
    {
        0x0Cu /* nSa */
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_NTaType CanTp_NTaConfig[] = {
    {
        0x0Cu /* nTa */
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_NAeType CanTp_NAeConfig[] = {
    {
        0x0Cu /* nAe */
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_RxNPduType CanTp_RxNPduConfig[] = {
    {

    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

/* TODO: use CANTP_NUM_OF_SDU. */
const CanTp_RxNSduType CanTp_RxNSduConfig[] = {
    {
        0x00u, /* nSduId */
        &CanTp_NSaConfig[0x00u], /* pNSa */
        &CanTp_NTaConfig[0x00u], /* pNTa */
        &CanTp_NAeConfig[0x00u], /* pNAe */
        0x02u, /* bs */
        0x64u, /* nar */
        0x64u, /* nbr */
        0x64u, /* ncr */
        0x64u, /* wftMax */
        0x55u, /* sTMin */
        0x00u, /* rxNSduRef */
        CANTP_EXTENDED, /* af */
        CANTP_ON, /* padding */
        CANTP_PHYSICAL /* comType */
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_TxNSduType CanTp_TxNSduConfig[] = {
    {
        0x01u, /* nSduId */
        &CanTp_NSaConfig[0x00u], /* pNSa */
        &CanTp_NTaConfig[0x00u], /* pNTa */
        &CanTp_NAeConfig[0x00u], /* pNAe */
        0x64u, /* nas */
        0x64u << 0x01u, /* nbs */
        0x64u << 0x02u, /* ncs */
        TRUE, /* tc */
        CANTP_STANDARD, /* af */
        CANTP_ON, /* padding */
        CANTP_PHYSICAL, /* taType */
        0xA0u /* nSduRef */
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_ChannelType CanTp_ChannelConfig[] = {
    {
        {
            CanTp_RxNSduConfig,
            sizeof(CanTp_RxNSduConfig) / sizeof(CanTp_RxNSduConfig[0x00u]),
            CanTp_TxNSduConfig,
            sizeof(CanTp_TxNSduConfig) / sizeof(CanTp_TxNSduConfig[0x00u])
        },
        CANTP_MODE_FULL_DUPLEX
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"


#define CanTp_START_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

const CanTp_ConfigType CanTp_Config[] = {
    {
        10,
        sizeof(CanTp_ChannelConfig) / sizeof(CanTp_ChannelConfig[0x00u]),
        &CanTp_ChannelConfig[0x00u],
        0xFFu
    }
};

#define CanTp_STOP_SEC_CONST_UNSPECIFIED
#include "CanTp_MemMap.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local variable definitions (static).                                                          */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LVDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global constant definitions (extern const).                                                   */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_GCDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global variable definitions (extern).                                                         */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_GVDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global function definitions.                                                                  */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_GFDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local function definitions (static).                                                          */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_PBCFG_LFDEF
 * @{
 */

/** @} */
