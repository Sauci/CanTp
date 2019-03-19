/**
 * @file CanIf_Mock.hpp
 * @author Guillaume Sottas
 * @date 11/12/2018
 */

#ifndef PDUR_MOCK_H
#define PDUR_MOCK_H

#include <gmock/gmock.h>

#include "PduR.h"

class PduR_Interface
{
public:

    virtual void PduR_CanTpRxIndication(PduIdType rxPduId, Std_ReturnType result) = 0;

    virtual void PduR_CanTpTxConfirmation(PduIdType txPduId, Std_ReturnType result) = 0;

    virtual BufReq_ReturnType PduR_CanTpCopyRxData(PduIdType rxPduId,
                                                   const PduInfoType *pPduInfo,
                                                   PduLengthType *pBuffer) = 0;

    virtual BufReq_ReturnType PduR_CanTpCopyTxData(PduIdType txPduId,
                                                   const PduInfoType *pPduInfo,
                                                   const RetryInfoType *pRetryInfo,
                                                   PduLengthType *pAvailableData) = 0;

    virtual BufReq_ReturnType PduR_CanTpStartOfReception(PduIdType pduId,
                                                         const PduInfoType *pPduInfo,
                                                         PduLengthType tpSduLength,
                                                         PduLengthType *pBufferSize) = 0;
};

class PduR_Mock : public PduR_Interface
{
private:

    static PduR_Mock *singleton;

public:

    static PduR_Mock &instance()
    {
        if (singleton == nullptr)
        {
            singleton = new PduR_Mock();
        }

        return *singleton;
    }

    static void clear()
    {
        if (singleton != nullptr)
        {
            delete singleton;
            singleton = nullptr;
        }
    }

    MOCK_METHOD2(PduR_CanTpRxIndication, void(PduIdType, Std_ReturnType));

    MOCK_METHOD2(PduR_CanTpTxConfirmation, void(PduIdType, Std_ReturnType));

    MOCK_METHOD3(PduR_CanTpCopyRxData, BufReq_ReturnType(PduIdType,
                                                         const PduInfoType *,
                                                         PduLengthType *));

    MOCK_METHOD4(PduR_CanTpCopyTxData, BufReq_ReturnType(PduIdType,
                                                         const PduInfoType *,
                                                         const RetryInfoType *,
                                                         PduLengthType *));

    MOCK_METHOD4(PduR_CanTpStartOfReception, BufReq_ReturnType(PduIdType,
                                                               const PduInfoType *,
                                                               PduLengthType,
                                                               PduLengthType *));
};

ACTION_P3(PduR_SetCopiedTxDataPdu, SduDataPtr, MetaDataPtr, SduLength)
{
    auto p_pdu_info = (PduInfoType *)arg1;

    for (unsigned int idx = 0x00u; idx < SduLength; idx++)
    {
        p_pdu_info->SduDataPtr[idx] = SduDataPtr[idx];
    }

    p_pdu_info->SduDataPtr = SduDataPtr;
    p_pdu_info->MetaDataPtr = MetaDataPtr;
    p_pdu_info->SduLength = SduLength;
}

#endif /* #ifndef PDUR_MOCK_H */
