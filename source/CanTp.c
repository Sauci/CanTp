/**
 * @file CanTp.c
 * @author
 * @date
 *
 * @defgroup CANTP_C implementation
 * @ingroup CANTP
 *
 * @defgroup CANTP_C_LDEF local definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LTDEF local data type definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LMDEF local macros
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LFDECL local function declarations
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LCDEF local constant definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LVDEF local variable definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_GCDEF global constant definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_GVDEF global variable definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_GFDEF global function definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_GSFDEF global scheduled function definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_GCFDEF global callback function definitions
 * @ingroup CANTP_C
 * @defgroup CANTP_C_LFDEF local function definitions
 * @ingroup CANTP_C
 */

/*-----------------------------------------------------------------------------------------------*/
/* included files (#include).                                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C
 * @{
 */

#ifdef __cplusplus

extern "C"
{

#endif /* ifdef __cplusplus */

#include "CanIf.h"
#include "CanTp.h"
#include "CanTp_Cbk.h"
#include "CanTp_Cfg.h"
#include "ComStack_Types.h"
#include "Det.h"
#include "PduR.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local definitions (#define).                                                                  */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LDEF
 * @{
 */

#define CANTP_CAN_FRAME_SIZE (0x08u)

#define CANTP_FLAG_SEND_DATA (0x01u << 0x00u)

#define CANTP_FLAG_COPY_DATA (0x01u << 0x01u)

#define CANTP_FLAG_WAIT_STMIN (0x01u << 0x02u)

#define CANTP_MS_TO_INTERNAL(timeout) (timeout * 1000u)

#define CANTP_INTERNAL_TO_MS(timeout) (timeout / 1000u)

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local data type definitions (typedef, struct).                                                */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LTDEF
 * @{
 */

typedef enum
{
    CANTP_DIRECTION_INVALID,
    CANTP_DIRECTION_RX,
    CANTP_DIRECTION_TX
} CanTp_DirectionType;

typedef enum
{
    CANTP_N_PCI_TYPE_INVALID,
    CANTP_N_PCI_TYPE_SF = 0x00u,
    CANTP_N_PCI_TYPE_FF = 0x01u,
    CANTP_N_PCI_TYPE_CF = 0x02u,
    CANTP_N_PCI_TYPE_FC = 0x03u
} CanTp_NPciType;

typedef enum
{
    CANTP_FLOW_STATUS_TYPE_INVALID = 0xFFu,
    CANTP_FLOW_STATUS_TYPE_CTS = 0x00u,
    CANTP_FLOW_STATUS_TYPE_WT = 0x01u,
    CANTP_FLOW_STATUS_TYPE_OVFLW = 0x02u,
} CanTp_FlowStatusType;

typedef enum
{
    CANTP_FRAME_STATE_INVALID,
    CANTP_FRAME_STATE_WAIT_SF_TX_CONFIRMATION,
    CANTP_FRAME_STATE_WAIT_FF_TX_CONFIRMATION,
    CANTP_FRAME_STATE_WAIT_FC_RX_INDICATION,
    CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION,
    CANTP_FRAME_STATE_WAIT_STMIN_TIMEOUT,
    CANTP_FRAME_STATE_TX_OK
} CanTp_FrameStateType;

typedef enum
{
    /* as the @ref CanTp_ChannelStateConfig memory section is cleared at start-up, make sure the
     * internal value of state field is set to CANTP_WAIT. */
        CANTP_INVALID = 0x00u,
    CANTP_WAIT,
    CANTP_PROCESSING
} CanTp_TaskStateType;

typedef struct
{
    //PduInfoType pduInfo;
    uint8 can[CANTP_CAN_FRAME_SIZE];
    uint32 size;
    uint32 sent;
    uint32 remaining;
} CanTp_NSduBufferType;

typedef struct
{
    uint32 currentAs;
    uint32 currentBs;
    uint32 currentCs;
    uint32_least targetStMin;
    uint32_least currentStMin;
} CanTp_TimeoutType;

typedef struct
{
    struct
    {
        const CanTp_RxNSduType *rx;
        const CanTp_TxNSduType *tx;
    } cfg;
    struct
    {
        CanTp_TaskStateType rx;
        CanTp_TaskStateType tx;
    } taskState;
    struct
    {
        CanTp_NSduBufferType rx;
        CanTp_NSduBufferType tx;
    } buf;
    struct
    {
        CanTp_TimeoutType rx;
        CanTp_TimeoutType tx;
    } timeout;
    CanTp_FrameStateType state;
    CanTp_NPciType pci;
    uint8 nSa;
    uint8 nTa;
    uint8 nAe;
    uint8 targetBlockSize;
    uint8 currentBlockSize;
    uint8 sn;
    CanTp_FlowStatusType fs;
    boolean metaData;
    CanTp_DirectionType dir;
    uint32 flag;
    PduInfoType pduInfo;
} CanTp_NSduType;

typedef struct
{
    CanTp_NSduType sdu[CANTP_MAX_NUM_OF_N_SDU];
} CanTp_ChannelRtType;

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local macros definitions (#define, inline).                                                   */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LMDEF
 * @{
 */

#ifndef CANTP_ENTER_CRITICAL_SECTION

#define CANTP_ENTER_CRITICAL_SECTION

#endif /* #ifndef CANTP_ENTER_CRITICAL_SECTION */

#ifndef CANTP_EXIT_CRITICAL_SECTION

#define CANTP_EXIT_CRITICAL_SECTION

#endif /* #ifndef CANTP_EXIT_CRITICAL_SECTION */

#ifndef CANTP_CRITICAL_SECTION

#define CANTP_CRITICAL_SECTION(...) \
CANTP_ENTER_CRITICAL_SECTION \
    __VA_ARGS__ \
CANTP_EXIT_CRITICAL_SECTION

#endif /* #ifndef CANTP_CRITICAL_SECTION */

#if (CANTP_DEV_ERROR_DETECT == STD_ON)

#define CANTP_DET_ASSERT_ERROR(condition, instanceId, apiId, errorId, ...) \
    if((condition)) \
    { \
        (void)Det_ReportError(CANTP_MODULE_ID, instanceId, apiId, errorId); \
        __VA_ARGS__; \
    }

#define CANTP_DET_ASSERT_RUNTIME_ERROR(condition, instanceId, apiId, errorId, ...) \
    if((condition)) \
    { \
        (void)Det_ReportRuntimeError(CANTP_MODULE_ID, instanceId, apiId, errorId); \
        __VA_ARGS__; \
    }

#else

#define CANTP_DET_ASSERT_ERROR(...)

#define CANTP_DET_ASSERT_RUNTIME_ERROR(...)

#endif

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local function declarations (static).                                                         */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LFDECL
 * @{
 */

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static Std_ReturnType CanTp_GetNSduFromPduId(PduIdType pduId, CanTp_NSduType **pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief this function decodes a raw minimum separation time (STmin) to a value in microsecond(s),
 * according to ISO 15765-2.
 *
 * @note see section 6.5.5.5 of ISO 15765-2.
 *
 * @param rawValue [in]: the raw minimum separation time (8 bits STmin value)
 * @return decoded minimum separation time value [μs]
 */
static uint32_least CanTp_DecodeSTMinValue(uint8 rawValue);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/**
 * @brief this function encodes a minimum separation time in microsecond(s) (STmin) to a 8 bits
 * value, according to ISO 15765-2.
 *
 * @note see section 6.5.5.5 of ISO 15765-2.
 *
 * @param value [in]: the minimum separation time [μs]
 * @return encoded minimum separation time value (8 bits STmin value)
 */
static uint8 CanTp_EncodeSTMinValue(uint32 value);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_AbortSession(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static CanTp_NPciType CanTp_GetPCIType(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static boolean CanTp_GetNextTxFrame(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_InitSFTx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_InitFFTx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_InitCFTx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_InitFCTx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_LDataRequest(CanTp_NSduType *pNSdu,
                                            BufReq_ReturnType (*pFunc)(CanTp_NSduType *));

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_FillAIField(CanTp_NSduType *pNSdu, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_FillPCIField(CanTp_NSduType *pNSdu, CanTp_NPciType nPciType, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_FillTxPayload(CanTp_NSduType *pNSdu, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_FillPadding(CanTp_NSduType *pNSdu, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local constant definitions (static const).                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LCDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local variable definitions (static).                                                          */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LVDEF
 * @{
 */

#define CanTp_START_SEC_VAR_FAST_INIT_UNSPECIFIED
#include "CanTp_MemMap.h"

static const CanTp_ConfigType *CanTp_ConfigPtr = NULL_PTR;

#define CanTp_STOP_SEC_VAR_FAST_INIT_UNSPECIFIED
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_VAR_FAST_CLEARED_UNSPECIFIED
#include "CanTp_MemMap.h"

static CanTp_ChannelRtType CanTp_Rt[CANTP_NUM_OF_CHANNEL];

#define CanTp_STOP_SEC_VAR_FAST_CLEARED_UNSPECIFIED
#include "CanTp_MemMap.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global constant definitions (extern const).                                                   */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_GCDEF
 * @{
 */

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global variable definitions (extern).                                                         */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_GVDEF
 * @{
 */

#define CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED
#include "CanTp_MemMap.h"

CanTp_StateType CanTp_State = CANTP_OFF;

#define CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED
#include "CanTp_MemMap.h"

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global function definitions.                                                                  */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_GFDEF
 * @{
 */

void CanTp_Init(const CanTp_ConfigType *pConfig)
{
    CANTP_DET_ASSERT_ERROR(pConfig == NULL_PTR,
                           0x00u,
                           CANTP_INIT_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return)

    Std_ReturnType result = E_OK;
    uint32_least n_sdu_range;
    uint32_least channel_idx;
    uint32_least rt_sdu_idx;
    uint32_least cfg_sdu_idx;
    const CanTp_ChannelType *p_cfg_channel;
    CanTp_ChannelRtType *p_rt_channel;
    CanTp_NSduType *p_rt_sdu;
    const CanTp_RxNSduType *p_cfg_rx_sdu;
    const CanTp_TxNSduType *p_cfg_tx_sdu;

    CanTp_ConfigPtr = pConfig;

    /* make sure the static configuration's channel(s) count fits into provided
     * CANTP_NUM_OF_CHANNEL. */
    if (pConfig->maxChannelCnt == CANTP_NUM_OF_CHANNEL)
    {
        /* iterate over all statically defined channels. */
        for (channel_idx = 0x00u; channel_idx < pConfig->maxChannelCnt; channel_idx++)
        {
            p_rt_channel = &CanTp_Rt[channel_idx];
            p_cfg_channel = &pConfig->pChannel[channel_idx];

            /* initialize all runtime-related variables. */
            for (rt_sdu_idx = 0x00u; rt_sdu_idx < CANTP_MAX_NUM_OF_N_SDU; rt_sdu_idx++)
            {
                p_rt_sdu = &CanTp_Rt[channel_idx].sdu[rt_sdu_idx];

                p_rt_sdu->flag = 0x00u;
                p_rt_sdu->cfg.rx = NULL_PTR;
                p_rt_sdu->cfg.tx = NULL_PTR;
                p_rt_sdu->taskState.rx = CANTP_INVALID;
                p_rt_sdu->taskState.tx = CANTP_INVALID;
                p_rt_sdu->buf.rx.sent = 0x00u;
                p_rt_sdu->buf.rx.size = 0x00u;
                p_rt_sdu->buf.rx.remaining = 0x00u;
                p_rt_sdu->buf.tx.sent = 0x00u;
                p_rt_sdu->buf.tx.size = 0x00u;
                p_rt_sdu->buf.tx.remaining = 0x00u;
                p_rt_sdu->timeout.rx.currentAs = 0x00u;
                p_rt_sdu->timeout.rx.currentBs = 0x00u;
                p_rt_sdu->timeout.rx.currentCs = 0x00u;
                p_rt_sdu->timeout.rx.currentStMin = 0x00u;
                p_rt_sdu->timeout.rx.targetStMin = 0x00u;
                p_rt_sdu->timeout.tx.currentAs = 0x00u;
                p_rt_sdu->timeout.tx.currentBs = 0x00u;
                p_rt_sdu->timeout.tx.currentCs = 0x00u;
                p_rt_sdu->timeout.tx.currentStMin = 0x00u;
                p_rt_sdu->timeout.tx.targetStMin = 0x00u;
                p_rt_sdu->state = CANTP_FRAME_STATE_INVALID;
                p_rt_sdu->pci = CANTP_N_PCI_TYPE_INVALID;
                p_rt_sdu->nSa = 0x00u;
                p_rt_sdu->nTa = 0x00u;
                p_rt_sdu->nAe = 0x00u;
                p_rt_sdu->targetBlockSize = 0x00u;
                p_rt_sdu->currentBlockSize = 0x00u;
                p_rt_sdu->sn = 0x00u;
                p_rt_sdu->fs = CANTP_FLOW_STATUS_TYPE_INVALID;
                p_rt_sdu->metaData = FALSE;
                p_rt_sdu->dir = CANTP_DIRECTION_INVALID;
            }

            /* make sure the static configuration's PDU count fits into provided
             * CANTP_MAX_NUM_OF_N_SDU. */
            n_sdu_range = p_cfg_channel->nSdu.rxNSduCnt + p_cfg_channel->nSdu.txNSduCnt;

            if (n_sdu_range <= CANTP_MAX_NUM_OF_N_SDU)
            {
                for (rt_sdu_idx = 0x00u; rt_sdu_idx < CANTP_MAX_NUM_OF_N_SDU; rt_sdu_idx++)
                {
                    for (cfg_sdu_idx = 0x00u;
                         cfg_sdu_idx < p_cfg_channel->nSdu.rxNSduCnt; cfg_sdu_idx++)
                    {
                        if (p_cfg_channel->nSdu.rx != NULL_PTR)
                        {
                            p_cfg_rx_sdu = &p_cfg_channel->nSdu.rx[cfg_sdu_idx];

                            /* make sure the nSduId is in allowed range. */
                            if (p_cfg_rx_sdu->nSduId < n_sdu_range)
                            {
                                if (p_cfg_rx_sdu->nSduId == rt_sdu_idx)
                                {
                                    p_rt_sdu = &p_rt_channel->sdu[p_cfg_rx_sdu->nSduId];

                                    /* make sure the runtime configuration for the current PDU is
                                     * not already defined (meaning duplicated SDU identifier in the
                                     * current static channel configuration). */
                                    if ((p_rt_sdu->cfg.rx == NULL_PTR) &&
                                        (p_rt_sdu->cfg.tx == NULL_PTR))
                                    {
                                        p_rt_sdu->dir = CANTP_DIRECTION_RX;
                                        p_rt_sdu->cfg.rx = p_cfg_rx_sdu;
                                        p_rt_sdu->taskState.rx = CANTP_WAIT;
                                    }
                                    else
                                    {
                                        result = E_NOT_OK;

                                        break;
                                    }
                                }
                            }
                            else
                            {
                                result = E_NOT_OK;

                                break;
                            }
                        }
                    }

                    for (cfg_sdu_idx = 0x00u;
                         cfg_sdu_idx < p_cfg_channel->nSdu.txNSduCnt; cfg_sdu_idx++)
                    {
                        if (p_cfg_channel->nSdu.tx != NULL_PTR)
                        {
                            p_cfg_tx_sdu = &p_cfg_channel->nSdu.tx[cfg_sdu_idx];

                            /* make sure the nSduId is in allowed range. */
                            if (p_cfg_tx_sdu->nSduId < n_sdu_range)
                            {
                                if (p_cfg_tx_sdu->nSduId == rt_sdu_idx)
                                {
                                    p_rt_sdu = &p_rt_channel->sdu[p_cfg_tx_sdu->nSduId];

                                    /* make sure the runtime configuration for the current PDU is
                                     * not already defined (meaning duplicated SDU identifier in the
                                     * current static channel configuration). */
                                    if ((p_rt_sdu->cfg.rx == NULL_PTR) &&
                                        (p_rt_sdu->cfg.tx == NULL_PTR))
                                    {
                                        p_rt_sdu->dir = CANTP_DIRECTION_TX;
                                        p_rt_sdu->cfg.tx = p_cfg_tx_sdu;
                                        p_rt_sdu->taskState.tx = CANTP_WAIT;
                                    }
                                    else
                                    {
                                        result = E_NOT_OK;

                                        break;
                                    }
                                }
                            }
                            else
                            {
                                result = E_NOT_OK;

                                break;
                            }
                        }
                    }
                }
            }
            else
            {
                result = E_NOT_OK;

                break;
            }
        }
    }
    else
    {
        result = E_NOT_OK;
    }

    if (result != E_OK)
    {
        CANTP_DET_ASSERT_ERROR(TRUE,
                               0x00u,
                               CANTP_INIT_API_ID,
                               CANTP_E_INIT_FAILED)
    }
    else
    {
        CanTp_State = CANTP_ON;
    }
}

void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo)
{

#if (CANTP_DEV_ERROR_DETECT == STD_ON)

    CANTP_DET_ASSERT_ERROR(pVersionInfo == NULL_PTR,
                           0x00u,
                           CANTP_GET_VERSION_INFO_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return)

#endif

    pVersionInfo->vendorID = 0x00u;
    pVersionInfo->moduleID = (uint16)CANTP_MODULE_ID;
    pVersionInfo->sw_major_version = 0x00u;
    pVersionInfo->sw_minor_version = 0x01u;
    pVersionInfo->sw_patch_version = 0x00u;
}

void CanTp_Shutdown(void)
{

#if (CANTP_DEV_ERROR_DETECT == STD_ON)

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_SHUTDOWN_API_ID,
                           CANTP_E_UNINIT,
                           return)

#endif

    CanTp_State = CANTP_OFF;
}

Std_ReturnType CanTp_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo)
{
    CanTp_TaskStateType taskState;
    CanTp_NSduType *p_n_sdu = NULL_PTR;
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_TRANSMIT_API_ID,
                           CANTP_E_UNINIT,
                           return E_NOT_OK)

    CANTP_DET_ASSERT_ERROR(pPduInfo == NULL_PTR,
                           0x00u,
                           CANTP_TRANSMIT_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return E_NOT_OK)

    if (CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == E_OK)
    {
        /* the task state is the flag used in CanTp_MainFunction to determine if the communication
         * process should go further (CANTP_PROCESSING) or not (CANTP_WAIT). thus we can prevent any
         * concurrency issues by protecting this variable and not the full structure. */
        CANTP_CRITICAL_SECTION(taskState = p_n_sdu->taskState.tx;)

        /* SWS_CanTp_00206: the function CanTp_Transmit shall reject a request if the CanTp_Transmit
         * service is called for a N-SDU identifier which is being used in a currently running CAN
         * Transport Layer session. */
        if ((taskState != CANTP_PROCESSING) &&
            (pPduInfo->SduLength > 0x0000u) &&
            (pPduInfo->SduLength <= 0x0FFFu))
        {
            p_n_sdu->buf.tx.size = pPduInfo->SduLength;
            p_n_sdu->buf.tx.sent = 0x00u;

            if (pPduInfo->MetaDataPtr != NULL_PTR)
            {
                p_n_sdu->metaData = TRUE;

                switch (p_n_sdu->cfg.tx->af)
                {
                    case CANTP_NORMALFIXED:
                    {
                        p_n_sdu->nSa = pPduInfo->MetaDataPtr[0x00u];
                        p_n_sdu->nTa = pPduInfo->MetaDataPtr[0x01u];

                        break;
                    }
                    case CANTP_MIXED:
                    {
                        p_n_sdu->nAe = pPduInfo->MetaDataPtr[0x00u];

                        break;
                    }
                    case CANTP_MIXED29BIT:
                    {
                        p_n_sdu->nSa = pPduInfo->MetaDataPtr[0x00u];
                        p_n_sdu->nTa = pPduInfo->MetaDataPtr[0x01u];
                        p_n_sdu->nAe = pPduInfo->MetaDataPtr[0x02u];

                        break;
                    }
                    case CANTP_EXTENDED:
                    {
                        p_n_sdu->nTa = pPduInfo->MetaDataPtr[0x00u];

                        break;
                    }
                    case CANTP_STANDARD:
                    default:
                    {
                        break;
                    }
                }
            }
            else
            {
                p_n_sdu->metaData = FALSE;
            }

            switch (CanTp_GetPCIType(p_n_sdu))
            {
                case CANTP_N_PCI_TYPE_SF:
                {
                    if (CanTp_LDataRequest(p_n_sdu, CanTp_InitSFTx) == BUFREQ_OK)
                    {
                        p_n_sdu->state = CANTP_FRAME_STATE_WAIT_SF_TX_CONFIRMATION;
                        taskState = CANTP_PROCESSING;
                        p_n_sdu->flag |= CANTP_FLAG_SEND_DATA;

                        tmp_return = E_OK;
                    }

                    break;
                }
                case CANTP_N_PCI_TYPE_FF:
                {
                    if (CanTp_LDataRequest(p_n_sdu, CanTp_InitFFTx) == BUFREQ_OK)
                    {
                        p_n_sdu->state = CANTP_FRAME_STATE_WAIT_FF_TX_CONFIRMATION;
                        taskState = CANTP_PROCESSING;
                        p_n_sdu->flag |= CANTP_FLAG_SEND_DATA;

                        tmp_return = E_OK;
                    }

                    break;
                }
                default:
                {
                    break;
                }
            }

            CANTP_CRITICAL_SECTION(p_n_sdu->taskState.tx = taskState;)
        }
    }

    return tmp_return;
}

Std_ReturnType CanTp_CancelTransmit(PduIdType txPduId)
{
    CanTp_TaskStateType taskState;
    CanTp_DirectionType direction;
    CanTp_NSduType *p_n_sdu;

    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_CANCEL_TRANSMIT_API_ID,
                           CANTP_E_UNINIT,
                           return tmp_return)

    if (CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == E_OK)
    {
        CANTP_CRITICAL_SECTION(
            {
                taskState = p_n_sdu->taskState.tx;

                /* TODO: check if overridden after init. */
                direction = p_n_sdu->dir;
            })

        if (direction == CANTP_DIRECTION_TX)
        {
            if (taskState == CANTP_PROCESSING)
            {
                taskState = CANTP_WAIT;

                CANTP_CRITICAL_SECTION(p_n_sdu->taskState.tx = taskState;)

                /* SWS_CanTp_00255: If the CanTp_CancelTransmit service has been successfully
                 * executed the CanTp shall call the PduR_CanTpTxConfirmation with notification
                 * result E_NOT_OK. */
                PduR_CanTpTxConfirmation(p_n_sdu->cfg.tx->nSduId, E_NOT_OK);

                tmp_return = E_OK;
            }
            else
            {
                /* SWS_CanTp_00254: if development error detection is enabled the function
                 * CanTp_CancelTransmit shall check the validity of TxPduId parameter. If the parameter
                 * value is invalid, the CanTp_CancelTransmit function shall raise the development error
                 * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
                 * if the parameter value indicates a cancel transmission request for an N-SDU that it is
                 * not on transmission process the CanTp module shall report a runtime error code
                 * CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the service shall return
                 * E_NOT_OK. */
                CANTP_DET_ASSERT_RUNTIME_ERROR(TRUE,
                                               0x00u,
                                               CANTP_CANCEL_TRANSMIT_API_ID,
                                               CANTP_E_OPER_NOT_SUPPORTED)
            }
        }
        else
        {
            CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, CANTP_CANCEL_TRANSMIT_API_ID, CANTP_E_PARAM_ID)
        }
    }
    else
    {
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, CANTP_CANCEL_TRANSMIT_API_ID, CANTP_E_PARAM_ID)
    }

    return tmp_return;
}

Std_ReturnType CanTp_CancelReceive(PduIdType rxPduId)
{
    CanTp_TaskStateType taskState;
    CanTp_DirectionType direction;
    CanTp_NSduType *p_n_sdu;

    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_CANCEL_RECEIVE_API_ID,
                           CANTP_E_UNINIT,
                           return tmp_return)

    if (CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == E_OK)
    {
        CANTP_CRITICAL_SECTION(
            {
                taskState = p_n_sdu->taskState.rx;

                /* TODO: check if overridden after init. */
                direction = p_n_sdu->dir;
            })

        if (direction == CANTP_DIRECTION_RX)
        {
            if (taskState == CANTP_PROCESSING)
            {
                taskState = CANTP_WAIT;

                CANTP_CRITICAL_SECTION(p_n_sdu->taskState.rx = taskState;)

                /* SWS_CanTp_00263: if the CanTp_CancelReceive service has been successfully
                 * executed the CanTp shall call the PduR_CanTpRxIndication with notification result
                 * E_NOT_OK. */
                PduR_CanTpRxIndication(p_n_sdu->cfg.tx->nSduId, E_NOT_OK);

                tmp_return = E_OK;
            }
            else
            {
                /* SWS_CanTp_00254: if development error detection is enabled the function
                 * CanTp_CancelTransmit shall check the validity of TxPduId parameter. If the parameter
                 * value is invalid, the CanTp_CancelTransmit function shall raise the development error
                 * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
                 * if the parameter value indicates a cancel transmission request for an N-SDU that it is
                 * not on transmission process the CanTp module shall report a runtime error code
                 * CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the service shall return
                 * E_NOT_OK. */
                CANTP_DET_ASSERT_RUNTIME_ERROR(TRUE,
                                               0x00u,
                                               CANTP_CANCEL_RECEIVE_API_ID,
                                               CANTP_E_OPER_NOT_SUPPORTED)
            }
        }
        else
        {
            CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, CANTP_CANCEL_RECEIVE_API_ID, CANTP_E_PARAM_ID)
        }
    }
    else
    {
        /* SWS_CanTp_00260: if development error detection is enabled the function
         * CanTp_CancelReceive shall check the validity of RxPduId parameter. if the parameter value
         * is invalid, the CanTp_CancelReceive function shall raise the development error
         * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294). */
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, CANTP_CANCEL_RECEIVE_API_ID, CANTP_E_PARAM_ID)
    }

    return tmp_return;
}

Std_ReturnType CanTp_ChangeParameter(PduIdType pduId, TPParameterType parameter, uint16 value)
{
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_CHANGE_PARAMETER_API_ID,
                           CANTP_E_UNINIT,
                           return tmp_return)

    (void)pduId;
    (void)parameter;
    (void)value;

    return tmp_return;
}

Std_ReturnType CanTp_ReadParameter(PduIdType pduId, TPParameterType parameter, uint16 *pValue)
{
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_READ_PARAMETER_API_ID,
                           CANTP_E_UNINIT,
                           return tmp_return)

    CANTP_DET_ASSERT_ERROR(pValue == NULL_PTR,
                           0x00u,
                           CANTP_READ_PARAMETER_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return tmp_return)

    CanTp_NSduType *p_n_sdu = &CanTp_Rt->sdu[pduId];

    switch (parameter)
    {
        case TP_STMIN:
        {
            *pValue = (uint16)p_n_sdu->timeout.tx.targetStMin;

            tmp_return = E_OK;

            break;
        }
        case TP_BS:
        {
            *pValue = (uint16)p_n_sdu->targetBlockSize;

            tmp_return = E_OK;

            break;
        }
        case TP_BC:
        default:
        {
            CANTP_DET_ASSERT_ERROR(TRUE,
                                   0x00u,
                                   CANTP_READ_PARAMETER_API_ID,
                                   CANTP_E_PARAM_ID)

            break;
        }
    }

    return tmp_return;
}

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global scheduled function definitions.                                                        */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_GSFDEF
 * @{
 */

void CanTp_MainFunction(void)
{

#if (CANTP_DEV_ERROR_DETECT == STD_ON)

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_MAIN_FUNCTION_API_ID,
                           CANTP_E_UNINIT)

#endif

    uint32 idx;
    CanTp_NSduType n_sdu;

    if (CanTp_State == CANTP_ON)
    {
        for (idx = 0x00u; idx < CANTP_MAX_NUM_OF_N_SDU; idx++)
        {
            CANTP_CRITICAL_SECTION(
                {
                    n_sdu = CanTp_Rt->sdu[idx];
                })

            if (n_sdu.taskState.tx == CANTP_PROCESSING)
            {
                if (CanTp_GetNextTxFrame(&n_sdu) == TRUE)
                {
                    /* TODO: get CanIf PDU ID from configuration. */
                    (void)CanIf_Transmit(1, &n_sdu.pduInfo);
                }

                n_sdu.timeout.tx.currentAs += CanTp_ConfigPtr->mainFunctionPeriod;
                n_sdu.timeout.tx.currentBs += CanTp_ConfigPtr->mainFunctionPeriod;
                n_sdu.timeout.tx.currentCs += CanTp_ConfigPtr->mainFunctionPeriod;
                n_sdu.timeout.tx.currentStMin += CanTp_ConfigPtr->mainFunctionPeriod;
            }

            CANTP_CRITICAL_SECTION(
                {
                    CanTp_Rt->sdu[idx] = n_sdu;
                })
        }
    }
}

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* global callback function definitions.                                                         */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_GCFDEF
 * @{
 */

void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo)
{
    CanTp_NPciType n_pci_type;
    CanTp_FlowStatusType fs;
    uint8_least bs;
    uint8_least st_min;
    CanTp_NSduType n_sdu;
    CanTp_NSduType *p_n_sdu = NULL_PTR;

    CANTP_DET_ASSERT_ERROR(pPduInfo == NULL_PTR,
                           0x00u,
                           CANTP_RX_INDICATION_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return)

    if (pPduInfo->SduLength != 0)
    {
        if (CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == E_OK)
        {
            CANTP_CRITICAL_SECTION(n_sdu = *p_n_sdu;)

            n_pci_type = (CanTp_NPciType)(uint8)(pPduInfo->SduDataPtr[0x00u] >> 0x04u) & 0x0Fu;

            switch (n_pci_type)
            {
                case CANTP_N_PCI_TYPE_FC:
                {
                    fs = (CanTp_FlowStatusType)pPduInfo->SduDataPtr[0x00u] & 0x0Fu;
                    bs = pPduInfo->SduDataPtr[0x01u];
                    st_min = pPduInfo->SduDataPtr[0x02u];

                    /* SWS_CanTp_00315: the CanTp module shall start a timeout observation for N_Bs
                     * time at confirmation of the FF transmission, last CF of a block transmission
                     * and at each indication of FC with FS=WT (i.e. time until reception of the
                     * next FC). */
                    if (fs == CANTP_FLOW_STATUS_TYPE_WT)
                    {
                        n_sdu.timeout.tx.currentBs = 0x00u;
                    }

                    n_sdu.fs = fs;
                    n_sdu.currentBlockSize = 0x00u;
                    n_sdu.targetBlockSize = bs;
                    n_sdu.timeout.tx.targetStMin = CanTp_DecodeSTMinValue(st_min);
                    n_sdu.timeout.tx.currentCs = 0x00u;

                    /* we might initialize the consecutive frame here, but as this function might
                     * be called from interrupt context, we should keep the function as short as
                     * possible, that's why it is handled in CanTp_MainFunction. */
                    n_sdu.flag |= CANTP_FLAG_COPY_DATA;

                    n_sdu.state = CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION;

                    break;
                }
                default:
                {
                    break;
                }
            }

            CANTP_CRITICAL_SECTION(*p_n_sdu = n_sdu;)
        }
    }
}

void CanTp_TxConfirmation(PduIdType txPduId, Std_ReturnType result)
{
    CanTp_NSduType *p_n_sdu = &CanTp_Rt->sdu[txPduId];

    if (result == E_OK)
    {
        if (p_n_sdu->state == CANTP_FRAME_STATE_WAIT_SF_TX_CONFIRMATION)
        {
            if (p_n_sdu->pci != CANTP_N_PCI_TYPE_SF)
            {
                /* TODO: unexpected frame received, check behavior to adopt. */
            }

            p_n_sdu->taskState.tx = CANTP_WAIT;
        }
        else
        {
            if ((p_n_sdu->state == CANTP_FRAME_STATE_WAIT_FF_TX_CONFIRMATION) ||
                (p_n_sdu->state == CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION))
            {
                /* SWS_CanTp_00315: the CanTp module shall start a timeout observation for N_Bs
                 * time at confirmation of the FF transmission, last CF of a block transmission and
                 * at each indication of FC with FS=WT (i.e. time until reception of the next FC).
                 */
                p_n_sdu->timeout.tx.currentBs = 0x00u;
            }

            if (p_n_sdu->state == CANTP_FRAME_STATE_WAIT_SF_TX_CONFIRMATION)
            {
                if (p_n_sdu->pci != CANTP_N_PCI_TYPE_SF)
                {
                    /* TODO: unexpected frame received, check behavior to adopt. */
                }

                p_n_sdu->taskState.tx = CANTP_WAIT;
            }
            else if (p_n_sdu->state == CANTP_FRAME_STATE_WAIT_FF_TX_CONFIRMATION)
            {
                p_n_sdu->state = CANTP_FRAME_STATE_WAIT_FC_RX_INDICATION;
            }
            else if (p_n_sdu->state == CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION)
            {
                /* ISO15765: the measurement of the STmin starts after completion of transmission of
                 * a ConsecutiveFrame (CF) and ends at the request for the transmission of the next
                 * CF. */
                p_n_sdu->timeout.tx.currentStMin = 0x00u;

                if (p_n_sdu->buf.tx.size > p_n_sdu->buf.tx.sent)
                {
                    if (p_n_sdu->currentBlockSize < p_n_sdu->targetBlockSize)
                    {
                        p_n_sdu->flag |= CANTP_FLAG_COPY_DATA;
                        p_n_sdu->state = CANTP_FRAME_STATE_WAIT_STMIN_TIMEOUT;
                    }
                    else
                    {
                        p_n_sdu->state = CANTP_FRAME_STATE_WAIT_FC_RX_INDICATION;
                    }
                }
                else
                {
                    p_n_sdu->state = CANTP_FRAME_STATE_TX_OK;
                }
            }
            else
            {
                /* MISRA C, do nothing. */
            }
        }
    }
    else
    {
        /* SWS_CanTp_00355: CanTp shall abort the corresponding session, when CanTp_TxConfirmation()
         * is called with the result E_NOT_OK. */
        CanTp_AbortSession(p_n_sdu);
    }
}

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local function definitions (static).                                                          */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LFDEF
 * @{
 */

static Std_ReturnType CanTp_GetNSduFromPduId(PduIdType pduId, CanTp_NSduType **pNSdu)
{
    Std_ReturnType tmp_return = E_NOT_OK;
    CanTp_NSduType *p_n_sdu;

    if (pduId < (sizeof(CanTp_Rt->sdu) / sizeof(CanTp_Rt->sdu[0x00u])))
    {
        p_n_sdu = &CanTp_Rt->sdu[pduId];

        if (p_n_sdu != NULL_PTR)
        {
            *pNSdu = p_n_sdu;
            tmp_return = E_OK;
        }
    }

    return tmp_return;
}

static uint32_least CanTp_DecodeSTMinValue(uint8 rawValue)
{
    uint32_least result;

    /* ISO15765: the units of STmin in the range 00 hex – 7F hex are absolute milliseconds (ms). */
    if ((0x00u <= rawValue) && (rawValue <= 0x7Fu))
    {
        result = CANTP_MS_TO_INTERNAL(rawValue);
    }
        /* ISO15765: the units of STmin in the range F1 hex – F9 hex are even 100 microseconds (μs),
         * where parameter value F1 hex represents 100 μs and parameter value F9 hex represents 900 μs.
         */
    else if ((0xF1u <= rawValue) && (rawValue <= 0xF9u))
    {
        result = (rawValue & 0x0Fu) * 100u;
    }
        /* ISO15765: if an FC N_PDU message is received with a reserved ST parameter value, then the
         * sending network entity shall use the longest ST value specified by this part of ISO 15765
         * (7F hex – 127 ms) instead of the value received from the receiving network entity for the
         * duration of the ongoing segmented message transmission. */
    else
    {
        result = CANTP_MS_TO_INTERNAL(0x7Fu);
    }

    return result;
}

static uint8 CanTp_EncodeSTMinValue(uint32 value)
{
    uint8 result;

    if ((0x00u <= CANTP_INTERNAL_TO_MS(value)) && (CANTP_INTERNAL_TO_MS(value) <= 0x7Fu))
    {
        result = CANTP_INTERNAL_TO_MS(value);
    }
    else if ((value == 100u) ||
             (value == 200u) ||
             (value == 300u) ||
             (value == 400u) ||
             (value == 500u) ||
             (value == 600u) ||
             (value == 700u) ||
             (value == 800u) ||
             (value == 900u))
    {
        result = (0xF0u | (value / 100u));
    }
    else
    {
        result = 0x7Fu;
    }

    return result;
}

static CanTp_NPciType CanTp_GetPCIType(CanTp_NSduType *pNSdu)
{
    CanTp_NPciType n_pci;
    CanTp_AddressingFormatType af = pNSdu->cfg.tx->af;
    const uint16_least ps = pNSdu->buf.tx.size;

    if (((af == CANTP_STANDARD || af == CANTP_NORMALFIXED) && ps <= 0x07u) ||
        ((af == CANTP_EXTENDED || af == CANTP_MIXED || af == CANTP_MIXED29BIT) && ps <= 0x06u))
    {
        n_pci = CANTP_N_PCI_TYPE_SF;
    }
    else
    {
        n_pci = CANTP_N_PCI_TYPE_FF;
    }

    return n_pci;
}

static void CanTp_AbortSession(CanTp_NSduType *pNSdu)
{
    pNSdu->taskState.rx = CANTP_WAIT;
    pNSdu->taskState.tx = CANTP_WAIT;
}

static boolean CanTp_GetNextTxFrame(CanTp_NSduType *pNSdu)
{
    boolean send_data = FALSE;
    CanTp_NSduType *p_n_sdu = pNSdu;

    switch (p_n_sdu->state)
    {
        case CANTP_FRAME_STATE_WAIT_SF_TX_CONFIRMATION:
        case CANTP_FRAME_STATE_WAIT_FF_TX_CONFIRMATION:
        {
            /* the bellow code will lead to a direct call of CanIf_Transmit. that's why we clear
             * the N_As timeout. */
            if ((p_n_sdu->flag & CANTP_FLAG_SEND_DATA) != 0x00u)
            {
                p_n_sdu->flag &= ~(CANTP_FLAG_SEND_DATA);
                p_n_sdu->timeout.tx.currentAs = 0x00u;
                send_data = TRUE;
            }
                /* SWS_CanTp_00310: in case of N_As timeout occurrence (no confirmation from CAN driver)
                 * the CanTp module shall notify the upper layer by calling the callback function
                 * PduR_CanTpTxConfirmation() with the result E_NOT_OK. */
            else if (p_n_sdu->timeout.tx.currentAs >= pNSdu->cfg.tx->nas)
            {
                CanTp_AbortSession(p_n_sdu);
                PduR_CanTpTxConfirmation(pNSdu->cfg.tx->nSduId, E_NOT_OK);

                /* SWS_CanTp_00229 if the task was aborted due to As, Bs, Cs, Ar, Br, Cr timeout,
                 * the CanTp module shall raise the DET error CANTP_E_RX_COM (in case of a reception
                 * operation) or CANTP_E_TX_COM (in case of a transmission operation). If the task
                 * was aborted due to any other protocol error, the CanTp module shall raise the
                 * runtime error code CANTP_E_COM to the Default Error Tracer. */
                CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, 0x00u, CANTP_E_TX_COM)
            }

            break;
        }
        case CANTP_FRAME_STATE_WAIT_FC_RX_INDICATION:
        {
            /* SWS_CanTp_00316: in case of N_Bs timeout occurrence the CanTp module shall abort
             * transmission of this message and notify the upper layer by calling the callback
             * function PduR_CanTpTxConfirmation() with the result E_NOT_OK. */
            if (p_n_sdu->timeout.tx.currentBs >= pNSdu->cfg.tx->nbs)
            {
                CanTp_AbortSession(p_n_sdu);
                PduR_CanTpTxConfirmation(pNSdu->cfg.tx->nSduId, E_NOT_OK);

                CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, 0x00u, CANTP_E_TX_COM)
            }

            break;
        }
        case CANTP_FRAME_STATE_WAIT_STMIN_TIMEOUT:
        {
            if (p_n_sdu->timeout.tx.currentStMin < p_n_sdu->timeout.tx.targetStMin)
            {
                break;
            }
            else
            {
                p_n_sdu->state = CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION;
            }
        }
        case CANTP_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
        {
            /* check if data have been copied. */
            if ((p_n_sdu->flag & CANTP_FLAG_COPY_DATA) != 0x00u)
            {
                if (CanTp_LDataRequest(p_n_sdu, CanTp_InitCFTx) == BUFREQ_OK)
                {
                    /* data successfully copied. clear the copy flag and clear N_As timeout. */
                    p_n_sdu->flag &= ~(CANTP_FLAG_COPY_DATA);
                    p_n_sdu->timeout.tx.currentAs = 0x00u;

                    send_data = TRUE;
                }
                else
                {
                    /* SWS_CanTp_00280: if data is not available within N_Cs timeout the CanTp
                     * module shall notify the upper layer of this failure by calling the callback
                     * function PduR_CanTpTxConfirmation with the result E_NOT_OK. */
                    if (p_n_sdu->timeout.tx.currentCs >= pNSdu->cfg.tx->ncs)
                    {
                        CanTp_AbortSession(p_n_sdu);
                        PduR_CanTpTxConfirmation(p_n_sdu->cfg.tx->nSduId, E_NOT_OK);

                        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, 0x00u, CANTP_E_TX_COM)
                    }
                }
            }
            else
            {
                if (p_n_sdu->timeout.tx.currentAs >= pNSdu->cfg.tx->nas)
                {
                    CanTp_AbortSession(p_n_sdu);
                    PduR_CanTpTxConfirmation(p_n_sdu->cfg.tx->nSduId, E_NOT_OK);

                    CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, 0x00u, CANTP_E_TX_COM)
                }
            }

            break;
        }
        case CANTP_FRAME_STATE_TX_OK:
        {
            /* SWS_CanTp_00090: when the transport transmission session is successfully completed,
             * the CanTp module shall call a notification service of the upper layer,
             * PduR_CanTpTxConfirmation(), with the result E_OK. */
            PduR_CanTpTxConfirmation(p_n_sdu->cfg.tx->nSduId, E_OK);

            break;
        }
        default:
        {
            break;
        }
    }

    return send_data;
}

static void CanTp_FillAIField(CanTp_NSduType *pNSdu, PduLengthType *pOfs)
{
    PduLengthType ofs = *pOfs;
    CanTp_NSduType *p_n_sdu = pNSdu;
    CanTp_AddressingFormatType af = p_n_sdu->cfg.tx->af;

    /* TODO: fill PDU meta data. */

    /* SWS_CanTp_00334: when CanTp_Transmit is called for an N-SDU with meta data, the CanTp module
     * shall store the addressing information contained in the meta data of the N-SDU and use this
     * information for transmission of SF, FF, and CF N-PDUs and for identification of FC N-PDUs. */
    switch (af)
    {
        case CANTP_EXTENDED:
        {
            if (p_n_sdu->metaData == TRUE)
            {
                p_n_sdu->buf.tx.can[ofs++] = p_n_sdu->nTa;
            }
            else
            {
                p_n_sdu->buf.tx.can[ofs++] = p_n_sdu->cfg.tx->pNTa->nTa;
            }

            break;
        }
        case CANTP_MIXED:
        case CANTP_MIXED29BIT:
        {
            if (p_n_sdu->metaData == TRUE)
            {
                p_n_sdu->buf.tx.can[ofs++] = p_n_sdu->nAe;
            }
            else
            {
                p_n_sdu->buf.tx.can[ofs++] = p_n_sdu->cfg.tx->pNAe->nAe;
            }

            break;
        }
        case CANTP_STANDARD:
        case CANTP_NORMALFIXED:
        default:
        {
            break;
        }
    }

    *pOfs = ofs;
}

static void CanTp_FillPCIField(CanTp_NSduType *pNSdu, CanTp_NPciType nPciType, PduLengthType *pOfs)
{
    PduLengthType ofs = *pOfs;

    switch (nPciType)
    {
        case CANTP_N_PCI_TYPE_SF:
        {
            pNSdu->pci = nPciType;
            pNSdu->buf.tx.can[ofs] = ((uint8)nPciType << 0x04u);
            pNSdu->buf.tx.can[ofs] |= pNSdu->buf.tx.size;
            ofs = ofs + 0x01u;

            break;
        }
        case CANTP_N_PCI_TYPE_FF:
        {
            pNSdu->pci = nPciType;
            pNSdu->buf.tx.can[ofs] = ((uint8)nPciType << 0x04u);
            pNSdu->buf.tx.can[ofs] |= ((pNSdu->buf.tx.size & 0x0F00u) >> 0x08u);
            pNSdu->buf.tx.can[ofs + 0x01u] = pNSdu->buf.tx.size & 0xFFu;
            ofs = ofs + 0x02u;

            break;
        }
        case CANTP_N_PCI_TYPE_CF:
        {
            pNSdu->pci = nPciType;
            pNSdu->buf.tx.can[ofs] = ((uint8)nPciType << 0x04u);
            pNSdu->buf.tx.can[ofs] |= (pNSdu->sn & 0x0Fu);
            ofs = ofs + 0x01u;

            break;
        }
        case CANTP_N_PCI_TYPE_FC:
        {
            pNSdu->pci = nPciType;
            pNSdu->buf.tx.can[ofs] = ((uint8)nPciType << 0x04u);

            switch (pNSdu->fs)
            {
                case CANTP_FLOW_STATUS_TYPE_CTS:
                case CANTP_FLOW_STATUS_TYPE_OVFLW:
                case CANTP_FLOW_STATUS_TYPE_WT:
                {
                    pNSdu->buf.tx.can[ofs] |= ((uint8)pNSdu->fs & 0x0Fu);
                    pNSdu->buf.tx.can[ofs + 0x01u] = pNSdu->targetBlockSize;
                    pNSdu->buf.tx.can[ofs + 0x02u] = pNSdu->timeout.tx.targetStMin;
                    ofs += 0x03u;

                    break;
                }
                default:
                {
                    break;
                }
            }

            break;
        }
        default:
        {
            break;
        }
    }

    *pOfs = ofs;
}

static BufReq_ReturnType CanTp_FillTxPayload(CanTp_NSduType *pNSdu, PduLengthType *pOfs)
{
    BufReq_ReturnType tmp_return;
    PduInfoType tmp_pdu;

    PduLengthType ofs = *pOfs;
    CanTp_NSduType *p_n_sdu = pNSdu;
    tmp_pdu.SduDataPtr = &p_n_sdu->buf.tx.can[ofs];

    if ((p_n_sdu->buf.tx.size - p_n_sdu->buf.tx.sent) <= CANTP_CAN_FRAME_SIZE - ofs)
    {
        tmp_pdu.SduLength = p_n_sdu->buf.tx.size - p_n_sdu->buf.tx.sent;
    }
    else
    {
        tmp_pdu.SduLength = CANTP_CAN_FRAME_SIZE - ofs;
    }

    /* TODO: use correct PDU ID. */
    /* SWS_CanTp_00272: the API PduR_CanTpCopyTxData() contains a parameter used for the recovery
     * mechanism – ‘retry’. Because ISO 15765-2 does not support such a mechanism, the CAN Transport
     * Layer does not implement any kind of recovery. Thus, the parameter is always set to NULL
     * pointer. */
    tmp_return = PduR_CanTpCopyTxData(0x01u, &tmp_pdu, NULL_PTR, &p_n_sdu->buf.tx.remaining);

    switch (tmp_return)
    {
        case BUFREQ_OK:
        {
            ofs += tmp_pdu.SduLength;
            p_n_sdu->buf.tx.sent += tmp_pdu.SduLength;

            *pOfs = ofs;

            break;
        }
        case BUFREQ_E_BUSY:
        {
            /* TODO: add retry strategy. */
            break;
        }
        case BUFREQ_E_NOT_OK:
        {
            /* SWS_CanTp_00087: if PduR_CanTpCopyTxData() returns BUFREQ_E_NOT_OK, the CanTp module
             * shall abort the transmit request and notify the upper layer of this failure by
             * calling the callback function PduR_CanTpTxConfirmation() with the result E_NOT_OK. */
            CanTp_AbortSession(p_n_sdu);
            PduR_CanTpTxConfirmation(p_n_sdu->cfg.tx->nSduId, E_NOT_OK);

            break;
        }
        case BUFREQ_E_OVFL:
        default:
        {
            break;
        }
    }

    return tmp_return;
}

static void CanTp_FillPadding(CanTp_NSduType *pNSdu, PduLengthType *pOfs)
{
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduLengthType ofs = *pOfs;

    /* SWS_CanTp_00348: if frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD
     * frames) are used for a Tx N-SDU and if CanTpTxPaddingActivation is equal to CANTP_ON,
     * CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU or last CF Tx
     * N-PDU that belongs to that Tx N-SDU with the length of eight bytes(i.e.
     * PduInfoPtr.SduLength = 8). Unused bytes in N-PDU shall be updated with
     * CANTP_PADDING_BYTE (see ECUC_CanTp_00298). */
    if (p_n_sdu->cfg.tx->padding == CANTP_ON)
    {
        for (; ofs < CANTP_CAN_FRAME_SIZE; ofs++)
        {
            p_n_sdu->buf.tx.can[ofs] = CANTP_PADDING_BYTE;
        }
    }

    *pOfs = ofs;
}

static BufReq_ReturnType CanTp_InitSFTx(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->pduInfo;
    PduLengthType ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_SF;

    CanTp_FillAIField(p_n_sdu, &ofs);
    CanTp_FillPCIField(p_n_sdu, p_n_sdu->pci, &ofs);
    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        CanTp_FillPadding(p_n_sdu, &ofs);
        p_pdu_info->SduDataPtr = &p_n_sdu->buf.tx.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_InitFFTx(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->pduInfo;
    PduLengthType ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_FF;
    p_n_sdu->sn = 0x00u;

    CanTp_FillAIField(p_n_sdu, &ofs);
    CanTp_FillPCIField(p_n_sdu, p_n_sdu->pci, &ofs);
    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        CanTp_FillPadding(p_n_sdu, &ofs);
        p_pdu_info->SduDataPtr = &p_n_sdu->buf.tx.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_InitCFTx(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->pduInfo;
    PduLengthType ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_CF;
    p_n_sdu->sn++;
    p_n_sdu->currentBlockSize++;

    CanTp_FillAIField(p_n_sdu, &ofs);
    CanTp_FillPCIField(p_n_sdu, p_n_sdu->pci, &ofs);
    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        CanTp_FillPadding(p_n_sdu, &ofs);
        p_pdu_info->SduDataPtr = &p_n_sdu->buf.tx.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_InitFCTx(CanTp_NSduType *pNSdu)
{

    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->pduInfo;
    uint16_least ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_FC;

    CanTp_FillAIField(p_n_sdu, &ofs);
    CanTp_FillPCIField(p_n_sdu, p_n_sdu->pci, &ofs);
    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        CanTp_FillPadding(p_n_sdu, &ofs);
        p_pdu_info->SduDataPtr = &p_n_sdu->buf.tx.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_LDataRequest(CanTp_NSduType *pNSdu,
                                            BufReq_ReturnType (*pFunc)(CanTp_NSduType *))
{
    BufReq_ReturnType tmp_return = BUFREQ_E_NOT_OK;

    if (pFunc != NULL_PTR)
    {
        /* ISO15765: N_As starts at L_Data.request and ends at L_Data.confirm. */
        //pNSdu->timeout.tx.currentAs = 0x00u;

        tmp_return = pFunc(pNSdu);
    }

    return tmp_return;
}

/** @} */

#ifdef __cplusplus

}

#endif /* ifdef __cplusplus */
