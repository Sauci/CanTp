//
// Created by Guillaume Sottas on 2019-07-16.
//

#include <CanTp_Types.h>
#include "CanTp.h"
#include "CanTp_PBcfg.h"

Std_ReturnType CanIf_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo)
{
    return E_OK;
}

Std_ReturnType Det_ReportError(uint16 moduleId,
                               uint8 instanceId,
                               uint8 apiId,
                               uint8 errorId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)errorId;

    return E_OK;
}

Std_ReturnType Det_ReportRuntimeError(uint16 moduleId,
                                      uint8 instanceId,
                                      uint8 apiId,
                                      uint8 errorId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)errorId;

    return E_OK;
}

Std_ReturnType Det_ReportTransientFault(uint16 moduleId,
                                        uint8 instanceId,
                                        uint8 apiId,
                                        uint8 faultId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)faultId;

    return E_OK;
}

void PduR_CanTpRxIndication(PduIdType rxPduId, Std_ReturnType result)
{
    (void)rxPduId;
    (void)result;
}

void PduR_CanTpTxConfirmation(PduIdType txPduId, Std_ReturnType result)
{
    (void)txPduId;
    (void)result;
}

BufReq_ReturnType PduR_CanTpCopyRxData(PduIdType rxPduId,
                                       const PduInfoType *pPduInfo,
                                       PduLengthType *pBuffer)
{
    (void)rxPduId;
    (void)pPduInfo;
    (void)pBuffer;

    return E_OK;
}

BufReq_ReturnType PduR_CanTpCopyTxData(PduIdType txPduId,
                                       const PduInfoType *pPduInfo,
                                       const RetryInfoType *pRetryInfo,
                                       PduLengthType *pAvailableData)
{
    (void)txPduId;
    (void)pPduInfo;
    (void)pRetryInfo;
    (void)pAvailableData;

    return E_OK;
}

BufReq_ReturnType PduR_CanTpStartOfReception(PduIdType pduId,
                                             const PduInfoType *pPduInfo,
                                             PduLengthType tpSduLength,
                                             PduLengthType *pBufferSize)
{
    (void)pduId;
    (void)pPduInfo;
    (void)tpSduLength;
    (void)pBufferSize;

    *pBufferSize = 8;

    return E_OK;
}

int main(int argc, char *argv[])
{
    int i;
    uint8 rx_data[] = {16, 8, 0xFFu, 0xFFu,
                       0xFFu, 0xFFu, 0xFFu, 0xFFu};
    uint8 tx_data[] = {0xFFu, 0xFFu, 0xFFu, 0xFFu,
                       0xFFu, 0xFFu, 0xFFu, 0xFFu,
                       0xFFu, 0xFFu, 0xFFu, 0xFFu};

    PduInfoType rx_pdu;
    PduInfoType tx_pdu;

    rx_pdu.SduDataPtr = &rx_data[0x00u];
    rx_pdu.MetaDataPtr = NULL_PTR;
    rx_pdu.SduLength = sizeof(rx_data);

    tx_pdu.SduDataPtr = &tx_data[0x00u];
    tx_pdu.MetaDataPtr = NULL_PTR;
    tx_pdu.SduLength = sizeof(tx_data);

    CanTp_Init(&CanTp_Config[0x00u]);
    CanTp_RxIndication(0, &rx_pdu);
    CanTp_MainFunction();

    return 0;
}
