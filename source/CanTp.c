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

#define CANTP_FLAG_SEND_RX_DATA (0x01u << 0x07u)

#define CANTP_FLAG_SEND_TX_DATA (0x01u << 0x08u)

#define CANTP_FLAG_COPY_RX_DATA (0x01u << 0x09u)

#define CANTP_FLAG_FIRST_CF (0x01u << 0x0Bu)

#define CANTP_FLAG_LAST_CF (0x01u << 0x0Cu)

#define CANTP_FLAG_SKIP_BS (0x01u << 0x0Du)

#define CANTP_MS_TO_INTERNAL(timeout) (timeout * 1000u)

#define CANTP_INTERNAL_TO_MS(timeout) (timeout / 1000u)

#define CANTP_US_TO_INTERNAL(timeout) (timeout)

#define CANTP_DIRECTION_RX (0x01u)

#define CANTP_DIRECTION_TX (0x02u)

#define CANTP_DIRECTION_RX_TX (CANTP_DIRECTION_RX | CANTP_DIRECTION_TX)

#define ISO15765_DIR_RX (0x00u)

#define ISO15765_DIR_TX (0x01u)

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
    CANTP_N_PCI_TYPE_SF = 0x00u,
    CANTP_N_PCI_TYPE_FF = 0x01u,
    CANTP_N_PCI_TYPE_CF = 0x02u,
    CANTP_N_PCI_TYPE_FC = 0x03u
} CanTp_NPciType;

typedef enum
{
    CANTP_FLOW_STATUS_TYPE_CTS = 0x00u,
    CANTP_FLOW_STATUS_TYPE_WT = 0x01u,
    CANTP_FLOW_STATUS_TYPE_OVFLW = 0x02u,
} CanTp_FlowStatusType;

typedef enum {
    CANTP_FRAME_STATE_INVALID = 0x00u,
    CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION,
    CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION,
    CANTP_TX_FRAME_STATE_WAIT_SF_TX_REQUEST,
    CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION,
    CANTP_TX_FRAME_STATE_WAIT_FF_TX_REQUEST,
    CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION,
    CANTP_TX_FRAME_STATE_WAIT_CF_TX_REQUEST,
    CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION,
    CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION,
    CANTP_FRAME_STATE_OK
} CanTp_FrameStateType;

typedef enum
{
    CANTP_WAIT = 0x00u,
    CANTP_PROCESSING
} CanTp_TaskStateType;

typedef struct
{
    uint8 can[CANTP_CAN_FRAME_SIZE];
    uint32 size;
    uint32 done;
    PduLengthType rmng;
} CanTp_NSduBufferType;

typedef struct
{
    const CanTp_RxNSduType *cfg;
    CanTp_NSduBufferType buf;
    CanTp_FrameStateType state;
    uint32 st_min;
    uint8 bs;
    uint8 sn;
    uint8 wft_max;
    uint8 meta_data[0x04u];
    PduInfoType pdu_info;
    struct
    {
        uint32 flag;
        CanTp_TaskStateType taskState;

        /**
         * @brief structure containing all parameters accessible via @ref CanTp_ReadParameter/@ref
         * CanTp_ChangeParameter.
         */
        struct {
            uint32 st_min;
            uint8 bs;
        } m_param;
    } shared;
} CanTp_RxConnectionType;

typedef struct
{
    const CanTp_TxNSduType *cfg;
    CanTp_NSduBufferType buf;
    CanTp_FrameStateType state;
    uint32 target_st_min;
    uint32 st_min;
    uint8 bs;
    uint8 sn;
    uint8 meta_data[0x04u];
    PduInfoType pdu_info;
    CanTp_TaskStateType taskState;
    struct
    {
        uint32 flag;
    } shared;
} CanTp_TxConnectionType;

typedef struct
{
    CanTp_RxConnectionType rx;
    CanTp_TxConnectionType tx;
    uint32 n[0x06u];
    CanTp_NPciType pci;
    uint8 n_sa;
    uint8 n_ta;
    uint8 n_ae;
    CanTp_FlowStatusType fs;
    boolean has_meta_data;
    uint8_least dir;
    uint32 t_flag;
} CanTp_NSduType;

typedef struct
{
    CanTp_NSduType sdu[CANTP_MAX_NUM_OF_N_SDU];
} CanTp_ChannelRtType;

typedef struct {
    BufReq_ReturnType (*const req[2][4])(CanTp_NSduType *pNSdu);
    CanTp_FrameStateType (*const ind[2][4])(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);
    CanTp_FrameStateType (*const con[2][4])(CanTp_NSduType *pNSdu);
} CanTp_ISO15765Type;

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
    if(condition) \
    { \
        (void)Det_ReportError(CANTP_MODULE_ID, instanceId, apiId, errorId); \
        __VA_ARGS__; \
    }

#define CANTP_DET_ASSERT_RUNTIME_ERROR(condition, instanceId, apiId, errorId, ...) \
    if(condition) \
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
 * @param data [in]: the raw minimum separation time (8 bits STmin value)
 * @return decoded minimum separation time value [μs]
 */
static uint32_least CanTp_DecodeSTMinValue(const uint8 data);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static Std_ReturnType CanTp_DecodePCIValue(CanTp_NPciType *pPci, const uint8 *pData);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static Std_ReturnType CanTp_DecodeSNValue(uint8 *pSn, const uint8 *pData);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static Std_ReturnType CanTp_DecodeDLValue(uint16 *pDl, const uint8 *pData);

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
static uint8 CanTp_EncodeSTMinValue(uint16 value);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_AbortTxSession(CanTp_NSduType *pNSdu, const uint8 instanceId, boolean confirm);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static CanTp_NPciType CanTp_EncodePCIValue(CanTp_AddressingFormatType af, uint16 ps);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_PerformStepRx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_PerformStepTx(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

//static void CanTp_FillAIField(CanTp_AddressingFormatType af,
//                              uint8 n_sa,
//                              uint8 n_ta,
//                              uint8 n_ae,
//                              uint8 *pBuffer,
//                              PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_FillRxPayload(CanTp_NSduType *pNSdu);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_FillTxPayload(CanTp_NSduType *pNSdu, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

#define CanTp_START_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static void CanTp_FillPadding(uint8 *pBuffer, PduLengthType *pOfs);

#define CanTp_STOP_SEC_CODE_FAST
#include "CanTp_MemMap.h"

static BufReq_ReturnType CanTp_LDataReqTSF(CanTp_NSduType *pNSdu);

static BufReq_ReturnType CanTp_LDataReqTFF(CanTp_NSduType *pNSdu);

static BufReq_ReturnType CanTp_LDataReqTCF(CanTp_NSduType *pNSdu);

static BufReq_ReturnType CanTp_LDataReqRFC(CanTp_NSduType *pNSdu);

static CanTp_FrameStateType CanTp_LDataIndRSF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);

static CanTp_FrameStateType CanTp_LDataIndRFF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);

static CanTp_FrameStateType CanTp_LDataIndRCF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);

static CanTp_FrameStateType CanTp_LDataIndTFC(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);

static CanTp_FrameStateType CanTp_LDataConRFC(CanTp_NSduType *pNSdu);

static CanTp_FrameStateType CanTp_LDataConTSF(CanTp_NSduType *pNSdu);

static CanTp_FrameStateType CanTp_LDataConTFF(CanTp_NSduType *pNSdu);

static CanTp_FrameStateType CanTp_LDataConTCF(CanTp_NSduType *pNSdu);

/** @} */


/*-----------------------------------------------------------------------------------------------*/
/* local constant definitions (static const).                                                    */
/*-----------------------------------------------------------------------------------------------*/

/**
 * @addtogroup CANTP_C_LCDEF
 * @{
 */

static const CanTp_ISO15765Type ISO15765 = {
    {
        {
            NULL_PTR,
            NULL_PTR,
            NULL_PTR,
            CanTp_LDataReqRFC
        },
        {
            CanTp_LDataReqTSF,
            CanTp_LDataReqTFF,
            CanTp_LDataReqTCF,
            NULL_PTR
        }
    },
    {
        {
            CanTp_LDataIndRSF,
            CanTp_LDataIndRFF,
            CanTp_LDataIndRCF,
            NULL_PTR
        },
        {
            NULL_PTR,
            NULL_PTR,
            NULL_PTR,
            CanTp_LDataIndTFC
        }
    },
    {
        {
            NULL_PTR,
            NULL_PTR,
            NULL_PTR,
            CanTp_LDataConRFC
        },
        {
            CanTp_LDataConTSF,
            CanTp_LDataConTFF,
            CanTp_LDataConTCF,
            NULL_PTR
        }
    }
};

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
        uint8 *p_cleared_data = (uint8 *)&CanTp_Rt[0x00u];
        uint32_least idx;

        for (idx = 0x00u; idx < sizeof(CanTp_Rt); idx++)
        {
            p_cleared_data[idx] = 0x00u;
        }
        /* iterate over all statically defined channels. */
        for (channel_idx = 0x00u; channel_idx < pConfig->maxChannelCnt; channel_idx++)
        {
            p_rt_channel = &CanTp_Rt[channel_idx];
            p_cfg_channel = &pConfig->pChannel[channel_idx];

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

                                    p_rt_sdu->dir |= CANTP_DIRECTION_RX;
                                    p_rt_sdu->rx.cfg = p_cfg_rx_sdu;
                                    p_rt_sdu->rx.shared.taskState = CANTP_WAIT;
                                    p_rt_sdu->rx.shared.m_param.st_min = p_cfg_rx_sdu->sTMin;
                                    p_rt_sdu->rx.shared.m_param.bs = p_cfg_rx_sdu->bs;
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

                                    p_rt_sdu->dir |= CANTP_DIRECTION_TX;
                                    p_rt_sdu->tx.cfg = p_cfg_tx_sdu;
                                    p_rt_sdu->tx.taskState = CANTP_WAIT;
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
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, CANTP_INIT_API_ID, CANTP_E_INIT_FAILED)
    }
    else
    {
        CanTp_State = CANTP_ON;
    }
}

void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo)
{
    CANTP_DET_ASSERT_ERROR(pVersionInfo == NULL_PTR,
                           0x00u,
                           CANTP_GET_VERSION_INFO_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return)

    pVersionInfo->vendorID = 0x00u;
    pVersionInfo->moduleID = (uint16)CANTP_MODULE_ID;
    pVersionInfo->sw_major_version = CANTP_SW_MAJOR_VERSION;
    pVersionInfo->sw_minor_version = CANTP_SW_MINOR_VERSION;
    pVersionInfo->sw_patch_version = CANTP_SW_PATCH_VERSION;
}

void CanTp_Shutdown(void)
{
    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_SHUTDOWN_API_ID,
                           CANTP_E_UNINIT,
                           return)

    CanTp_State = CANTP_OFF;
}

Std_ReturnType CanTp_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo)
{
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
        /* SWS_CanTp_00206: the function CanTp_Transmit shall reject a request if the CanTp_Transmit
         * service is called for a N-SDU identifier which is being used in a currently running CAN
         * Transport Layer session. */
        if ((p_n_sdu->tx.taskState != CANTP_PROCESSING) &&
            (pPduInfo->SduLength > 0x0000u) &&
            (pPduInfo->SduLength <= 0x0FFFu))
        {
            p_n_sdu->tx.buf.size = pPduInfo->SduLength;
            p_n_sdu->tx.buf.done = 0x00u;

            if (pPduInfo->MetaDataPtr != NULL_PTR)
            {
                p_n_sdu->has_meta_data = TRUE;

                switch (p_n_sdu->tx.cfg->af)
                {
                    case CANTP_NORMALFIXED:
                    {
                        p_n_sdu->n_sa = pPduInfo->MetaDataPtr[0x00u];
                        p_n_sdu->n_ta = pPduInfo->MetaDataPtr[0x01u];

                        break;
                    }
                    case CANTP_MIXED:
                    {
                        p_n_sdu->n_ae = pPduInfo->MetaDataPtr[0x00u];

                        break;
                    }
                    case CANTP_MIXED29BIT:
                    {
                        p_n_sdu->n_sa = pPduInfo->MetaDataPtr[0x00u];
                        p_n_sdu->n_ta = pPduInfo->MetaDataPtr[0x01u];
                        p_n_sdu->n_ae = pPduInfo->MetaDataPtr[0x02u];

                        break;
                    }
                    case CANTP_EXTENDED:
                    {
                        p_n_sdu->n_ta = pPduInfo->MetaDataPtr[0x00u];

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
                p_n_sdu->has_meta_data = FALSE;
            }

            switch (CanTp_EncodePCIValue(p_n_sdu->tx.cfg->af, p_n_sdu->tx.buf.size))
            {
                case CANTP_N_PCI_TYPE_SF:
                {
                    p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_SF_TX_REQUEST;
                    tmp_return = E_OK;

                    break;
                }
                case CANTP_N_PCI_TYPE_FF:
                {
                    p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_FF_TX_REQUEST;
                    tmp_return = E_OK;

                    break;
                }
                default:
                {
                    break;
                }
            }

            if (tmp_return == E_OK)
            {
                p_n_sdu->tx.taskState = CANTP_PROCESSING;
            }
        }
    }

    return tmp_return;
}

Std_ReturnType CanTp_CancelTransmit(PduIdType txPduId)
{
    CanTp_NSduType *p_n_sdu;
    const uint8 api_id = CANTP_CANCEL_TRANSMIT_API_ID;
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           api_id,
                           CANTP_E_UNINIT,
                           return tmp_return)

    if ((CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == E_OK) &&
        ((p_n_sdu->dir & CANTP_DIRECTION_TX) != 0x00u))
    {
        if (p_n_sdu->tx.taskState == CANTP_PROCESSING)
        {
            p_n_sdu->tx.taskState = CANTP_WAIT;

            /* SWS_CanTp_00255: If the CanTp_CancelTransmit service has been successfully executed
             * the CanTp shall call the PduR_CanTpTxConfirmation with notification result E_NOT_OK.
             */
            PduR_CanTpTxConfirmation(p_n_sdu->tx.cfg->nSduId, E_NOT_OK);

            tmp_return = E_OK;
        }
        else
        {
            /* SWS_CanTp_00254: if development error detection is enabled the function
             * CanTp_CancelTransmit shall check the validity of TxPduId parameter. If the parameter
             * value is invalid, the CanTp_CancelTransmit function shall raise the development error
             * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
             * if the parameter value indicates a cancel transmission request for an N-SDU that it
             * is not on transmission process the CanTp module shall report a runtime error code
             * CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the service shall return
             * E_NOT_OK. */
            CANTP_DET_ASSERT_RUNTIME_ERROR(TRUE, 0x00u, api_id, CANTP_E_OPER_NOT_SUPPORTED)
        }
    }
    else
    {
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
    }

    return tmp_return;
}

Std_ReturnType CanTp_CancelReceive(PduIdType rxPduId)
{
    CanTp_NSduType *p_n_sdu;
    CanTp_TaskStateType task_state;
    const uint8 api_id = CANTP_CANCEL_RECEIVE_API_ID;
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           api_id,
                           CANTP_E_UNINIT,
                           return tmp_return)

    if ((CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == E_OK) &&
        ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u))
    {
        CANTP_CRITICAL_SECTION(task_state = p_n_sdu->rx.shared.taskState;)

        if (task_state == CANTP_PROCESSING)
        {
            /* SWS_CanTp_00262: The CanTp shall reject the request for receive cancellation in case
             * of a Single Frame reception or if the CanTp is in the process of receiving the last
             * Consecutive Frame of the N-SDU (i.e. the service is called after N-Cr timeout is
             * started for the last Consecutive Frame). In this case the CanTp shall return
             * E_NOT_OK. */
            if ((p_n_sdu->pci != CANTP_N_PCI_TYPE_SF) &&
                ((p_n_sdu->rx.shared.flag & CANTP_FLAG_LAST_CF) == 0x00u))
            {
                CANTP_CRITICAL_SECTION(p_n_sdu->rx.shared.taskState = CANTP_WAIT;)

                /* SWS_CanTp_00263: if the CanTp_CancelReceive service has been successfully
                 * executed the CanTp shall call the PduR_CanTpRxIndication with notification
                 * result E_NOT_OK. */
                PduR_CanTpRxIndication(p_n_sdu->rx.cfg->nSduId, E_NOT_OK);

                tmp_return = E_OK;
            }
        }
        else
        {
            /* SWS_CanTp_00254: if development error detection is enabled the function
             * CanTp_CancelTransmit shall check the validity of TxPduId parameter. If the parameter
             * value is invalid, the CanTp_CancelTransmit function shall raise the development error
             * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
             * if the parameter value indicates a cancel transmission request for an N-SDU that it
             * is not on transmission process the CanTp module shall report a runtime error code
             * CANTP_E_OPER_NOT_SUPPORTED to the Default Error Tracer and the service shall return
             * E_NOT_OK. */
            CANTP_DET_ASSERT_RUNTIME_ERROR(TRUE, 0x00u, api_id, CANTP_E_OPER_NOT_SUPPORTED)
        }
    }
    else
    {
        /* SWS_CanTp_00260: if development error detection is enabled the function
         * CanTp_CancelReceive shall check the validity of RxPduId parameter. if the parameter value
         * is invalid, the CanTp_CancelReceive function shall raise the development error
         * CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294). */
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
    }

    return tmp_return;
}

Std_ReturnType CanTp_ChangeParameter(PduIdType pduId, TPParameterType parameter, uint16 value)
{
    CanTp_NSduType *p_n_sdu;
    CanTp_TaskStateType task_state;
    const uint8 api_id = CANTP_CHANGE_PARAMETER_API_ID;
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           api_id,
                           CANTP_E_UNINIT,
                           return tmp_return)

    if (CanTp_GetNSduFromPduId(pduId, &p_n_sdu) == E_OK)
    {
        CANTP_CRITICAL_SECTION(task_state = p_n_sdu->rx.shared.taskState;)

        if (task_state != CANTP_PROCESSING)
        {
            if ((parameter == (uint16)TP_STMIN) &&
                (value <= 0xFFu) &&
                ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u))
            {
                CANTP_CRITICAL_SECTION(p_n_sdu->rx.shared.m_param.st_min = (uint32)value;)
                tmp_return = E_OK;
            }
            else if ((parameter == (uint16)TP_BS) &&
                     (value <= 0xFFu) &&
                     ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u))
            {
                CANTP_CRITICAL_SECTION(p_n_sdu->rx.shared.m_param.bs = (uint8)value);
                tmp_return = E_OK;
            }
            else
            {
                CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
            }
        }
    }
    else
    {
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
    }

    return tmp_return;
}

Std_ReturnType CanTp_ReadParameter(PduIdType pduId, TPParameterType parameter, uint16 *pValue)
{
    CanTp_NSduType *p_n_sdu;
    uint16 value;
    const uint8 api_id = CANTP_READ_PARAMETER_API_ID;
    Std_ReturnType tmp_return = E_NOT_OK;

    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           api_id,
                           CANTP_E_UNINIT,
                           return tmp_return)

    CANTP_DET_ASSERT_ERROR(pValue == NULL_PTR,
                           0x00u,
                           api_id,
                           CANTP_E_PARAM_POINTER,
                           return tmp_return)

    if (CanTp_GetNSduFromPduId(pduId, &p_n_sdu) == E_OK)
    {
        if ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u)
        {
            if (parameter == (uint16)TP_STMIN)
            {
                CANTP_CRITICAL_SECTION(value = (uint16)p_n_sdu->rx.shared.m_param.st_min;)
                *pValue = value;
                tmp_return = E_OK;
            }
            else if (parameter == (uint16)TP_BS)
            {
                CANTP_CRITICAL_SECTION(value = (uint16)p_n_sdu->rx.shared.m_param.bs;)
                *pValue = value;
                tmp_return = E_OK;
            }
            else
            {
                CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
            }
        }
    }
    else
    {
        CANTP_DET_ASSERT_ERROR(TRUE, 0x00u, api_id, CANTP_E_PARAM_ID)
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
    CANTP_DET_ASSERT_ERROR(CanTp_State == CANTP_OFF,
                           0x00u,
                           CANTP_MAIN_FUNCTION_API_ID,
                           CANTP_E_UNINIT)

    uint32 idx;
    CanTp_NSduType *p_n_sdu;

    CanTp_TaskStateType task_state_rx;
    CanTp_TaskStateType task_state_tx;

    if (CanTp_State == CANTP_ON)
    {
        for (idx = 0x00u; idx < CANTP_MAX_NUM_OF_N_SDU; idx++)
        {
            p_n_sdu = &CanTp_Rt->sdu[idx];

            CANTP_CRITICAL_SECTION(task_state_rx = p_n_sdu->rx.shared.taskState;)
            task_state_tx = p_n_sdu->tx.taskState;

            if (task_state_rx == CANTP_PROCESSING)
            {
                CanTp_PerformStepRx(p_n_sdu);
            }

            if (task_state_tx == CANTP_PROCESSING)
            {
                CanTp_PerformStepTx(p_n_sdu);
            }

            CANTP_CRITICAL_SECTION(
                {
                    p_n_sdu->n[0x00u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->n[0x01u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->n[0x02u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->n[0x03u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->n[0x04u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->n[0x05u] += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->rx.st_min += CanTp_ConfigPtr->mainFunctionPeriod;
                    p_n_sdu->tx.st_min += CanTp_ConfigPtr->mainFunctionPeriod;
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

static void CanTp_StartNetworkLayerTimeout(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
    if (instanceId < (sizeof(pNSdu->n) / sizeof(pNSdu->n[0x00u])))
    {
        if ((pNSdu->t_flag & (0x01u << instanceId)) == 0x00u)
        {
            pNSdu->t_flag |= (0x01u << instanceId);
            pNSdu->n[instanceId] = 0x00u;
        }
    }
}

static void CanTp_StopNetworkLayerTimeout(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
    if (instanceId < (sizeof(pNSdu->n) / sizeof(pNSdu->n[0x00u])))
    {
        pNSdu->t_flag &= ~(0x01u << instanceId);
    }
}

static boolean CanTp_NetworkLayerTimedOut(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
    boolean result = FALSE;

    switch (instanceId)
    {
        case CANTP_I_N_AS:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_AS] >= pNSdu->tx.cfg->nas) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_AS)) != 0x00u));
            break;
        }
        case CANTP_I_N_BS:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_BS] >= pNSdu->tx.cfg->nbs) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_BS)) != 0x00u));
            break;
        }
        case CANTP_I_N_CS:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_CS] >= pNSdu->tx.cfg->ncs) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_CS)) != 0x00u));
            break;
        }
        case CANTP_I_N_AR:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_AR] >= pNSdu->rx.cfg->nar) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_AR)) != 0x00u));
            break;
        }
        case CANTP_I_N_BR:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_BR] >= pNSdu->rx.cfg->nbr) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_BR)) != 0x00u));
            break;
        }
        case CANTP_I_N_CR:
        {
            result = (boolean)((pNSdu->n[CANTP_I_N_CR] >= pNSdu->rx.cfg->ncr) &&
                               ((pNSdu->t_flag & (0x01u << CANTP_I_N_CR)) != 0x00u));
            break;
        }
        default:
        {
            break;
        }
    }

    return result;
}

static void CanTp_StartFlowControlTimeout(CanTp_NSduType *pNSdu)
{
    if ((pNSdu->tx.shared.flag & CANTP_I_ST_MIN) == 0x00u)
    {
        pNSdu->tx.shared.flag |= CANTP_I_ST_MIN;
        pNSdu->tx.st_min = 0x00u;
    }
}

static boolean CanTp_FlowControlActive(CanTp_NSduType *pNSdu)
{
    return (boolean)((pNSdu->tx.shared.flag & CANTP_I_ST_MIN) != 0x00u);
}

static boolean CanTp_FlowControlExpired(CanTp_NSduType *pNSdu)
{
    boolean result = FALSE;

    if ((pNSdu->tx.st_min >= pNSdu->tx.target_st_min) &&
        ((pNSdu->tx.shared.flag & CANTP_I_ST_MIN) != 0x00u))
    {
        result = TRUE;
        pNSdu->tx.shared.flag &= ~(CANTP_I_ST_MIN);
    }

    return result;
}

static BufReq_ReturnType CanTp_LDataReqTSF(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->tx.pdu_info;
    PduLengthType ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_SF;

    // CanTp_FillAIField(p_n_sdu, &ofs);

    p_n_sdu->tx.buf.can[ofs] = ((uint8)CANTP_N_PCI_TYPE_SF << 0x04u);
    p_n_sdu->tx.buf.can[ofs] |= pNSdu->tx.buf.size;
    ofs = ofs + 0x01u;

    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        /* SWS_CanTp_00348: if frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD
         * frames) are used for a Tx N-SDU and if CanTpTxPaddingActivation is equal to CANTP_ON,
         * CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU or last CF Tx N-PDU
         * that belongs to that Tx N-SDU with the length of eight bytes(i.e. PduInfoPtr.SduLength =
         * 8). Unused bytes in N-PDU shall be updated with CANTP_PADDING_BYTE (see
         * ECUC_CanTp_00298). */
        if (p_n_sdu->tx.cfg->padding == CANTP_ON)
        {
            CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
        }

        p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_LDataReqTFF(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->tx.pdu_info;
    PduLengthType ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_FF;
    p_n_sdu->tx.sn = 0x00u;

    // CanTp_FillAIField(p_n_sdu, &ofs);

    p_n_sdu->tx.buf.can[ofs] = ((uint8)CANTP_N_PCI_TYPE_FF << 0x04u);
    p_n_sdu->tx.buf.can[ofs] |= ((pNSdu->tx.buf.size & 0x0F00u) >> 0x08u);
    p_n_sdu->tx.buf.can[ofs + 0x01u] = pNSdu->tx.buf.size & 0xFFu;
    ofs = ofs + 0x02u;

    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        /* SWS_CanTp_00348: if frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD
         * frames) are used for a Tx N-SDU and if CanTpTxPaddingActivation is equal to CANTP_ON,
         * CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU or last CF Tx N-PDU
         * that belongs to that Tx N-SDU with the length of eight bytes(i.e. PduInfoPtr.SduLength =
         * 8). Unused bytes in N-PDU shall be updated with CANTP_PADDING_BYTE (see
         * ECUC_CanTp_00298). */
        if (p_n_sdu->tx.cfg->padding == CANTP_ON)
        {
            CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
        }

        p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_LDataReqTCF(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType tmp_return;
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->tx.pdu_info;
    PduLengthType ofs = 0x01u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_CF;

    tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
    if (tmp_return == BUFREQ_OK)
    {
        p_n_sdu->tx.sn ++;

        // CanTp_FillAIField(p_n_sdu, &ofs);

        p_n_sdu->tx.buf.can[0x00u] = ((uint8)CANTP_N_PCI_TYPE_CF << 0x04u);
        p_n_sdu->tx.buf.can[0x00u] |= (p_n_sdu->tx.sn & 0x0Fu);

        /* SWS_CanTp_00348: if frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD
         * frames) are used for a Tx N-SDU and if CanTpTxPaddingActivation is equal to CANTP_ON,
         * CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU or last CF Tx N-PDU
         * that belongs to that Tx N-SDU with the length of eight bytes(i.e. PduInfoPtr.SduLength =
         * 8). Unused bytes in N-PDU shall be updated with CANTP_PADDING_BYTE (see
         * ECUC_CanTp_00298). */
        if (p_n_sdu->tx.cfg->padding == CANTP_ON)
        {
            CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
        }

        p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
        p_pdu_info->MetaDataPtr = NULL_PTR;
        p_pdu_info->SduLength = ofs;
    }

    return tmp_return;
}

static BufReq_ReturnType CanTp_LDataReqRFC(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;
    PduInfoType *p_pdu_info = &p_n_sdu->rx.pdu_info;
    uint16_least ofs = 0x00u;

    p_n_sdu->pci = CANTP_N_PCI_TYPE_FC;

    //CanTp_FillAIField(p_n_sdu, &ofs);

    p_n_sdu->rx.buf.can[0x00u] = (0x03u << 0x04u) | (uint8)CANTP_FLOW_STATUS_TYPE_CTS;
    p_n_sdu->rx.buf.can[0x01u] = p_n_sdu->rx.cfg->bs;
    p_n_sdu->rx.buf.can[0x02u] = CanTp_EncodeSTMinValue(p_n_sdu->rx.shared.m_param.st_min);

    /* SWS_CanTp_00348: if frames with a payload <= 8 (either CAN 2.0 frames or small CAN FD
     * frames) are used for a Tx N-SDU and if CanTpTxPaddingActivation is equal to CANTP_ON,
     * CanTp shall transmit by means of CanIf_Transmit() call, SF Tx N-PDU or last CF Tx N-PDU
     * that belongs to that Tx N-SDU with the length of eight bytes(i.e. PduInfoPtr.SduLength =
     * 8). Unused bytes in N-PDU shall be updated with CANTP_PADDING_BYTE (see
     * ECUC_CanTp_00298). */
    if (p_n_sdu->rx.cfg->padding == CANTP_ON)
    {
        CanTp_FillPadding(&p_n_sdu->rx.buf.can[0x00u], &ofs);
    }

    p_pdu_info->SduDataPtr = &p_n_sdu->rx.buf.can[0];
    p_pdu_info->MetaDataPtr = NULL_PTR;
    p_pdu_info->SduLength = ofs;

    return BUFREQ_OK;
}

static CanTp_FrameStateType CanTp_LDataIndRSF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
    uint16 dl;
    CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
    CanTp_NSduType *p_n_sdu = pNSdu;

    CANTP_CRITICAL_SECTION(p_n_sdu->rx.shared.taskState = CANTP_PROCESSING;)

    p_n_sdu->rx.sn = 0x00u;

    CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BR);

    if (CanTp_DecodeDLValue(&dl, &pPduInfo->SduDataPtr[0x00u]) == E_OK)
    {
        p_n_sdu->rx.buf.size = dl;

        PduLengthType pdu_length;

        /* TODO: call from CanTp_MainFunction. */
        PduR_CanTpStartOfReception(p_n_sdu->rx.cfg->nSduId,
                                   &p_n_sdu->rx.pdu_info,
                                   p_n_sdu->rx.buf.size,
                                   &pdu_length);

        result = CANTP_FRAME_STATE_OK;
    }

    return result;
}

static CanTp_FrameStateType CanTp_LDataIndRFF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
    uint16 dl;
    CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
    CanTp_NSduType *p_n_sdu = pNSdu;

    if (CanTp_DecodeDLValue(&dl, &pPduInfo->SduDataPtr[0x00u]) == E_OK)
    {
        CANTP_CRITICAL_SECTION(p_n_sdu->rx.shared.taskState = CANTP_PROCESSING;)

        p_n_sdu->rx.buf.size = dl;
        p_n_sdu->rx.sn = 0x00u;
        p_n_sdu->rx.bs = p_n_sdu->rx.shared.m_param.bs;

        p_n_sdu->rx.shared.flag |= CANTP_FLAG_SEND_RX_DATA | CANTP_FLAG_FIRST_CF;
        CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BR);
        result = CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION;
    }

    return result;
}

static CanTp_FrameStateType CanTp_LDataIndRCF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
    CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_CR);

    if (p_n_sdu->rx.state == CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION)
    {
        if (p_n_sdu->rx.shared.taskState == CANTP_PROCESSING)
        {
            if ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u)
            {
                /* If awaited, process the CF N_PDU in the on-going reception and
                 * perform the required checks (e.g. SN in right order), otherwise
                 * ignore it. */
                uint8 sn;

                p_n_sdu->rx.sn ++;

                if (CanTp_DecodeSNValue(&sn, &pPduInfo->SduDataPtr[0x00u]) == E_OK)
                {
                    if (p_n_sdu->rx.sn == sn)
                    {
                        p_n_sdu->rx.bs --;

                        if ((p_n_sdu->rx.buf.size - p_n_sdu->rx.buf.done) != 0x00u)
                        {
                            if (p_n_sdu->rx.bs == 0x00u)
                            {
                                p_n_sdu->rx.bs = p_n_sdu->rx.shared.m_param.bs;

                                /* SWS_CanTp_00166: At the reception of a FF or last CF of a block,
                                 * the CanTp module shall start a time-out N_Br before calling
                                 * PduR_CanTpStartOfReception or PduR_CanTpCopyRxData. */
                                CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BR);
                                result = CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION;
                            }
                            else
                            {
                                CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_CR);
                                result = CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION;
                            }
                        }
                        else
                        {
                            result = CANTP_FRAME_STATE_OK;
                        }
                    }
                }
            }
        }
    }

    return result;
}

static CanTp_FrameStateType CanTp_LDataIndTFC(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BS);

    p_n_sdu->fs = (CanTp_FlowStatusType)pPduInfo->SduDataPtr[0x00u] & 0x0Fu;
    p_n_sdu->tx.bs = pPduInfo->SduDataPtr[0x01u];
    p_n_sdu->tx.target_st_min = CanTp_DecodeSTMinValue(pPduInfo->SduDataPtr[0x02u]);

    /* SWS_CanTp_00315: the CanTp module shall start a timeout observation for N_Bs time at
     * confirmation of the FF transmission, last CF of a block transmission and at each
     * indication of FC with FS=WT (i.e. time until reception of the next FC). */
    if (p_n_sdu->fs == CANTP_FLOW_STATUS_TYPE_WT)
    {
        CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BS);
    }

    /* ISO15765:
     * 00: The BS parameter value zero (0) shall be used to indicate to the sender that no more
     * FC frames shall be sent during the transmission of the segmented message. The sending
     * network layer entity shall send all remaining consecutive frames without any stop for
     * further FC frames from the receiving network layer entity.
     * 01-FF: This range of BS parameter values shall be used to indicate to the sender the
     * maximum number of consecutive frames that can be received without an intermediate FC
     * frame from the receiving network entity.*/
    if (p_n_sdu->tx.bs == 0x00u)
    {
        p_n_sdu->tx.shared.flag |= CANTP_FLAG_SKIP_BS;
    }

    return CANTP_TX_FRAME_STATE_WAIT_CF_TX_REQUEST;
}

static CanTp_FrameStateType CanTp_LDataConTSF(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_AS);

    return CANTP_FRAME_STATE_OK;
}

static CanTp_FrameStateType CanTp_LDataConTFF(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_AS);

    /* SWS_CanTp_00315: the CanTp module shall start a timeout observation for N_Bs time at
     * confirmation of the FF transmission, last CF of a block transmission and at each indication
     * of FC with FS=WT (i.e. time until reception of the next FC). */
    CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BS);

    return CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION;
}

static CanTp_FrameStateType CanTp_LDataConTCF(CanTp_NSduType *pNSdu)
{
    CanTp_FrameStateType result;
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_AS);

    /* ISO15765: the measurement of the STmin starts after completion of transmission of a
     * ConsecutiveFrame (CF) and ends at the request for the transmission of the next CF. */
    CanTp_StartFlowControlTimeout(p_n_sdu);

    if (p_n_sdu->tx.buf.size > p_n_sdu->tx.buf.done)
    {
        p_n_sdu->tx.bs--;

        if ((p_n_sdu->tx.bs != 0x00u) || ((p_n_sdu->tx.shared.flag & CANTP_FLAG_SKIP_BS) != 0x00u))
        {
            result = CANTP_TX_FRAME_STATE_WAIT_CF_TX_REQUEST;
        }
        else
        {
            /* SWS_CanTp_00315: the CanTp module shall start a timeout observation for N_Bs time at
             * confirmation of the FF transmission, last CF of a block transmission and at each
             * indication of FC with FS=WT (i.e. time until reception of the next FC). */
            CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BS);

            result = CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION;
        }
    }
    else
    {
        result = CANTP_FRAME_STATE_OK;
    }

    return result;
}

static CanTp_FrameStateType CanTp_LDataConRFC(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_AR);
    CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_CR);

    p_n_sdu->rx.shared.flag |= CANTP_FLAG_COPY_RX_DATA;

    return CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION;
}

void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo)
{
    CanTp_FrameStateType next_state;
    CanTp_NSduType *p_n_sdu;
    uint8 instance_id = CANTP_I_FULL_DUPLEX_RX_FF;

    CANTP_DET_ASSERT_ERROR(pPduInfo == NULL_PTR,
                           0x00u,
                           CANTP_RX_INDICATION_API_ID,
                           CANTP_E_PARAM_POINTER,
                           return)

    if ((CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == E_OK) &&
        (CanTp_DecodePCIValue(&p_n_sdu->pci, &pPduInfo->SduDataPtr[0x00u]) == E_OK))
    {
        next_state = CANTP_FRAME_STATE_INVALID;
        if ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u)
        {
            switch (p_n_sdu->pci)
            {
                case CANTP_N_PCI_TYPE_SF:
                case CANTP_N_PCI_TYPE_FF:
                {
                    if ((p_n_sdu->rx.shared.taskState == CANTP_PROCESSING) &&
                        (p_n_sdu->dir == CANTP_DIRECTION_RX_TX))
                    {
                        /* SWS_CanTp_00057: Terminate the current reception, report an indication,
                         * with parameter Result set to E_NOT_OK, to the upper layer, and process
                         * the SF/FF N-PDU as the start of a new reception */
                        PduR_CanTpRxIndication(p_n_sdu->rx.cfg->nSduId, E_NOT_OK);

                        if (p_n_sdu->pci == CANTP_N_PCI_TYPE_SF)
                        {
                            instance_id = CANTP_I_FULL_DUPLEX_RX_SF;
                        }

                        CANTP_DET_ASSERT_RUNTIME_ERROR(TRUE, instance_id, 0x00u, CANTP_E_UNEXP_PDU)
                    }
                }
                case CANTP_N_PCI_TYPE_CF:
                {
                    next_state = ISO15765.ind[ISO15765_DIR_RX][p_n_sdu->pci](p_n_sdu, pPduInfo);
                }
                default:
                {
                    break;
                }
            }

            if (next_state != CANTP_FRAME_STATE_INVALID)
            {
                p_n_sdu->rx.state = next_state;
            }
        }
        if ((p_n_sdu->dir & CANTP_DIRECTION_TX) != 0x00u)
        {
            next_state = CANTP_FRAME_STATE_INVALID;
            switch (p_n_sdu->tx.state)
            {
                case CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION:
                {
                    next_state = ISO15765.ind[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_FC](p_n_sdu,
                                                                                    pPduInfo);
                }
                default:
                {
                    break;
                }
            }

            if (next_state != CANTP_FRAME_STATE_INVALID)
            {
                p_n_sdu->tx.state = next_state;
            }
        }
    }
}

void CanTp_TxConfirmation(PduIdType txPduId, Std_ReturnType result)
{
    CanTp_FrameStateType next_state;
    CanTp_NSduType *p_n_sdu;

    if (CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == E_OK)
    {
        if (result == E_OK)
        {
            if ((p_n_sdu->dir & CANTP_DIRECTION_RX) != 0x00u)
            {
                next_state = CANTP_FRAME_STATE_INVALID;

                switch (p_n_sdu->rx.state)
                {
                    case CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION:
                    {
                        next_state = ISO15765.con[ISO15765_DIR_RX][CANTP_N_PCI_TYPE_FC](p_n_sdu);

                        break;
                    }
                    default:
                    {
                        break;
                    }
                }

                if (next_state != CANTP_FRAME_STATE_INVALID)
                {
                    p_n_sdu->rx.state = next_state;
                }
            }
            if ((p_n_sdu->dir & CANTP_DIRECTION_TX) != 0x00u)
            {
                next_state = CANTP_FRAME_STATE_INVALID;

                switch (p_n_sdu->tx.state)
                {
                    case CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION:
                    {
                        next_state = ISO15765.con[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_SF](p_n_sdu);

                        break;
                    }
                    case CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION:
                    {
                        next_state = ISO15765.con[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_FF](p_n_sdu);

                        break;
                    }
                    case CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
                    {
                        next_state = ISO15765.con[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_CF](p_n_sdu);

                        break;
                    }
                    default:
                    {
                        break;
                    }
                }

                if (next_state != CANTP_FRAME_STATE_INVALID)
                {
                    p_n_sdu->tx.state = next_state;
                }
            }
        }
        else
        {
            /* SWS_CanTp_00355: CanTp shall abort the corresponding session, when
             * CanTp_TxConfirmation() is called with the result E_NOT_OK. */
            CanTp_AbortTxSession(p_n_sdu, CANTP_I_NONE, FALSE);
        }
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
    CanTp_ChannelRtType *p_channel_rt;
    uint32_least channel_idx;

    for (channel_idx = 0x00u; channel_idx < CANTP_NUM_OF_CHANNEL; channel_idx++)
    {
        p_channel_rt = &CanTp_Rt[channel_idx];

        if (pduId < (sizeof(p_channel_rt->sdu) / sizeof(p_channel_rt->sdu[0x00u])))
        {
            p_n_sdu = &p_channel_rt->sdu[pduId];

            if ((p_n_sdu->rx.cfg != NULL_PTR) && (p_n_sdu->rx.cfg->nSduId == pduId))
            {
                *pNSdu = p_n_sdu;
                tmp_return = E_OK;

                break;
            }
            else if ((p_n_sdu->tx.cfg != NULL_PTR) && (p_n_sdu->tx.cfg->nSduId == pduId))
            {
                *pNSdu = p_n_sdu;
                tmp_return = E_OK;

                break;
            }
            else
            {
                /* MISRA C, do nothing. */
            }
        }
    }

    return tmp_return;
}

static CanTp_NPciType CanTp_EncodePCIValue(const CanTp_AddressingFormatType af, const uint16 ps)
{
    CanTp_NPciType n_pci;

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

static Std_ReturnType CanTp_DecodePCIValue(CanTp_NPciType *pPci, const uint8 *pData)
{
    Std_ReturnType tmp_return = E_NOT_OK;
    CanTp_NPciType pci;

    if ((pPci != NULL_PTR) && (pData != NULL_PTR))
    {
        pci = (CanTp_NPciType)(pData[0x00u] >> 0x04u) & 0x0Fu;

        if ((pci == CANTP_N_PCI_TYPE_SF) ||
            (pci == CANTP_N_PCI_TYPE_FF) ||
            (pci == CANTP_N_PCI_TYPE_CF) ||
            (pci == CANTP_N_PCI_TYPE_FC))
        {
            *pPci = pci;
            tmp_return = E_OK;
        }
    }

    return tmp_return;
}

static Std_ReturnType CanTp_DecodeSNValue(uint8 *pSn, const uint8 *pData)
{
    Std_ReturnType tmp_return = E_NOT_OK;
    uint8 sn;

    if ((pSn != NULL_PTR) && (pData != NULL_PTR))
    {
        sn = pData[0x00u] & 0x0Fu;

        *pSn = sn;
        tmp_return = E_OK;
    }

    return tmp_return;
}

static Std_ReturnType CanTp_DecodeDLValue(uint16 *pDl, const uint8 *pData)
{
    Std_ReturnType tmp_return = E_NOT_OK;
    CanTp_NPciType pci;
    uint16 dl;

    if ((pDl != NULL_PTR) && (pData != NULL_PTR))
    {
        if (CanTp_DecodePCIValue(&pci, pData) == E_OK)
        {
            if ((pci == CANTP_N_PCI_TYPE_SF) ||
                (pci == CANTP_N_PCI_TYPE_FF))
            {
                dl = pData[0x00u] & 0x0Fu;

                if (pci == CANTP_N_PCI_TYPE_FF)
                {
                    dl = (uint16)(dl << 0x08u) | pData[0x01u];
                }

                /* SWS_CanTp_00350: The received data link layer data length (RX_DL) shall be
                 * derived from the first received payload length of the CAN frame/PDU (CAN_DL) as
                 * follows:
                 * - For CAN_DL values less than or equal to eight bytes the RX_DL value shall be
                 *   eight.
                 * - For CAN_DL values greater than eight bytes the RX_DL value equals the CAN_DL
                 *   value.*/
                if (dl < 0x08u)
                {
                    dl = 0x08u;
                }

                *pDl = dl;
                tmp_return = E_OK;
            }
        }
    }

    return tmp_return;
}

static uint32_least CanTp_DecodeSTMinValue(const uint8 data)
{
    uint32_least result;

    /* ISO15765: the units of STmin in the range 00 hex – 7F hex are absolute milliseconds (ms). */
    if ((0x00u <= data) && (data <= 0x7Fu))
    {
        result = CANTP_MS_TO_INTERNAL(data);
    }
    /* ISO15765: the units of STmin in the range F1 hex – F9 hex are even 100 microseconds (μs),
     * where parameter value F1 hex represents 100 μs and parameter value F9 hex represents 900 μs.
     */
    else if ((0xF1u <= data) && (data <= 0xF9u))
    {
        result = CANTP_US_TO_INTERNAL((data & 0x0Fu) * 100u);
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

static uint8 CanTp_EncodeSTMinValue(const uint16 value)
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

static void CanTp_AbortRxSession(CanTp_NSduType *pNSdu, const uint8 instanceId, const boolean confirm)
{
    pNSdu->rx.shared.taskState = CANTP_WAIT;

    if (confirm == TRUE)
    {
        PduR_CanTpRxIndication(pNSdu->rx.cfg->nSduId, E_NOT_OK);
    }

    if (instanceId != CANTP_I_NONE)
    {
        /* SWS_CanTp_00229 if the task was aborted due to As, Bs, Cs, Ar, Br, Cr timeout, the CanTp
         * module shall raise the DET error CANTP_E_RX_COM (in case of a reception operation) or
         * CANTP_E_TX_COM (in case of a transmission operation). If the task was aborted due to any
         * other protocol error, the CanTp module shall raise the runtime error code CANTP_E_COM to
         * the Default Error Tracer. */
        CANTP_DET_ASSERT_ERROR(TRUE, instanceId, 0x00u, CANTP_E_RX_COM)
    }
}

static void CanTp_AbortTxSession(CanTp_NSduType *pNSdu, const uint8 instanceId, boolean confirm)
{
    pNSdu->tx.taskState = CANTP_WAIT;

    if (confirm == TRUE)
    {
        PduR_CanTpTxConfirmation(pNSdu->tx.cfg->nSduId, E_NOT_OK);
    }

    if (instanceId != CANTP_I_NONE)
    {
        /* SWS_CanTp_00229 if the task was aborted due to As, Bs, Cs, Ar, Br, Cr timeout, the CanTp
         * module shall raise the DET error CANTP_E_RX_COM (in case of a reception operation) or
         * CANTP_E_TX_COM (in case of a transmission operation). If the task was aborted due to any
         * other protocol error, the CanTp module shall raise the runtime error code CANTP_E_COM to
         * the Default Error Tracer. */
        CANTP_DET_ASSERT_ERROR(TRUE, instanceId, 0x00u, CANTP_E_TX_COM)
    }
}

static void CanTp_TransmitRxCANData(CanTp_NSduType *pNSdu)
{
    CanTp_StartNetworkLayerTimeout(pNSdu, CANTP_I_N_AR);

    if (CanIf_Transmit(pNSdu->rx.cfg->rxNSduRef, &pNSdu->rx.pdu_info) != E_OK)
    {
        CanTp_AbortRxSession(pNSdu, CANTP_I_NONE, FALSE);
    }
}

static void CanTp_TransmitTxCANData(CanTp_NSduType *pNSdu)
{
    CanTp_StartNetworkLayerTimeout(pNSdu, CANTP_I_N_AS);

    if (CanIf_Transmit(pNSdu->tx.cfg->txNSduRef, &pNSdu->tx.pdu_info) != E_OK)
    {
        CanTp_AbortTxSession(pNSdu, CANTP_I_NONE, FALSE);
    }
}

static void CanTp_PerformStepRx(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_AR) == TRUE)
    {
        CanTp_AbortRxSession(pNSdu, CANTP_I_N_AR, TRUE);
    }
    else if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_CR) == TRUE)
    {
        CanTp_AbortRxSession(pNSdu, CANTP_I_N_CR, TRUE);
    }
    else
    {
        switch (p_n_sdu->rx.state)
        {
            case CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION:
            {
                /* SWS_CanTp_00166: At the reception of a FF or last CF of a block, the CanTp module
                 * shall start a time-out N_Br before calling PduR_CanTpStartOfReception or
                 * PduR_CanTpCopyRxData. */
                if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_BR) == TRUE)
                {
                    CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_BR);

                    CanTp_FillRxPayload(pNSdu);

                    if ((p_n_sdu->rx.shared.flag & CANTP_FLAG_SEND_RX_DATA) != 0x00u)
                    {
                        (void)ISO15765.req[ISO15765_DIR_RX][CANTP_N_PCI_TYPE_FC](p_n_sdu);

                        p_n_sdu->rx.shared.flag &= ~(CANTP_FLAG_SEND_RX_DATA);

                        CanTp_TransmitRxCANData(p_n_sdu);
                    }
                }
                else
                {
                    /* SWS_CanTp_00222: wWhile the timer N_Br is active, the CanTp module shall call
                     * the service PduR_CanTpCopyRxData() with a data length 0 (zero) and NULL_PTR
                     * as data buffer during each processing of the MainFunction. */
                    pNSdu->rx.pdu_info.SduLength = 0x00u;
                    pNSdu->rx.pdu_info.SduDataPtr = NULL_PTR;
                    PduR_CanTpCopyRxData(pNSdu->rx.cfg->nSduId,
                                         &pNSdu->rx.pdu_info,
                                         &pNSdu->rx.buf.rmng);
                }

                break;
            }
            case CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION:
            {
                if ((p_n_sdu->rx.shared.flag & CANTP_FLAG_COPY_RX_DATA) != 0x00u)
                {
                    p_n_sdu->rx.shared.flag &= ~(CANTP_FLAG_COPY_RX_DATA);

                    CanTp_FillRxPayload(pNSdu);
                }

                break;
            }
            case CANTP_FRAME_STATE_OK:
            {
                p_n_sdu->rx.shared.taskState = CANTP_WAIT;

                break;
            }
            default:
            {
                break;
            }
        }
    }
}

static void CanTp_PerformStepTx(CanTp_NSduType *pNSdu)
{
    CanTp_NSduType *p_n_sdu = pNSdu;

    if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_AS) == TRUE)
    {
        CanTp_AbortTxSession(pNSdu, CANTP_I_N_AS, TRUE);
    }
    else if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_BS) == TRUE)
    {
        /* SWS_CanTp_00316: in case of N_Bs timeout occurrence the CanTp module shall abort
         * transmission of this message and notify the upper layer by calling the callback function
         * PduR_CanTpTxConfirmation() with the result E_NOT_OK. */
        CanTp_AbortTxSession(pNSdu, CANTP_I_N_BS, TRUE);
    }
    else if (CanTp_NetworkLayerTimedOut(p_n_sdu, CANTP_I_N_CS) == TRUE)
    {
        /* SWS_CanTp_00280: if data is not available within N_Cs timeout the CanTp module shall
         * notify the upper layer of this failure by calling the callback function
         * PduR_CanTpTxConfirmation with the result E_NOT_OK. */
        CanTp_AbortTxSession(p_n_sdu, CANTP_I_N_CS, TRUE);
    }
    else
    {
        switch (p_n_sdu->tx.state)
        {
            case CANTP_TX_FRAME_STATE_WAIT_SF_TX_REQUEST:
            {
                if (ISO15765.req[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_SF](p_n_sdu) == BUFREQ_OK)
                {
                    CanTp_TransmitTxCANData(p_n_sdu);

                    p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION;
                }

                break;
            }
            case CANTP_TX_FRAME_STATE_WAIT_FF_TX_REQUEST:
            {
                if (ISO15765.req[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_FF](p_n_sdu) == BUFREQ_OK)
                {
                    CanTp_TransmitTxCANData(p_n_sdu);

                    p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION;
                }

                break;
            }
            case CANTP_TX_FRAME_STATE_WAIT_CF_TX_REQUEST:
            {
                if ((CanTp_FlowControlExpired(p_n_sdu) == TRUE) ||
                    (CanTp_FlowControlActive(p_n_sdu) == FALSE))
                {
                    if (ISO15765.req[ISO15765_DIR_TX][CANTP_N_PCI_TYPE_CF](p_n_sdu) == BUFREQ_OK)
                    {
                        CanTp_TransmitTxCANData(p_n_sdu);

                        p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION;
                    }
                }

                break;
            }
            case CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
            {
                /* TODO: handle this somewhere else... */
                if (p_n_sdu->tx.buf.done < p_n_sdu->tx.buf.size)
                {
                    p_n_sdu->tx.shared.flag &= ~(CANTP_FLAG_LAST_CF);
                }
                else
                {
                    p_n_sdu->tx.shared.flag |= (CANTP_FLAG_LAST_CF);
                }

                break;
            }
            case CANTP_FRAME_STATE_OK:
            {
                /* SWS_CanTp_00090: when the transport transmission session is successfully completed,
                 * the CanTp module shall call a notification service of the upper layer,
                 * PduR_CanTpTxConfirmation(), with the result E_OK. */
                PduR_CanTpTxConfirmation(p_n_sdu->tx.cfg->nSduId, E_OK);

                p_n_sdu->tx.taskState = CANTP_WAIT;

                break;
            }
            case CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION:
            case CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION:
            case CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION:
            // case CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
            default:
            {
                break;
            }
        }
    }
}

//static void CanTp_FillAIField(const CanTp_AddressingFormatType af,
//                              const uint8 n_sa,
//                              const uint8 n_ta,
//                              const uint8 n_ae,
//                              uint8 *pBuffer,
//                              PduLengthType *pOfs)
//{
//    PduLengthType ofs = *pOfs;
//
//    /* TODO: fill PDU meta data. */
//
//    /* SWS_CanTp_00334: when CanTp_Transmit is called for an N-SDU with meta data, the CanTp module
//     * shall store the addressing information contained in the meta data of the N-SDU and use this
//     * information for transmission of SF, FF, and CF N-PDUs and for identification of FC N-PDUs. */
//    switch (af)
//    {
//        case CANTP_EXTENDED:
//        {
//            pBuffer[ofs++] = n_ta;
//
//            break;
//        }
//        case CANTP_MIXED:
//        case CANTP_MIXED29BIT:
//        {
//            pBuffer[ofs++] = n_ae;
//
//            break;
//        }
//        case CANTP_STANDARD:
//        case CANTP_NORMALFIXED:
//        default:
//        {
//            (void)n_sa;
//
//            break;
//        }
//    }
//
//    *pOfs = ofs;
//}

static BufReq_ReturnType CanTp_FillRxPayload(CanTp_NSduType *pNSdu)
{
    BufReq_ReturnType result;

    if ((pNSdu->rx.shared.flag & CANTP_FLAG_FIRST_CF) != 0x00u)
    {
        pNSdu->rx.shared.flag &= ~(CANTP_FLAG_FIRST_CF);

        result = PduR_CanTpStartOfReception(pNSdu->rx.cfg->nSduId,
                                            &pNSdu->rx.pdu_info,
                                            pNSdu->rx.buf.size,
                                            &pNSdu->rx.buf.rmng);
    }
    else
    {
        result = PduR_CanTpCopyRxData(pNSdu->rx.cfg->nSduId,
                                      &pNSdu->rx.pdu_info,
                                      &pNSdu->rx.buf.rmng);
    }

    return result;
}

static BufReq_ReturnType CanTp_FillTxPayload(CanTp_NSduType *pNSdu, PduLengthType *pOfs)
{
    BufReq_ReturnType result;
    PduInfoType tmp_pdu;
    PduLengthType ofs = *pOfs;
    CanTp_NSduType *p_n_sdu = pNSdu;
    tmp_pdu.SduDataPtr = &p_n_sdu->tx.buf.can[ofs];

    if ((p_n_sdu->tx.buf.size - p_n_sdu->tx.buf.done) <= CANTP_CAN_FRAME_SIZE - ofs)
    {
        tmp_pdu.SduLength = p_n_sdu->tx.buf.size - p_n_sdu->tx.buf.done;
    }
    else
    {
        tmp_pdu.SduLength = CANTP_CAN_FRAME_SIZE - ofs;
    }

    CanTp_StartNetworkLayerTimeout(p_n_sdu, CANTP_I_N_CS);

    /* SWS_CanTp_00272: the API PduR_CanTpCopyTxData() contains a parameter used for the recovery
     * mechanism – ‘retry’. Because ISO 15765-2 does not support such a mechanism, the CAN Transport
     * Layer does not implement any kind of recovery. Thus, the parameter is always set to NULL
     * pointer. */
    result = PduR_CanTpCopyTxData(pNSdu->tx.cfg->nSduId, &tmp_pdu, NULL_PTR, &pNSdu->tx.buf.rmng);

    switch (result)
    {
        case BUFREQ_OK:
        {
            CanTp_StopNetworkLayerTimeout(p_n_sdu, CANTP_I_N_CS);

            ofs += tmp_pdu.SduLength;
            p_n_sdu->tx.buf.done += tmp_pdu.SduLength;

            *pOfs = ofs;

            break;
        }
        case BUFREQ_E_NOT_OK:
        {
            /* SWS_CanTp_00087: if PduR_CanTpCopyTxData() returns BUFREQ_E_NOT_OK, the CanTp module
             * shall abort the transmit request and notify the upper layer of this failure by
             * calling the callback function PduR_CanTpTxConfirmation() with the result E_NOT_OK. */
            CanTp_AbortTxSession(p_n_sdu, CANTP_I_NONE, TRUE);

            break;
        }
        case BUFREQ_E_BUSY:
        case BUFREQ_E_OVFL:
        default:
        {
            break;
        }
    }

    return result;
}

static void CanTp_FillPadding(uint8 *pBuffer, PduLengthType *pOfs)
{
    uint8 *p_buffer = pBuffer;
    PduLengthType ofs = *pOfs;

    for (; ofs < CANTP_CAN_FRAME_SIZE; ofs++)
    {
        p_buffer[ofs] = CANTP_PADDING_BYTE;
    }

    *pOfs = ofs;
}

/** @} */

#ifdef __cplusplus

}

#endif /* ifdef __cplusplus */
