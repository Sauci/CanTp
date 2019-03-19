//
// Created by Guillaume Sottas on 2019-03-04.
//

#include "PduR_Mock.h"

PduR_Mock *PduR_Mock::singleton = nullptr;

void PduR_CanTpRxIndication(PduIdType rxPduId, Std_ReturnType result)
{
    return PduR_Mock::instance().PduR_CanTpRxIndication(rxPduId, result);
}

void PduR_CanTpTxConfirmation(PduIdType txPduId, Std_ReturnType result)
{
    return PduR_Mock::instance().PduR_CanTpTxConfirmation(txPduId, result);
}

BufReq_ReturnType PduR_CanTpCopyRxData(PduIdType rxPduId,
                                       const PduInfoType *pPduInfo,
                                       PduLengthType *pBuffer)
{
    return PduR_Mock::instance().PduR_CanTpCopyRxData(rxPduId, pPduInfo, pBuffer);
}

BufReq_ReturnType PduR_CanTpCopyTxData(PduIdType txPduId,
                                       const PduInfoType *pPduInfo,
                                       const RetryInfoType *pRetryInfo,
                                       PduLengthType *pAvailableData)
{
    return PduR_Mock::instance().PduR_CanTpCopyTxData(txPduId,
                                                      pPduInfo,
                                                      pRetryInfo,
                                                      pAvailableData);
}

BufReq_ReturnType PduR_CanTpStartOfReception(PduIdType pduId,
                                             const PduInfoType *pPduInfo,
                                             PduLengthType tpSduLength,
                                             PduLengthType *pBufferSize)
{
    return PduR_Mock::instance().PduR_CanTpStartOfReception(pduId,
                                                            pPduInfo,
                                                            tpSduLength,
                                                            pBufferSize);
}
