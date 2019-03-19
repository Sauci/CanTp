//
// Created by Guillaume Sottas on 2019-03-04.
//

#include "CanIf_Mock.h"

CanIf_Mock *CanIf_Mock::singleton = nullptr;

Std_ReturnType CanIf_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo)
{
    return CanIf_Mock::instance().CanIf_Transmit(txPduId, pPduInfo);
}
