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
