/**
 * @file CanIf_Mock.hpp
 * @author Guillaume Sottas
 * @date 11/12/2018
 */

#ifndef CANIF_MOCK_H
#define CANIF_MOCK_H

#include <gmock/gmock.h>

#include "CanIf.h"

class CanIf_Interface
{
public:

    virtual Std_ReturnType CanIf_Transmit(PduIdType, const PduInfoType *) = 0;
};

class CanIf_Mock : public CanIf_Interface
{
private:

    static CanIf_Mock *singleton;

public:

    static CanIf_Mock &instance()
    {
        if (singleton == nullptr)
        {
            singleton = new CanIf_Mock();
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

    MOCK_METHOD2(CanIf_Transmit, Std_ReturnType(PduIdType, const PduInfoType *));
};

#endif /* #ifndef CANIF_MOCK_H */
