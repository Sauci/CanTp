typedef unsigned char uint8;
typedef signed char sint8;
typedef unsigned short uint16;
typedef signed short sint16;
typedef unsigned int uint32;
typedef signed int sint32;
typedef uint32 uint8_least;
typedef sint32 sint8_least;
typedef uint32 uint16_least;
typedef sint32 sint16_least;
typedef uint32 uint32_least;
typedef sint32 sint32_least;
typedef uint8_least boolean;
typedef float ieee_float;
typedef uint32 Std_ReturnType;
typedef struct 
{
  uint16 vendorID;
  uint16 moduleID;
  uint8 sw_major_version;
  uint8 sw_minor_version;
  uint8 sw_patch_version;
} Std_VersionInfoType;
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
typedef struct PduInfoType
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
PduIdType get_pdu_id(void);
const PduInfoType *get_p_pdu_info_type(void);
Std_ReturnType get_return_value(void);
void set_pdu_id(PduIdType pduId);
void set_p_pdu_info_type(PduInfoType *pPduInfo);
void set_return_value(Std_ReturnType returnValue);
extern Std_ReturnType CanIf_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo);
void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo);
void CanTp_TxConfirmation(PduIdType txPduId, Std_ReturnType result);
typedef enum 
{
  CANTP_MODE_FULL_DUPLEX,
  CANTP_MODE_HALF_DUPLEX
} CanTp_ChannelMode;
typedef enum 
{
  CANTP_EXTENDED,
  CANTP_MIXED,
  CANTP_MIXED29BIT,
  CANTP_NORMALFIXED,
  CANTP_STANDARD
} CanTp_AddressingFormatType;
typedef enum 
{
  CANTP_OFF,
  CANTP_ON
} CanTp_StateType;
typedef CanTp_StateType CanTp_RxPaddingActivationType;
typedef CanTp_StateType CanTp_TxPaddingActivationType;
typedef enum 
{
  CANTP_FUNCTIONAL,
  CANTP_PHYSICAL
} CanTp_ComTypeType;
typedef struct 
{
  uint8 nSa;
} CanTp_NSaType;
typedef struct 
{
  uint8 nTa;
} CanTp_NTaType;
typedef struct 
{
  uint8 nAe;
} CanTp_NAeType;
typedef struct 
{
  const uint32 rxFcNPduRef;
  const uint16 rxFcNPduId;
} CanTp_RxFcNPduType;
typedef struct 
{
  const uint32 fcNPduRef;
  const uint16 fcNPduId;
} CanTp_TxFcNPduType;
typedef struct 
{
  const uint16 nSduId;
  const CanTp_NSaType *pNSa;
  const CanTp_NTaType *pNTa;
  const CanTp_NAeType *pNAe;
  const uint8 bs;
  const uint32 nar;
  const uint32 nbr;
  const uint32 ncr;
  const uint16 wftMax;
  const uint16 sTMin;
  const CanTp_AddressingFormatType af;
  const CanTp_RxPaddingActivationType padding;
  const CanTp_ComTypeType taType;
  const PduIdType rxNSduRef;
} CanTp_RxNSduType;
typedef struct 
{
  const uint16 nSduId;
  const CanTp_NSaType *pNSa;
  const CanTp_NTaType *pNTa;
  const CanTp_NAeType *pNAe;
  const uint32 nas;
  const uint32 nbs;
  const uint32 ncs;
  const boolean tc;
  const CanTp_AddressingFormatType af;
  const CanTp_TxPaddingActivationType padding;
  const CanTp_ComTypeType taType;
  const uint32 txNSduRef;
} CanTp_TxNSduType;
typedef struct 
{
  const uint16 id;
  const uint32 rxNPduId;
} CanTp_RxNPduType;
typedef struct 
{
  const uint32 pduRef;
  const uint16 pduConfirmationPduId;
} CanTp_TxNPduType;
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
} CanTp_ChannelType;
typedef struct 
{
  const uint32 mainFunctionPeriod;
  const uint32 maxChannelCnt;
  const CanTp_ChannelType *pChannel;
  const uint8 paddingByte;
} CanTp_ConfigType;
extern CanTp_StateType CanTp_State;
void CanTp_Init(const CanTp_ConfigType *pConfig);
void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo);
void CanTp_Shutdown(void);
Std_ReturnType CanTp_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo);
Std_ReturnType CanTp_CancelTransmit(PduIdType txPduId);
Std_ReturnType CanTp_CancelReceive(PduIdType rxPduId);
Std_ReturnType CanTp_ChangeParameter(PduIdType pduId, TPParameterType parameter, uint16 value);
Std_ReturnType CanTp_ReadParameter(PduIdType pduId, TPParameterType parameter, uint16 *pValue);
void CanTp_MainFunction(void);
void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo);
void CanTp_TxConfirmation(PduIdType txPduId, Std_ReturnType result);
Std_ReturnType Det_ReportError(uint16 moduleId, uint8 instanceId, uint8 apiId, uint8 errorId);
Std_ReturnType Det_ReportRuntimeError(uint16 moduleId, uint8 instanceId, uint8 apiId, uint8 errorId);
Std_ReturnType Det_ReportTransientFault(uint16 moduleId, uint8 instanceId, uint8 apiId, uint8 faultId);
extern void PduR_CanTpRxIndication(PduIdType rxPduId, Std_ReturnType result);
extern void PduR_CanTpTxConfirmation(PduIdType txPduId, Std_ReturnType result);
extern BufReq_ReturnType PduR_CanTpCopyRxData(PduIdType rxPduId, const PduInfoType *pPduInfo, PduLengthType *pBuffer);
extern BufReq_ReturnType PduR_CanTpCopyTxData(PduIdType txPduId, const PduInfoType *pPduInfo, const RetryInfoType *pRetryInfo, PduLengthType *pAvailableData);
extern BufReq_ReturnType PduR_CanTpStartOfReception(PduIdType pduId, const PduInfoType *pPduInfo, PduLengthType tpSduLength, PduLengthType *pBufferSize);
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
  CANTP_FLOW_STATUS_TYPE_OVFLW = 0x02u
} CanTp_FlowStatusType;
typedef enum 
{
  CANTP_FRAME_STATE_INVALID = 0x00u,
  CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION,
  CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION,
  CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION,
  CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION,
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
  uint8 can[0x08u];
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
    struct 
    {
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
  CanTp_NSduType sdu[0x02u];
} CanTp_ChannelRtType;
typedef struct 
{
  BufReq_ReturnType (* const req[2][4])(CanTp_NSduType *pNSdu);
  CanTp_FrameStateType (* const ind[2][4])(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo);
  CanTp_FrameStateType (* const con[2][4])(CanTp_NSduType *pNSdu);
} CanTp_ISO15765Type;
static Std_ReturnType CanTp_GetNSduFromPduId(PduIdType pduId, CanTp_NSduType **pNSdu);
static uint32_least CanTp_DecodeSTMinValue(const uint8 data);
static Std_ReturnType CanTp_DecodePCIValue(CanTp_NPciType *pPci, const uint8 *pData);
static Std_ReturnType CanTp_DecodeSNValue(uint8 *pSn, const uint8 *pData);
static Std_ReturnType CanTp_DecodeDLValue(uint16 *pDl, const uint8 *pData);
static uint8 CanTp_EncodeSTMinValue(uint16 value);
static void CanTp_AbortTxSession(CanTp_NSduType *pNSdu, const uint8 instanceId, boolean confirm);
static CanTp_NPciType CanTp_EncodePCIValue(CanTp_AddressingFormatType af, uint16 ps);
static void CanTp_PerformStepRx(CanTp_NSduType *pNSdu);
static void CanTp_PerformStepTx(CanTp_NSduType *pNSdu);
static BufReq_ReturnType CanTp_FillRxPayload(CanTp_NSduType *pNSdu);
static BufReq_ReturnType CanTp_FillTxPayload(CanTp_NSduType *pNSdu, PduLengthType *pOfs);
static void CanTp_FillPadding(uint8 *pBuffer, PduLengthType *pOfs);
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
static const CanTp_ISO15765Type ISO15765 = {{{(void *) 0x00u, (void *) 0x00u, (void *) 0x00u, CanTp_LDataReqRFC}, {CanTp_LDataReqTSF, CanTp_LDataReqTFF, CanTp_LDataReqTCF, (void *) 0x00u}}, {{CanTp_LDataIndRSF, CanTp_LDataIndRFF, CanTp_LDataIndRCF, (void *) 0x00u}, {(void *) 0x00u, (void *) 0x00u, (void *) 0x00u, CanTp_LDataIndTFC}}, {{(void *) 0x00u, (void *) 0x00u, (void *) 0x00u, CanTp_LDataConRFC}, {CanTp_LDataConTSF, CanTp_LDataConTFF, CanTp_LDataConTCF, (void *) 0x00u}}};
static const CanTp_ConfigType *CanTp_ConfigPtr = (void *) 0x00u;
static CanTp_ChannelRtType CanTp_Rt[0x01u];
CanTp_StateType CanTp_State = CANTP_OFF;
void CanTp_Init(const CanTp_ConfigType *pConfig)
{
  if (pConfig == ((void *) 0x00u))
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x01u, 0x03u);
    return;
  }

  Std_ReturnType result = 0x00u;
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
  if (pConfig->maxChannelCnt == 0x01u)
  {
    uint8 *p_cleared_data = (uint8 *) (&CanTp_Rt[0x00u]);
    uint32_least idx;
    for (idx = 0x00u; idx < (sizeof(CanTp_Rt)); idx++)
    {
      p_cleared_data[idx] = 0x00u;
    }

    for (channel_idx = 0x00u; channel_idx < pConfig->maxChannelCnt; channel_idx++)
    {
      p_rt_channel = &CanTp_Rt[channel_idx];
      p_cfg_channel = &pConfig->pChannel[channel_idx];
      n_sdu_range = p_cfg_channel->nSdu.rxNSduCnt + p_cfg_channel->nSdu.txNSduCnt;
      if (n_sdu_range <= 0x02u)
      {
        for (rt_sdu_idx = 0x00u; rt_sdu_idx < 0x02u; rt_sdu_idx++)
        {
          for (cfg_sdu_idx = 0x00u; cfg_sdu_idx < p_cfg_channel->nSdu.rxNSduCnt; cfg_sdu_idx++)
          {
            if (p_cfg_channel->nSdu.rx != ((void *) 0x00u))
            {
              p_cfg_rx_sdu = &p_cfg_channel->nSdu.rx[cfg_sdu_idx];
              if (p_cfg_rx_sdu->nSduId < n_sdu_range)
              {
                if (p_cfg_rx_sdu->nSduId == rt_sdu_idx)
                {
                  p_rt_sdu = &p_rt_channel->sdu[p_cfg_rx_sdu->nSduId];
                  p_rt_sdu->dir |= 0x01u;
                  p_rt_sdu->rx.cfg = p_cfg_rx_sdu;
                  p_rt_sdu->rx.shared.taskState = CANTP_WAIT;
                  p_rt_sdu->rx.shared.m_param.st_min = p_cfg_rx_sdu->sTMin;
                  p_rt_sdu->rx.shared.m_param.bs = p_cfg_rx_sdu->bs;
                }

              }
              else
              {
                result = 0x01u;
                break;
              }

            }

          }

          for (cfg_sdu_idx = 0x00u; cfg_sdu_idx < p_cfg_channel->nSdu.txNSduCnt; cfg_sdu_idx++)
          {
            if (p_cfg_channel->nSdu.tx != ((void *) 0x00u))
            {
              p_cfg_tx_sdu = &p_cfg_channel->nSdu.tx[cfg_sdu_idx];
              if (p_cfg_tx_sdu->nSduId < n_sdu_range)
              {
                if (p_cfg_tx_sdu->nSduId == rt_sdu_idx)
                {
                  p_rt_sdu = &p_rt_channel->sdu[p_cfg_tx_sdu->nSduId];
                  p_rt_sdu->dir |= 0x02u;
                  p_rt_sdu->tx.cfg = p_cfg_tx_sdu;
                  p_rt_sdu->tx.taskState = CANTP_WAIT;
                }

              }
              else
              {
                result = 0x01u;
                break;
              }

            }

          }

        }

      }
      else
      {
        result = 0x01u;
        break;
      }

    }

  }
  else
  {
    result = 0x01u;
  }

  if (result != 0x00u)
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, 0x00u, 0x01u, 0x04u);
      ;
    }

  }
  else
  {
    CanTp_State = CANTP_ON;
  }

}

void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo)
{
  if (pVersionInfo == ((void *) 0x00u))
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x07u, 0x03u);
    return;
  }

  pVersionInfo->vendorID = 0x00u;
  pVersionInfo->moduleID = (uint16) 0x0Eu;
  pVersionInfo->sw_major_version = 0x00u;
  pVersionInfo->sw_minor_version = 0x01u;
  pVersionInfo->sw_patch_version = 0x00u;
}

void CanTp_Shutdown(void)
{
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x02u, 0x20u);
    return;
  }

  CanTp_State = CANTP_OFF;
}

Std_ReturnType CanTp_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo)
{
  CanTp_NSduType *p_n_sdu = (void *) 0x00u;
  Std_ReturnType tmp_return = 0x01u;
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x49u, 0x20u);
    return 0x01u;
  }

  if (pPduInfo == ((void *) 0x00u))
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x49u, 0x03u);
    return 0x01u;
  }

  if (CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == 0x00u)
  {
    if (((p_n_sdu->tx.taskState != CANTP_PROCESSING) && (pPduInfo->SduLength > 0x0000u)) && (pPduInfo->SduLength <= 0x0FFFu))
    {
      p_n_sdu->tx.buf.size = pPduInfo->SduLength;
      p_n_sdu->tx.buf.done = 0x00u;
      if (pPduInfo->MetaDataPtr != ((void *) 0x00u))
      {
        p_n_sdu->has_meta_data = 0x01u;
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
        p_n_sdu->has_meta_data = 0x00u;
      }

      switch (CanTp_EncodePCIValue(p_n_sdu->tx.cfg->af, p_n_sdu->tx.buf.size))
      {
        case CANTP_N_PCI_TYPE_SF:
        {
          if (ISO15765.req[0x01u][CANTP_N_PCI_TYPE_SF](p_n_sdu) == BUFREQ_OK)
          {
            p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION;
            tmp_return = 0x00u;
          }

          break;
        }

        case CANTP_N_PCI_TYPE_FF:
        {
          if (ISO15765.req[0x01u][CANTP_N_PCI_TYPE_FF](p_n_sdu) == BUFREQ_OK)
          {
            p_n_sdu->tx.state = CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION;
            tmp_return = 0x00u;
          }

          break;
        }

        default:
        {
          break;
        }

      }

      if (tmp_return == 0x00u)
      {
        p_n_sdu->tx.taskState = CANTP_PROCESSING;
        p_n_sdu->tx.shared.flag |= 0x01u << 0x08u;
      }

    }

  }

  return tmp_return;
}

Std_ReturnType CanTp_CancelTransmit(PduIdType txPduId)
{
  CanTp_NSduType *p_n_sdu;
  const uint8 api_id = 0x4Au;
  Std_ReturnType tmp_return = 0x01u;
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x20u);
    return tmp_return;
  }

  if ((CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == 0x00u) && ((p_n_sdu->dir & 0x02u) != 0x00u))
  {
    if (p_n_sdu->tx.taskState == CANTP_PROCESSING)
    {
      p_n_sdu->tx.taskState = CANTP_WAIT;
      PduR_CanTpTxConfirmation(p_n_sdu->tx.cfg->nSduId, 0x01u);
      tmp_return = 0x00u;
    }
    else
    {
      if (0x01u)
      {
        (void) Det_ReportRuntimeError(0x0Eu, 0x00u, api_id, 0xA0u);
        ;
      }

    }

  }
  else
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
      ;
    }

  }

  return tmp_return;
}

Std_ReturnType CanTp_CancelReceive(PduIdType rxPduId)
{
  CanTp_NSduType *p_n_sdu;
  CanTp_TaskStateType task_state;
  const uint8 api_id = 0x4Cu;
  Std_ReturnType tmp_return = 0x01u;
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x20u);
    return tmp_return;
  }

  if ((CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == 0x00u) && ((p_n_sdu->dir & 0x01u) != 0x00u))
  {
    task_state = p_n_sdu->rx.shared.taskState;
    if (task_state == CANTP_PROCESSING)
    {
      if ((p_n_sdu->pci != CANTP_N_PCI_TYPE_SF) && ((p_n_sdu->rx.shared.flag & (0x01u << 0x0Cu)) == 0x00u))
      {
        p_n_sdu->rx.shared.taskState = CANTP_WAIT;
        PduR_CanTpRxIndication(p_n_sdu->rx.cfg->nSduId, 0x01u);
        tmp_return = 0x00u;
      }

    }
    else
    {
      if (0x01u)
      {
        (void) Det_ReportRuntimeError(0x0Eu, 0x00u, api_id, 0xA0u);
        ;
      }

    }

  }
  else
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
      ;
    }

  }

  return tmp_return;
}

Std_ReturnType CanTp_ChangeParameter(PduIdType pduId, TPParameterType parameter, uint16 value)
{
  CanTp_NSduType *p_n_sdu;
  CanTp_TaskStateType task_state;
  const uint8 api_id = 0x4Bu;
  Std_ReturnType tmp_return = 0x01u;
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x20u);
    return tmp_return;
  }

  if (CanTp_GetNSduFromPduId(pduId, &p_n_sdu) == 0x00u)
  {
    task_state = p_n_sdu->rx.shared.taskState;
    if (task_state != CANTP_PROCESSING)
    {
      if (((parameter == ((uint16) TP_STMIN)) && (value <= 0xFFu)) && ((p_n_sdu->dir & 0x01u) != 0x00u))
      {
        p_n_sdu->rx.shared.m_param.st_min = (uint32) value;
        tmp_return = 0x00u;
      }
      else
        if (((parameter == ((uint16) TP_BS)) && (value <= 0xFFu)) && ((p_n_sdu->dir & 0x01u) != 0x00u))
      {
        p_n_sdu->rx.shared.m_param.bs = (uint8) value;
        tmp_return = 0x00u;
      }
      else
      {
        if (0x01u)
        {
          (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
          ;
        }

      }


    }

  }
  else
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
      ;
    }

  }

  return tmp_return;
}

Std_ReturnType CanTp_ReadParameter(PduIdType pduId, TPParameterType parameter, uint16 *pValue)
{
  CanTp_NSduType *p_n_sdu;
  uint16 value;
  const uint8 api_id = 0x0Bu;
  Std_ReturnType tmp_return = 0x01u;
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x20u);
    return tmp_return;
  }

  if (pValue == ((void *) 0x00u))
  {
    (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x03u);
    return tmp_return;
  }

  if (CanTp_GetNSduFromPduId(pduId, &p_n_sdu) == 0x00u)
  {
    if ((p_n_sdu->dir & 0x01u) != 0x00u)
    {
      if (parameter == ((uint16) TP_STMIN))
      {
        value = (uint16) p_n_sdu->rx.shared.m_param.st_min;
        *pValue = value;
        tmp_return = 0x00u;
      }
      else
        if (parameter == ((uint16) TP_BS))
      {
        value = (uint16) p_n_sdu->rx.shared.m_param.bs;
        *pValue = value;
        tmp_return = 0x00u;
      }
      else
      {
        if (0x01u)
        {
          (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
          ;
        }

      }


    }

  }
  else
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, 0x00u, api_id, 0x02u);
      ;
    }

  }

  return tmp_return;
}

void CanTp_MainFunction(void)
{
  if (CanTp_State == CANTP_OFF)
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x06u, 0x20u);
    ;
  }

  uint32 idx;
  CanTp_NSduType *p_n_sdu;
  CanTp_TaskStateType task_state_rx;
  CanTp_TaskStateType task_state_tx;
  if (CanTp_State == CANTP_ON)
  {
    for (idx = 0x00u; idx < 0x02u; idx++)
    {
      p_n_sdu = &CanTp_Rt->sdu[idx];
      task_state_rx = p_n_sdu->rx.shared.taskState;
      task_state_tx = p_n_sdu->tx.taskState;
      if (task_state_rx == CANTP_PROCESSING)
      {
        CanTp_PerformStepRx(p_n_sdu);
      }

      if (task_state_tx == CANTP_PROCESSING)
      {
        CanTp_PerformStepTx(p_n_sdu);
      }

      {
        p_n_sdu->n[0x00u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->n[0x01u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->n[0x02u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->n[0x03u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->n[0x04u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->n[0x05u] += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->rx.st_min += CanTp_ConfigPtr->mainFunctionPeriod;
        p_n_sdu->tx.st_min += CanTp_ConfigPtr->mainFunctionPeriod;
      }
    }

  }

}

static void CanTp_StartNetworkLayerTimeout(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
  if (instanceId < ((sizeof(pNSdu->n)) / (sizeof(pNSdu->n[0x00u]))))
  {
    if ((pNSdu->t_flag & (0x01u << instanceId)) == 0x00u)
    {
      pNSdu->t_flag |= 0x01u << instanceId;
      pNSdu->n[instanceId] = 0x00u;
    }

  }

}

static void CanTp_StopNetworkLayerTimeout(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
  if (instanceId < ((sizeof(pNSdu->n)) / (sizeof(pNSdu->n[0x00u]))))
  {
    pNSdu->t_flag &= ~(0x01u << instanceId);
  }

}

static boolean CanTp_NetworkLayerTimedOut(CanTp_NSduType *pNSdu, const uint8 instanceId)
{
  boolean result = 0x00u;
  switch (instanceId)
  {
    case 0x00u:
    {
      result = (boolean) ((pNSdu->n[0x00u] >= pNSdu->tx.cfg->nas) && ((pNSdu->t_flag & (0x01u << 0x00u)) != 0x00u));
      break;
    }

    case 0x01u:
    {
      result = (boolean) ((pNSdu->n[0x01u] >= pNSdu->tx.cfg->nbs) && ((pNSdu->t_flag & (0x01u << 0x01u)) != 0x00u));
      break;
    }

    case 0x02u:
    {
      result = (boolean) ((pNSdu->n[0x02u] >= pNSdu->tx.cfg->ncs) && ((pNSdu->t_flag & (0x01u << 0x02u)) != 0x00u));
      break;
    }

    case 0x03u:
    {
      result = (boolean) ((pNSdu->n[0x03u] >= pNSdu->rx.cfg->nar) && ((pNSdu->t_flag & (0x01u << 0x03u)) != 0x00u));
      break;
    }

    case 0x04u:
    {
      result = (boolean) ((pNSdu->n[0x04u] >= pNSdu->rx.cfg->nbr) && ((pNSdu->t_flag & (0x01u << 0x04u)) != 0x00u));
      break;
    }

    case 0x05u:
    {
      result = (boolean) ((pNSdu->n[0x05u] >= pNSdu->rx.cfg->ncr) && ((pNSdu->t_flag & (0x01u << 0x05u)) != 0x00u));
      break;
    }

    default:
    {
      break;
    }

  }

  return result;
}

static void CanTp_StartFlowControlTimeout(CanTp_NSduType *pNSdu, const uint8 direction)
{
  if (((direction & 0x01u) != 0x00u) && ((pNSdu->rx.shared.flag & (0x01u << 0x06u)) == 0x00u))
  {
    pNSdu->rx.shared.flag |= 0x01u << 0x06u;
    pNSdu->rx.st_min = 0x00u;
  }

  if (((direction & 0x02u) != 0x00u) && ((pNSdu->tx.shared.flag & (0x01u << 0x06u)) == 0x00u))
  {
    pNSdu->tx.shared.flag |= 0x01u << 0x06u;
    pNSdu->tx.st_min = 0x00u;
  }

}

static void CanTp_StopFlowControlTimeout(CanTp_NSduType *pNSdu, const uint8 direction)
{
  if ((direction & 0x01u) != 0x00u)
  {
    pNSdu->rx.shared.flag &= ~(0x01u << 0x06u);
  }

  if ((direction & 0x02u) != 0x00u)
  {
    pNSdu->tx.shared.flag &= ~(0x01u << 0x06u);
  }

}

static boolean CanTp_FlowControlTimedOut(CanTp_NSduType *pNSdu, const uint8 direction)
{
  boolean result = 0x00u;
  uint32 st_min;
  if ((direction & 0x01u) != 0x00u)
  {
    st_min = pNSdu->rx.shared.m_param.st_min;
    result = (boolean) ((pNSdu->rx.st_min >= st_min) && ((pNSdu->rx.shared.flag & (0x01u << 0x06u)) != 0x00u));
  }
  else
    if ((direction & 0x02u) != 0x00u)
  {
    result = (boolean) ((pNSdu->tx.st_min >= pNSdu->tx.target_st_min) && ((pNSdu->tx.shared.flag & (0x01u << 0x06u)) != 0x00u));
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
  p_n_sdu->tx.buf.can[ofs] = ((uint8) CANTP_N_PCI_TYPE_SF) << 0x04u;
  p_n_sdu->tx.buf.can[ofs] |= pNSdu->tx.buf.size;
  ofs = ofs + 0x01u;
  tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
  if (tmp_return == BUFREQ_OK)
  {
    if (p_n_sdu->tx.cfg->padding == CANTP_ON)
    {
      CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
    }

    p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
    p_pdu_info->MetaDataPtr = (void *) 0x00u;
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
  p_n_sdu->tx.buf.can[ofs] = ((uint8) CANTP_N_PCI_TYPE_FF) << 0x04u;
  p_n_sdu->tx.buf.can[ofs] |= (pNSdu->tx.buf.size & 0x0F00u) >> 0x08u;
  p_n_sdu->tx.buf.can[ofs + 0x01u] = pNSdu->tx.buf.size & 0xFFu;
  ofs = ofs + 0x02u;
  tmp_return = CanTp_FillTxPayload(p_n_sdu, &ofs);
  if (tmp_return == BUFREQ_OK)
  {
    if (p_n_sdu->tx.cfg->padding == CANTP_ON)
    {
      CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
    }

    p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
    p_pdu_info->MetaDataPtr = (void *) 0x00u;
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
    p_n_sdu->tx.sn++;
    p_n_sdu->tx.buf.can[0x00u] = ((uint8) CANTP_N_PCI_TYPE_CF) << 0x04u;
    p_n_sdu->tx.buf.can[0x00u] |= p_n_sdu->tx.sn & 0x0Fu;
    if (p_n_sdu->tx.cfg->padding == CANTP_ON)
    {
      CanTp_FillPadding(&p_n_sdu->tx.buf.can[0x00u], &ofs);
    }

    p_pdu_info->SduDataPtr = &p_n_sdu->tx.buf.can[0];
    p_pdu_info->MetaDataPtr = (void *) 0x00u;
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
  p_n_sdu->rx.buf.can[0x00u] = (0x03u << 0x04u) | ((uint8) CANTP_FLOW_STATUS_TYPE_CTS);
  p_n_sdu->rx.buf.can[0x01u] = p_n_sdu->rx.cfg->bs;
  p_n_sdu->rx.buf.can[0x02u] = CanTp_EncodeSTMinValue(p_n_sdu->rx.shared.m_param.st_min);
  if (p_n_sdu->rx.cfg->padding == CANTP_ON)
  {
    CanTp_FillPadding(&p_n_sdu->rx.buf.can[0x00u], &ofs);
  }

  p_pdu_info->SduDataPtr = &p_n_sdu->rx.buf.can[0];
  p_pdu_info->MetaDataPtr = (void *) 0x00u;
  p_pdu_info->SduLength = ofs;
  return BUFREQ_OK;
}

static CanTp_FrameStateType CanTp_LDataIndRSF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
  uint16 dl;
  CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
  CanTp_NSduType *p_n_sdu = pNSdu;
  p_n_sdu->rx.shared.taskState = CANTP_PROCESSING;
  p_n_sdu->rx.sn = 0x00u;
  CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x04u);
  if (CanTp_DecodeDLValue(&dl, &pPduInfo->SduDataPtr[0x00u]) == 0x00u)
  {
    p_n_sdu->rx.buf.size = dl;
    PduLengthType pdu_length;
    PduR_CanTpStartOfReception(p_n_sdu->rx.cfg->nSduId, &p_n_sdu->rx.pdu_info, p_n_sdu->rx.buf.size, &pdu_length);
    result = CANTP_FRAME_STATE_OK;
  }

  return result;
}

static CanTp_FrameStateType CanTp_LDataIndRFF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
  uint16 dl;
  CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
  CanTp_NSduType *p_n_sdu = pNSdu;
  if (CanTp_DecodeDLValue(&dl, &pPduInfo->SduDataPtr[0x00u]) == 0x00u)
  {
    p_n_sdu->rx.shared.taskState = CANTP_PROCESSING;
    p_n_sdu->rx.buf.size = dl;
    p_n_sdu->rx.sn = 0x00u;
    p_n_sdu->rx.bs = p_n_sdu->rx.shared.m_param.bs;
    p_n_sdu->rx.shared.flag |= (0x01u << 0x07u) | (0x01u << 0x0Bu);
    CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x04u);
    result = CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION;
  }

  return result;
}

static CanTp_FrameStateType CanTp_LDataIndRCF(CanTp_NSduType *pNSdu, const PduInfoType *pPduInfo)
{
  CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
  CanTp_NSduType *p_n_sdu = pNSdu;
  CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x05u);
  if (p_n_sdu->rx.state == CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION)
  {
    if (p_n_sdu->rx.shared.taskState == CANTP_PROCESSING)
    {
      if ((p_n_sdu->dir & 0x01u) != 0x00u)
      {
        uint8 sn;
        p_n_sdu->rx.sn++;
        if (CanTp_DecodeSNValue(&sn, &pPduInfo->SduDataPtr[0x00u]) == 0x00u)
        {
          if (p_n_sdu->rx.sn == sn)
          {
            p_n_sdu->rx.bs--;
            if ((p_n_sdu->rx.buf.size - p_n_sdu->rx.buf.done) != 0x00u)
            {
              if (p_n_sdu->rx.bs == 0x00u)
              {
                p_n_sdu->rx.bs = p_n_sdu->rx.shared.m_param.bs;
                CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x04u);
                result = CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION;
              }
              else
              {
                CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x05u);
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
  CanTp_FrameStateType result = CANTP_FRAME_STATE_INVALID;
  CanTp_NSduType *p_n_sdu = pNSdu;
  if (p_n_sdu->tx.state == CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION)
  {
    CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x01u);
    p_n_sdu->fs = ((CanTp_FlowStatusType) pPduInfo->SduDataPtr[0x00u]) & 0x0Fu;
    p_n_sdu->tx.bs = pPduInfo->SduDataPtr[0x01u];
    p_n_sdu->tx.target_st_min = CanTp_DecodeSTMinValue(pPduInfo->SduDataPtr[0x02u]);
    if (p_n_sdu->fs == CANTP_FLOW_STATUS_TYPE_WT)
    {
      CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x01u);
    }

    if (p_n_sdu->tx.bs == 0x00u)
    {
      p_n_sdu->tx.shared.flag |= (0x01u << 0x0Au) | (0x01u << 0x0Du);
    }
    else
    {
      p_n_sdu->tx.shared.flag |= 0x01u << 0x0Au;
    }

    result = CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION;
  }

  return result;
}

static CanTp_FrameStateType CanTp_LDataConTSF(CanTp_NSduType *pNSdu)
{
  CanTp_NSduType *p_n_sdu = pNSdu;
  CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x00u);
  return CANTP_FRAME_STATE_OK;
}

static CanTp_FrameStateType CanTp_LDataConTFF(CanTp_NSduType *pNSdu)
{
  CanTp_NSduType *p_n_sdu = pNSdu;
  CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x00u);
  CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x01u);
  return CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION;
}

static CanTp_FrameStateType CanTp_LDataConTCF(CanTp_NSduType *pNSdu)
{
  CanTp_FrameStateType result;
  CanTp_NSduType *p_n_sdu = pNSdu;
  CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x00u);
  CanTp_StartFlowControlTimeout(p_n_sdu, 0x02u);
  if (p_n_sdu->tx.buf.size > p_n_sdu->tx.buf.done)
  {
    p_n_sdu->tx.bs--;
    if ((p_n_sdu->tx.bs != 0x00u) || ((p_n_sdu->tx.shared.flag & (0x01u << 0x0Du)) != 0x00u))
    {
      p_n_sdu->tx.shared.flag |= 0x01u << 0x0Au;
      result = CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION;
    }
    else
    {
      CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x01u);
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
  CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x03u);
  CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x05u);
  p_n_sdu->rx.shared.flag |= 0x01u << 0x09u;
  return CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION;
}

void CanTp_RxIndication(PduIdType rxPduId, const PduInfoType *pPduInfo)
{
  CanTp_FrameStateType next_state;
  CanTp_NSduType *p_n_sdu;
  uint8 instance_id = 0x86u;
  if (pPduInfo == ((void *) 0x00u))
  {
    (void) Det_ReportError(0x0Eu, 0x00u, 0x42u, 0x03u);
    return;
  }

  if ((CanTp_GetNSduFromPduId(rxPduId, &p_n_sdu) == 0x00u) && (CanTp_DecodePCIValue(&p_n_sdu->pci, &pPduInfo->SduDataPtr[0x00u]) == 0x00u))
  {
    next_state = CANTP_FRAME_STATE_INVALID;
    if ((p_n_sdu->dir & 0x01u) != 0x00u)
    {
      switch (p_n_sdu->pci)
      {
        case CANTP_N_PCI_TYPE_SF:

        case CANTP_N_PCI_TYPE_FF:
        {
          if ((p_n_sdu->rx.shared.taskState == CANTP_PROCESSING) && (p_n_sdu->dir == (0x01u | 0x02u)))
          {
            PduR_CanTpRxIndication(p_n_sdu->rx.cfg->nSduId, 0x01u);
            if (p_n_sdu->pci == CANTP_N_PCI_TYPE_SF)
            {
              instance_id = 0x85u;
            }

            if (0x01u)
            {
              (void) Det_ReportRuntimeError(0x0Eu, instance_id, 0x00u, 0x85u);
              ;
            }

          }

        }

        case CANTP_N_PCI_TYPE_CF:
        {
          next_state = ISO15765.ind[0x00u][p_n_sdu->pci](p_n_sdu, pPduInfo);
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

    if ((p_n_sdu->dir & 0x02u) != 0x00u)
    {
      next_state = CANTP_FRAME_STATE_INVALID;
      switch (p_n_sdu->pci)
      {
        case CANTP_N_PCI_TYPE_FC:
        {
          next_state = ISO15765.ind[0x01u][p_n_sdu->pci](p_n_sdu, pPduInfo);
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
  if (CanTp_GetNSduFromPduId(txPduId, &p_n_sdu) == 0x00u)
  {
    if (result == 0x00u)
    {
      if ((p_n_sdu->dir & 0x01u) != 0x00u)
      {
        next_state = CANTP_FRAME_STATE_INVALID;
        switch (p_n_sdu->rx.state)
        {
          case CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION:
          {
            next_state = ISO15765.con[0x00u][CANTP_N_PCI_TYPE_FC](p_n_sdu);
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

      if ((p_n_sdu->dir & 0x02u) != 0x00u)
      {
        next_state = CANTP_FRAME_STATE_INVALID;
        switch (p_n_sdu->tx.state)
        {
          case CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION:
          {
            next_state = ISO15765.con[0x01u][CANTP_N_PCI_TYPE_SF](p_n_sdu);
            break;
          }

          case CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION:
          {
            next_state = ISO15765.con[0x01u][CANTP_N_PCI_TYPE_FF](p_n_sdu);
            break;
          }

          case CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
          {
            next_state = ISO15765.con[0x01u][CANTP_N_PCI_TYPE_CF](p_n_sdu);
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
      CanTp_AbortTxSession(p_n_sdu, 0xFFu, 0x00u);
    }

  }

}

static Std_ReturnType CanTp_GetNSduFromPduId(PduIdType pduId, CanTp_NSduType **pNSdu)
{
  Std_ReturnType tmp_return = 0x01u;
  CanTp_NSduType *p_n_sdu;
  CanTp_ChannelRtType *p_channel_rt;
  uint32_least channel_idx;
  for (channel_idx = 0x00u; channel_idx < 0x01u; channel_idx++)
  {
    p_channel_rt = &CanTp_Rt[channel_idx];
    if (pduId < ((sizeof(p_channel_rt->sdu)) / (sizeof(p_channel_rt->sdu[0x00u]))))
    {
      p_n_sdu = &p_channel_rt->sdu[pduId];
      if ((p_n_sdu->rx.cfg != ((void *) 0x00u)) && (p_n_sdu->rx.cfg->nSduId == pduId))
      {
        *pNSdu = p_n_sdu;
        tmp_return = 0x00u;
        break;
      }
      else
        if ((p_n_sdu->tx.cfg != ((void *) 0x00u)) && (p_n_sdu->tx.cfg->nSduId == pduId))
      {
        *pNSdu = p_n_sdu;
        tmp_return = 0x00u;
        break;
      }
      else
      {
      }


    }

  }

  return tmp_return;
}

static CanTp_NPciType CanTp_EncodePCIValue(const CanTp_AddressingFormatType af, const uint16 ps)
{
  CanTp_NPciType n_pci;
  if ((((af == CANTP_STANDARD) || (af == CANTP_NORMALFIXED)) && (ps <= 0x07u)) || ((((af == CANTP_EXTENDED) || (af == CANTP_MIXED)) || (af == CANTP_MIXED29BIT)) && (ps <= 0x06u)))
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
  Std_ReturnType tmp_return = 0x01u;
  CanTp_NPciType pci;
  if ((pPci != ((void *) 0x00u)) && (pData != ((void *) 0x00u)))
  {
    pci = ((CanTp_NPciType) (pData[0x00u] >> 0x04u)) & 0x0Fu;
    if ((((pci == CANTP_N_PCI_TYPE_SF) || (pci == CANTP_N_PCI_TYPE_FF)) || (pci == CANTP_N_PCI_TYPE_CF)) || (pci == CANTP_N_PCI_TYPE_FC))
    {
      *pPci = pci;
      tmp_return = 0x00u;
    }

  }

  return tmp_return;
}

static Std_ReturnType CanTp_DecodeSNValue(uint8 *pSn, const uint8 *pData)
{
  Std_ReturnType tmp_return = 0x01u;
  uint8 sn;
  if ((pSn != ((void *) 0x00u)) && (pData != ((void *) 0x00u)))
  {
    sn = pData[0x00u] & 0x0Fu;
    *pSn = sn;
    tmp_return = 0x00u;
  }

  return tmp_return;
}

static Std_ReturnType CanTp_DecodeDLValue(uint16 *pDl, const uint8 *pData)
{
  Std_ReturnType tmp_return = 0x01u;
  CanTp_NPciType pci;
  uint16 dl;
  if ((pDl != ((void *) 0x00u)) && (pData != ((void *) 0x00u)))
  {
    if (CanTp_DecodePCIValue(&pci, pData) == 0x00u)
    {
      if ((pci == CANTP_N_PCI_TYPE_SF) || (pci == CANTP_N_PCI_TYPE_FF))
      {
        dl = pData[0x00u] & 0x0Fu;
        if (pci == CANTP_N_PCI_TYPE_FF)
        {
          dl = ((uint16) (dl << 0x08u)) | pData[0x01u];
        }

        if (dl < 0x08u)
        {
          dl = 0x08u;
        }

        *pDl = dl;
        tmp_return = 0x00u;
      }

    }

  }

  return tmp_return;
}

static uint32_least CanTp_DecodeSTMinValue(const uint8 data)
{
  uint32_least result;
  if ((0x00u <= data) && (data <= 0x7Fu))
  {
    result = data * 1000u;
  }
  else
    if ((0xF1u <= data) && (data <= 0xF9u))
  {
    result = (data & 0x0Fu) * 100u;
  }
  else
  {
    result = 0x7Fu * 1000u;
  }


  return result;
}

static uint8 CanTp_EncodeSTMinValue(const uint16 value)
{
  uint8 result;
  if ((0x00u <= (value / 1000u)) && ((value / 1000u) <= 0x7Fu))
  {
    result = value / 1000u;
  }
  else
    if (((((((((value == 100u) || (value == 200u)) || (value == 300u)) || (value == 400u)) || (value == 500u)) || (value == 600u)) || (value == 700u)) || (value == 800u)) || (value == 900u))
  {
    result = 0xF0u | (value / 100u);
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
  if (confirm == 0x01u)
  {
    PduR_CanTpRxIndication(pNSdu->rx.cfg->nSduId, 0x01u);
  }

  if (instanceId != 0xFFu)
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, instanceId, 0x00u, 0xC0u);
      ;
    }

  }

}

static void CanTp_AbortTxSession(CanTp_NSduType *pNSdu, const uint8 instanceId, boolean confirm)
{
  pNSdu->tx.taskState = CANTP_WAIT;
  if (confirm == 0x01u)
  {
    PduR_CanTpTxConfirmation(pNSdu->tx.cfg->nSduId, 0x01u);
  }

  if (instanceId != 0xFFu)
  {
    if (0x01u)
    {
      (void) Det_ReportError(0x0Eu, instanceId, 0x00u, 0xD0u);
      ;
    }

  }

}

static void CanTp_TransmitRxCANData(CanTp_NSduType *pNSdu)
{
  CanTp_StartNetworkLayerTimeout(pNSdu, 0x03u);
  if (CanIf_Transmit(pNSdu->rx.cfg->rxNSduRef, &pNSdu->rx.pdu_info) != 0x00u)
  {
    CanTp_AbortRxSession(pNSdu, 0xFFu, 0x00u);
  }

}

static void CanTp_TransmitTxCANData(CanTp_NSduType *pNSdu)
{
  CanTp_StartNetworkLayerTimeout(pNSdu, 0x00u);
  if (CanIf_Transmit(pNSdu->tx.cfg->txNSduRef, &pNSdu->tx.pdu_info) != 0x00u)
  {
    CanTp_AbortTxSession(pNSdu, 0xFFu, 0x00u);
  }

}

static void CanTp_PerformStepRx(CanTp_NSduType *pNSdu)
{
  CanTp_NSduType *p_n_sdu = pNSdu;
  if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x03u) == 0x01u)
  {
    CanTp_AbortRxSession(pNSdu, 0x03u, 0x01u);
  }
  else
    if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x05u) == 0x01u)
  {
    CanTp_AbortRxSession(pNSdu, 0x05u, 0x01u);
  }
  else
  {
    switch (p_n_sdu->rx.state)
    {
      case CANTP_RX_FRAME_STATE_WAIT_FC_TX_CONFIRMATION:
      {
        if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x04u) == 0x01u)
        {
          CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x04u);
          CanTp_FillRxPayload(pNSdu);
          if ((p_n_sdu->rx.shared.flag & (0x01u << 0x07u)) != 0x00u)
          {
            (void) ISO15765.req[0x00u][CANTP_N_PCI_TYPE_FC](p_n_sdu);
            p_n_sdu->rx.shared.flag &= ~(0x01u << 0x07u);
            CanTp_TransmitRxCANData(p_n_sdu);
          }

        }
        else
        {
          pNSdu->rx.pdu_info.SduLength = 0x00u;
          pNSdu->rx.pdu_info.SduDataPtr = (void *) 0x00u;
          PduR_CanTpCopyRxData(pNSdu->rx.cfg->nSduId, &pNSdu->rx.pdu_info, &pNSdu->rx.buf.rmng);
        }

        break;
      }

      case CANTP_RX_FRAME_STATE_WAIT_CF_RX_INDICATION:
      {
        if ((p_n_sdu->rx.shared.flag & (0x01u << 0x09u)) != 0x00u)
        {
          p_n_sdu->rx.shared.flag &= ~(0x01u << 0x09u);
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
  if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x00u) == 0x01u)
  {
    CanTp_AbortTxSession(pNSdu, 0x00u, 0x01u);
  }
  else
    if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x01u) == 0x01u)
  {
    CanTp_AbortTxSession(pNSdu, 0x01u, 0x01u);
  }
  else
    if (CanTp_NetworkLayerTimedOut(p_n_sdu, 0x02u) == 0x01u)
  {
    CanTp_AbortTxSession(p_n_sdu, 0x02u, 0x01u);
  }
  else
  {
    switch (p_n_sdu->tx.state)
    {
      case CANTP_TX_FRAME_STATE_WAIT_SF_TX_CONFIRMATION:

      case CANTP_TX_FRAME_STATE_WAIT_FF_TX_CONFIRMATION:
      {
        if ((p_n_sdu->tx.shared.flag & (0x01u << 0x08u)) != 0x00u)
        {
          p_n_sdu->tx.shared.flag &= ~(0x01u << 0x08u);
          CanTp_TransmitTxCANData(p_n_sdu);
        }

        break;
      }

      case CANTP_TX_FRAME_STATE_WAIT_FC_RX_INDICATION:
      {
        break;
      }

      case CANTP_TX_FRAME_STATE_WAIT_CF_TX_CONFIRMATION:
      {
        if ((p_n_sdu->tx.shared.flag & (0x01u << 0x0Au)) != 0x00u)
        {
          if (ISO15765.req[0x01u][CANTP_N_PCI_TYPE_CF](p_n_sdu) == BUFREQ_OK)
          {
            p_n_sdu->tx.shared.flag &= ~(0x01u << 0x0Au);
            if (p_n_sdu->tx.buf.done < p_n_sdu->tx.buf.size)
            {
              p_n_sdu->tx.shared.flag &= ~(0x01u << 0x0Cu);
            }
            else
            {
              p_n_sdu->tx.shared.flag |= 0x01u << 0x0Cu;
            }

          }

        }

        if (((p_n_sdu->tx.shared.flag & (0x01u << 0x0Au)) == 0x00u) && ((CanTp_FlowControlTimedOut(p_n_sdu, 0x02u) == 0x01u) || ((p_n_sdu->tx.shared.flag & (0x01u << 0x06u)) == 0x00u)))
        {
          CanTp_StopFlowControlTimeout(p_n_sdu, 0x02u);
          CanTp_TransmitTxCANData(p_n_sdu);
        }

        break;
      }

      case CANTP_FRAME_STATE_OK:
      {
        PduR_CanTpTxConfirmation(p_n_sdu->tx.cfg->nSduId, 0x00u);
        p_n_sdu->tx.taskState = CANTP_WAIT;
        break;
      }

      default:
      {
        break;
      }

    }

  }



}

static BufReq_ReturnType CanTp_FillRxPayload(CanTp_NSduType *pNSdu)
{
  BufReq_ReturnType result;
  if ((pNSdu->rx.shared.flag & (0x01u << 0x0Bu)) != 0x00u)
  {
    pNSdu->rx.shared.flag &= ~(0x01u << 0x0Bu);
    result = PduR_CanTpStartOfReception(pNSdu->rx.cfg->nSduId, &pNSdu->rx.pdu_info, pNSdu->rx.buf.size, &pNSdu->rx.buf.rmng);
  }
  else
  {
    result = PduR_CanTpCopyRxData(pNSdu->rx.cfg->nSduId, &pNSdu->rx.pdu_info, &pNSdu->rx.buf.rmng);
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
  if ((p_n_sdu->tx.buf.size - p_n_sdu->tx.buf.done) <= (0x08u - ofs))
  {
    tmp_pdu.SduLength = p_n_sdu->tx.buf.size - p_n_sdu->tx.buf.done;
  }
  else
  {
    tmp_pdu.SduLength = 0x08u - ofs;
  }

  CanTp_StartNetworkLayerTimeout(p_n_sdu, 0x02u);
  result = PduR_CanTpCopyTxData(pNSdu->tx.cfg->nSduId, &tmp_pdu, (void *) 0x00u, &pNSdu->tx.buf.rmng);
  switch (result)
  {
    case BUFREQ_OK:
    {
      CanTp_StopNetworkLayerTimeout(p_n_sdu, 0x02u);
      ofs += tmp_pdu.SduLength;
      p_n_sdu->tx.buf.done += tmp_pdu.SduLength;
      *pOfs = ofs;
      break;
    }

    case BUFREQ_E_NOT_OK:
    {
      CanTp_AbortTxSession(p_n_sdu, 0xFFu, 0x01u);
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
  for (; ofs < 0x08u; ofs++)
  {
    p_buffer[ofs] = 0x55u;
  }

  *pOfs = ofs;
}

